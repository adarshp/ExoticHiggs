#include <iostream>
#include <stdio.h>
#include "TH1.h"
#include "TROOT.h"
#include "TCanvas.h"
#include "ROOT/TSeq.hxx"
#include "TSystem.h"
#include "TClonesArray.h"
#include "TPaveText.h"
#include "THStack.h"
#include "TString.h"
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
        map<string, ofstream*> PlotMap, ofstream* f_features) {

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
    *PlotMap["MET"] << met->MET << endl;

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

    Candidate W_hadronic;         
    double delta = 10000.0, mW = 80.4;

    for (int i=0; i < untagged_jets.size(); i++) {
      for (int j=0; j < untagged_jets.size(); j++) {
        if (i!=j and i<j) {
          Candidate candidate;
          candidate.Momentum = untagged_jets[i]->P4() + untagged_jets[j]->P4(); 
          if ((candidate.Momentum.M() - mW) < delta) 
            delta = candidate.Momentum.M() - mW;
            W_hadronic = candidate;
        }
      } 
    }

    *PlotMap["w_had"] << W_hadronic.Momentum.M() << endl;

    int j = 0; counters[j]++; j++;

    if (b_jets.size()!=1 and b_jets.size()!=2) continue; counters[j]++; j++;
    *PlotMap["pt_b1"] << b_jets[0]->PT << endl;

    if (tau_jets.size() != 1) continue; counters[j]++; j++;
    *PlotMap["pt_tau"] << tau_jets[0]->PT << endl;

    if (untagged_jets.size() < 2) continue; counters[j]++; j++;

    for(int i = 0; i < branchElectron->GetEntriesFast(); i++)
        leptons.push_back(make_candidate((Electron*)branchElectron->At(i)));

    for(int i = 0; i < branchMuon->GetEntriesFast(); i++)
        leptons.push_back(make_candidate((Muon*) branchMuon->At(i)));

    if (leptons.size() != 2) continue; counters[j]++; j++;
    if (leptons[0].Charge!=leptons[1].Charge) continue; counters[j]++; j++;
    *PlotMap["pt_l1"] << leptons[0].PT << endl;
    if(leptons[0].Charge!=tau_jets[0]->Charge) continue; counters[j]++; j++;
    *f_features  << leptons[0].PT << '\t' << tau_jets[0]->PT << '\t'
                 << b_jets[0]->PT << '\t' << met->MET        << '\t' << endl;
   
    // Neutrino reconstruction
    double a   = 0, b = 0, c = 0, d = 0, scale = 1.0, mw = 80.4,
        l1_pz  = leptons[0].Momentum.Pz(),
        l1_px  = leptons[0].Momentum.Px(),
        l1_py  = leptons[0].Momentum.Py(),
        l1_E   = leptons[0].Momentum.E(),
        MET    = met->MET,
        met_px = MET*cos(met->Phi),
        met_py = MET*sin(met->Phi);

      a = 4*(pow(l1_pz,2)-pow(l1_E,2));
      d = pow(mw,2) + 2*scale*(l1_px*met_px+l1_py*met_py);
      b = 4*l1_pz*d;
      c = d*d-4*pow(scale*MET*l1_pz,2);
      delta=b*b-4*a*c;
    
      while(delta<0) {
          scale -= 0.01;
          a      = 4*(pow(l1_pz,2)-pow(l1_E,2));
          d      = mw*mw+2*scale*(l1_px*met_px+l1_py*met_py);
          b      = 4*l1_pz*d;
          c      = d*d-4*pow(scale*MET*l1_pz,2);
          delta  = b*b-4*a*c;
      }
    
      double  sol1 = (-b+sqrt(delta))/(2*a),
              sol2 = (-b-sqrt(delta))/(2*a),
              pz   = abs(sol1) < abs(sol2) ? sol1 : sol2;
    
      fastjet::PseudoJet W_leptonic(met_px+l1_px,met_py+l1_py,pz+l1_pz,
          sqrt(met_px*met_px+met_py*met_py+pz*pz) + l1_E);
    
    }

    progressBar.Finish();
}

void run_analysis(string process, vector<int>& counters,
        map<string, ofstream*> PlotMap, ofstream* f_features) {
    TChain chain("Delphes");
    FillChain(&chain, (process+"_input_list.txt").c_str());
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    AnalyseEvents(treeReader, counters, PlotMap, f_features);
}

int main(int argc, char* argv[]) {
  vector<string> cutNames = {
    "Initial",
    "1/2 b-jets",
    "1 tau jet",
    "2+ untagged jets",
    "2 leptons",
    "OS Leptons",
    "OS tau jet"
  };

  string process = argv[1];
  map<string, ofstream*> PlotMap;
  vector<string> plots = {
    "pt_l1",
    "pt_b1",
    "pt_tau",
    "MET",
    "w_had"
  };
  for (auto p : plots) PlotMap[p] = new ofstream(process+"/histo_data/"
                                                +p+".txt");
  vector<int> counters; for (auto cut : cutNames) counters.push_back(0);
  ofstream f_features(process+"/features.txt");
  f_features << "MET" << '\t' << "m_Whad" << endl;
  run_analysis(process, counters, PlotMap, &f_features);
  for (auto p : plots) PlotMap[p]->close();
  f_features.close();

  ofstream f_counters(process+"/cuts.txt");
  f_counters << "Cut Name" << '\t' << "MC Events" << endl;

  for (int i=0; i < cutNames.size(); i++)
    f_counters << cutNames[i] << '\t' << counters[i] << endl;

  f_counters.close();
  return 0;
}
