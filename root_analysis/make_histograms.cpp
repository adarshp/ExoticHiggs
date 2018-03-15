#include <iostream>
#include <stdio.h>
#include "TH1.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TClonesArray.h"
#include "TTree.h"
#include "TH1F.h"
#include "TMath.h"
#include "TLorentzVector.h"
#include "TTreeReader.h"
#include "fastjet/PseudoJet.hh"
#include "classes/DelphesClasses.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/ExRootAnalysis/ExRootProgressBar.h"
#include "external/ExRootAnalysis/ExRootUtilities.h"
#include <fstream>

using namespace std;
using namespace fastjet;

template <class T>
Candidate make_candidate(T* delphes_particle) {
  Candidate candidate;
  candidate.Momentum = delphes_particle->P4(); 
  candidate.Charge = delphes_particle->Charge;
  return candidate;
}

void AnalyseEvents(ExRootTreeReader* treeReader, vector<int>& counters,
        map<string, TH1F*> plots, ofstream& f_features) {

  TClonesArray 
    *branchJet       = treeReader->UseBranch("Jet"),
    *branchFatJet    = treeReader->UseBranch("FatJet"),
    *branchElectron  = treeReader->UseBranch("Electron"),
    *branchMuon      = treeReader->UseBranch("Muon"),
    *branchMissingET = treeReader->UseBranch("MissingET");

  long totalEntries = treeReader->GetEntries();
  cout << "** Chain contains " << totalEntries << " events" << endl;
  MissingET* met; Electron* electron; Jet* jet;

  ExRootProgressBar progressBar(totalEntries-1);

  for(long i = 0; i < totalEntries; i++) {
    progressBar.Update(i);
    treeReader->ReadEntry(i);

    met = (MissingET*) branchMissingET->At(0);
    plots["MET"]->Fill(met->MET);

    // Declare containers
    vector<Jet*> jets, untagged_jets, b_jets, tau_jets, top_jets;
    vector<Electron*> electrons;
    vector<Candidate> leptons;

    // Collect jets
    for (int i = 0; i < branchJet->GetEntriesFast(); i++) {
      jet = (Jet*) branchJet->At(i);
      if (jet->BTag & (1 << 0)) b_jets.push_back(jet);
      else if (jet->TauTag) tau_jets.push_back(jet);
      else untagged_jets.push_back(jet);
      jets.push_back(jet);
    }

    // Collect top-tagged jets
    for (int i = 0; i < branchFatJet->GetEntriesFast(); i++) {
      jet = (Jet*) branchFatJet->At(i);
      if (jet->BTag & (1 << 0)) top_jets.push_back(jet);
    }

    plots["n_top"]->Fill(top_jets.size());

    // Collect leptons
    for(int i = 0; i < branchElectron->GetEntriesFast(); i++)
        leptons.push_back(make_candidate((Electron*)branchElectron->At(i)));

    for(int i = 0; i < branchMuon->GetEntriesFast(); i++)
        leptons.push_back(make_candidate((Muon*) branchMuon->At(i)));

    int j = 0; counters[j]++; j++;

    // Two leptons
    if (leptons.size() != 2) continue; counters[j]++; j++;
    
    // One or two b-jets
    if (b_jets.size()!=1 and b_jets.size()!=2) continue; counters[j]++; j++;
    plots["pt_b1"]->Fill(b_jets[0]->PT);

    // One tau jet
    if (tau_jets.size() != 1) continue; counters[j]++; j++;
    plots["pt_tau"]->Fill(tau_jets[0]->PT);

    // At least two untagged jets
    if (untagged_jets.size() < 2) continue; counters[j]++; j++;

    // SS leptons
    if (leptons[0].Charge!=leptons[1].Charge) continue; counters[j]++; j++;
    plots["pt_l1"]->Fill(leptons[0].PT);

    // OS tau jet
    if(leptons[0].Charge==tau_jets[0]->Charge) continue; counters[j]++; j++;

    // Neutrino reconstruction
    double delta = 10000.0, mW = 80.4;

    // Reconstruct hadronic W
    PseudoJet W_hadronic;         

    for (int i=0; i < untagged_jets.size(); i++) {
      for (int j=i+1; j < untagged_jets.size(); j++) {
        PseudoJet candidate(untagged_jets[i]->P4() + untagged_jets[j]->P4());
        if (fabs(candidate.m() - mW) < delta) {
           delta = candidate.m() - mW;
           W_hadronic = candidate;
        }
      } 
    }
    
    // Reconstruct leptonic W
    double
        a   = 0, b = 0, c = 0, d = 0, scale = 1.0,
        l1_pz  = leptons[0].Momentum.Pz(),
        l1_px  = leptons[0].Momentum.Px(),
        l1_py  = leptons[0].Momentum.Py(),
        l1_E   = leptons[0].Momentum.E(),
        MET    = met->MET,
        met_px = MET*cos(met->Phi),
        met_py = MET*sin(met->Phi);

      auto update = [&] () {
        a = 4*(pow(l1_pz,2)-pow(l1_E,2));
        d = pow(mW,2) + 2*scale*(l1_px*met_px+l1_py*met_py);
        b = 4*l1_pz*d;
        c = d*d-4*pow(scale*MET*l1_pz,2);
        delta=b*b-4*a*c;
      };

      update();

      while(delta<0) {
          scale -= 0.01;
          update();
      }
    
      double  sol1 = (-b+sqrt(delta))/(2*a),
              sol2 = (-b-sqrt(delta))/(2*a),
              pz   = abs(sol1) < abs(sol2) ? sol1 : sol2;
    
      PseudoJet W_leptonic(met_px+l1_px,met_py+l1_py,pz+l1_pz,
          sqrt(met_px*met_px+met_py*met_py+pz*pz) + l1_E);

    auto write_momentum_components = [&] (TLorentzVector momentum) {
        f_features << momentum.Pt()  << '\t'
                   << momentum.Eta() << '\t'
                   << momentum.Phi() << '\t'
                   << momentum.E()   << '\t';
    };

    write_momentum_components(leptons[0].Momentum);
    write_momentum_components(leptons[1].Momentum);
    write_momentum_components(tau_jets[0]->P4());
    write_momentum_components(b_jets[0]->P4());


    PseudoJet w_candidates[2]={W_hadronic, W_leptonic};
    double mt=174.0;
    delta=10000.0;
    int w_ind;

    // Reconstruct top candidate
    PseudoJet top_candidate;
    for (int i=0; i<2; i++){
      for (int j=0; j<b_jets.size(); j++){
        PseudoJet candidate(w_candidates[i].four_mom()+b_jets[j]->P4());
        if (fabs(candidate.m() - mt) < delta) {
          delta=candidate.m()-mt;
          top_candidate = candidate;
          w_ind=i;
        } 
      }
    }
    plots["m_top"]->Fill(top_candidate.m());

    // Reconstruct H candidate
    PseudoJet H_candidate(tau_jets[0]->P4()+leptons[1].Momentum);
    plots["m_H"]->Fill(H_candidate.m());

    // Reconstruct Charged Higgs
    PseudoJet charged_higgs;
    if (w_ind==0)
      charged_higgs.reset_momentum((H_candidate+W_leptonic).four_mom());
    else
      charged_higgs.reset_momentum((H_candidate+W_hadronic).four_mom());

    plots["m_cH"]->Fill(charged_higgs.m());

    f_features   << W_hadronic.m() << '\t'
                 << W_leptonic.m() << '\t'
                 << met->MET        << '\t'         
                 << H_candidate.m() << '\t'
                 << charged_higgs.m()
                 << endl;

    // Mass cuts

    delta = 0.4;

    // Mass of particles we are searching for
    double mH = 725.09;
    double mC = 1016.2776;

    // Width of ditau mass window
    double w_tautau = 0.25;
    double w_tautauW = 0.2*mC;

    double EH = (pow(mC, 2) + pow(mH, 2) - pow(mW, 2))/(2*mH);
    if (!(((1 - delta - w_tautau)*mH < H_candidate.m() < (1-delta+w_tautau)*mH)
        and ((mH/EH)*(charged_higgs.m() - mC - w_tautauW) 
            < H_candidate.m() - mH 
            < (mH/EH)*(charged_higgs.m() - mC + w_tautauW)))) continue;
    counters[j]++; j++;
  }
  progressBar.Finish();
}

