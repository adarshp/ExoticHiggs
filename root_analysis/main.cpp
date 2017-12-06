#include <iostream>
#include <stdio.h>
#include "TH1.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TClonesArray.h"
#include "TTree.h"
#include "TH1F.h"
#include "TMath.h"
#include "TTreeReader.h"
#include "fastjet/PseudoJet.hh"
#include "fastjet/ClusterSequence.hh"
#include "classes/DelphesClasses.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/ExRootAnalysis/ExRootProgressBar.h"
#include "external/ExRootAnalysis/ExRootResult.h"
#include "external/ExRootAnalysis/ExRootUtilities.h"
#include <fstream>

using namespace std;

template <class T>
Candidate make_candidate(T* delphes_particle) {
  Candidate candidate;
  candidate.Momentum = delphes_particle->P4(); 
  candidate.Charge = delphes_particle->Charge;
  return candidate;
}

void AnalyseEvents(ExRootTreeReader *treeReader, vector<int>& counters,
        map<string, TH1F*> plots, ofstream* f_features) {

  TClonesArray *branchJet       = treeReader->UseBranch("Jet"),
               *branchElectron  = treeReader->UseBranch("Electron"),
               *branchMuon      = treeReader->UseBranch("Muon"),
               *branchMissingET = treeReader->UseBranch("MissingET");

  long totalEntries = treeReader->GetEntries();
  cout << "** Chain contains " << totalEntries << " events" << endl;
  MissingET* met; Electron* electron; Jet* jet;

  ExRootProgressBar progressBar(totalEntries-1);


  // Loop over all events
  for(long i = 0; i < totalEntries; i++) {
    // Load selected branches with data from specified event
    progressBar.Update(i);
    treeReader->ReadEntry(i);

    // Analyse missing ET
    met = (MissingET*) branchMissingET->At(0);
    plots["MET"]->Fill(met->MET);

    vector<Jet*> jets, untagged_jets, b_jets, tau_jets;
    vector<Electron*> electrons;
    vector<Candidate> leptons;

    for (int i = 0; i < branchJet->GetEntriesFast(); i++) {
      jet = (Jet*) branchJet->At(i);
      if (jet->BTag & (1 << 0)) b_jets.push_back(jet);
      else if (jet->TauTag) tau_jets.push_back(jet);
      else untagged_jets.push_back(jet);
      jets.push_back(jet);
    }


    for(int i = 0; i < branchElectron->GetEntriesFast(); i++)
        leptons.push_back(make_candidate((Electron*)branchElectron->At(i)));

    for(int i = 0; i < branchMuon->GetEntriesFast(); i++)
        leptons.push_back(make_candidate((Muon*) branchMuon->At(i)));

    int j = 0; counters[j]++; j++;

    if (leptons.size() != 2) continue; counters[j]++; j++;
    if (b_jets.size()!=1 and b_jets.size()!=2) continue; counters[j]++; j++;
    plots["pt_b1"]->Fill(b_jets[0]->PT);

    if (tau_jets.size() != 1) continue; counters[j]++; j++;
    plots["pt_tau"]->Fill(tau_jets[0]->PT);


    if (untagged_jets.size() < 2) continue; counters[j]++; j++;

    if (leptons[0].Charge!=leptons[1].Charge) continue; counters[j]++; j++;
    plots["pt_l1"]->Fill(leptons[0].PT);
    if(leptons[0].Charge==tau_jets[0]->Charge) continue; counters[j]++; j++;

    // Neutrino reconstruction
    double delta = 10000.0, mW = 80.4;

    Candidate W_hadronic;         

    for (int i=0; i < untagged_jets.size(); i++) {
      for (int j=0; j < untagged_jets.size(); j++) {
        if (i!=j and i<j) {
          Candidate candidate;
          candidate.Momentum = untagged_jets[i]->P4() + untagged_jets[j]->P4(); 
          if (fabs(candidate.Momentum.M() - mW) < delta){
            delta = candidate.Momentum.M() - mW;
            W_hadronic = candidate;
          }
        }
      } 
    }

    plots["w_had"]->Fill(W_hadronic.Momentum.M());

    double
        a   = 0, b = 0, c = 0, d = 0, scale = 1.0,
        l1_pz  = leptons[0].Momentum.Pz(),
        l1_px  = leptons[0].Momentum.Px(),
        l1_py  = leptons[0].Momentum.Py(),
        l1_E   = leptons[0].Momentum.E(),
        MET    = met->MET,
        met_px = MET*cos(met->Phi),
        met_py = MET*sin(met->Phi);

      a = 4*(pow(l1_pz,2)-pow(l1_E,2));
      d = pow(mW,2) + 2*scale*(l1_px*met_px+l1_py*met_py);
      b = 4*l1_pz*d;
      c = d*d-4*pow(scale*MET*l1_pz,2);
      delta=b*b-4*a*c;
    
      while(delta<0) {
          scale -= 0.01;
          a      = 4*(pow(l1_pz,2)-pow(l1_E,2));
          d      = mW*mW+2*scale*(l1_px*met_px+l1_py*met_py);
          b      = 4*l1_pz*d;
          c      = d*d-4*pow(scale*MET*l1_pz,2);
          delta  = b*b-4*a*c;
      }
    
      double  sol1 = (-b+sqrt(delta))/(2*a),
              sol2 = (-b-sqrt(delta))/(2*a),
              pz   = abs(sol1) < abs(sol2) ? sol1 : sol2;
    
      fastjet::PseudoJet W_leptonic(met_px+l1_px,met_py+l1_py,pz+l1_pz,
          sqrt(met_px*met_px+met_py*met_py+pz*pz) + l1_E);

    plots["w_lep"]->Fill(W_leptonic.m());

    *f_features  

        << leptons[0].Momentum.Pt()  << '\t'
        << leptons[0].Momentum.Eta() << '\t'
        << leptons[0].Momentum.Phi() << '\t'
        << leptons[0].Momentum.E()   << '\t'

        << leptons[1].Momentum.Pt()  << '\t'
        << leptons[1].Momentum.Eta() << '\t'
        << leptons[1].Momentum.Phi() << '\t'
        << leptons[1].Momentum.E()   << '\t'

        << tau_jets[0]->P4().Pt()    << '\t'
        << tau_jets[0]->P4().Eta()   << '\t'
        << tau_jets[0]->P4().Phi()   << '\t'
        << tau_jets[0]->P4().E()     << '\t'

        << b_jets[0]->P4().Pt()      << '\t'
        << b_jets[0]->P4().Eta()     << '\t'
        << b_jets[0]->P4().Phi()     << '\t'
        << b_jets[0]->P4().E()       << '\t'

        << W_hadronic.Momentum.M()   << '\t'
        << W_leptonic.m()            << '\t'

        << met->MET                  << endl;
    }

    progressBar.Finish();
}

void run_analysis(string process, vector<int>& counters,
        map<string, TH1F*> plots, ofstream* f_features) {
    TChain chain("Delphes");
    FillChain(&chain, (process+"_input_list.txt").c_str());
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
  };

  string process = argv[1];
  map<string, TH1F*> plots;
  plots["MET"] = new TH1F("MET", "MET", 40, 0, 500);
  plots["pt_l1"] = new TH1F("pt_l1", "pt_l1", 40, 0, 500);
  plots["pt_b1"] = new TH1F("pt_b1", "pt_b1", 40, 0, 500);
  plots["pt_tau"] = new TH1F("pt_tau", "pt_tau", 40, 0, 500);
  plots["w_had"] = new TH1F("w_had", "w_had", 40, 0, 500);
  plots["w_lep"] = new TH1F("w_lep", "w_lep", 40, 0, 500);
  vector<int> counters; for (auto cut : cutNames) counters.push_back(0);

  vector<string> features = {
    "pt_l1",
    "eta_l1",
    "phi_l1",
    "e_l1",

    "pt_l2",
    "eta_l2",
    "phi_l2",
    "e_l2",

    "pt_tau",
    "eta_tau",
    "phi_tau",
    "e_tau",

    "pt_b1",
    "eta_b1",
    "phi_b1",
    "e_b1",

    "MET"
  };

  ofstream f_features(process+"/features.txt");
  for (int i=0; i < features.size(); i++){
    f_features << features[i];
    if (i!=features.size()-1)
        f_features << '\t';
    else 
        f_features << endl;
  }
  f_features.close();

  run_analysis(process, counters, plots, &f_features);

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