void run_analysis(string process, vector<int>& counters,
        map<string, TH1F*> plots, ofstream& f_features) {
    TChain chain("Delphes");
    FillChain(&chain, ("input_lists/"+process+".txt").c_str());
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    AnalyseEvents(treeReader, counters, plots, f_features);
}

int main(int argc, char* argv[]) {

  vector<string> cutNames = {
    "Initial",
    "2 leptons",
    "1/2 b-jets",
    "1 tau jet",
    "2+ untagged jets",
    "SS Leptons",
    "OS tau jet",
    "2D mass cut"
  };

  vector<int> counters; for (auto cut : cutNames) counters.push_back(0);

  string process = argv[1];
  map<string, TH1F*> plots;

  plots["n_top"]  = new TH1F("n_top", "n_top", 4, 0, 4);
  plots["MET"]    = new TH1F("MET", "MET", 40, 0, 500);
  plots["pt_l1"]  = new TH1F("pt_l1", "pt_l1", 40, 0, 500);
  plots["pt_b1"]  = new TH1F("pt_b1", "pt_b1", 40, 0, 500);
  plots["pt_tau"] = new TH1F("pt_tau", "pt_tau", 40, 0, 500);
  plots["m_top"]  = new TH1F("m_top", "m_top", 40, 0, 300);
  plots["m_H"]    = new TH1F("m_H", "m_H", 40, 0, 3000);
  plots["m_cH"]   = new TH1F("m_cH", "m_cH", 40, 0, 3000);

  vector<string> features = {
    "pt_l1"  , "eta_l1"  , "phi_l1"  , "e_l1"  ,
    "pt_l2"  , "eta_l2"  , "phi_l2"  , "e_l2"  ,
    "pt_tau" , "eta_tau" , "phi_tau" , "e_tau" ,
    "pt_b1"  , "eta_b1"  , "phi_b1"  , "e_b1"  ,
    "MET", "mH", "mC"
  };

  ofstream f_features(process+"/features.txt");
  for (int i=0; i < features.size(); i++){
    f_features << features[i];
    if (i!=features.size()-1) f_features << '\t';
    else f_features << endl;
  }
  run_analysis(process, counters, plots, f_features);
  f_features.close();

  for (auto p : plots) {
      string plotname = p.first;
      ofstream h(process+"/histo_data/"+plotname+".txt");
      h << "Bin Low Edge" << '\t'  << "Bin Width" << '\t' << "Bin Entries" << endl;
      for (int i=1; i < plots[plotname]->GetNbinsX(); i++) {
        h  << plots[plotname]->GetBinLowEdge(i) << '\t'
           << plots[plotname]->GetBinWidth(i)   << '\t'
           << plots[plotname]->GetBinContent(i) << endl;
      }
      h.close();
  }

  ofstream f_counters(process+"/cuts.txt");
  f_counters << "Cut Name" << '\t' << "MC Events" << endl;
  for (int i=0; i < cutNames.size(); i++)
    f_counters << cutNames[i] << '\t' << counters[i] << endl;
  f_counters.close();

  return 0;
}
