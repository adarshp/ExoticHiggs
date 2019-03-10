#include <iostream>
#include <stdio.h>
#include "TH1.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TClonesArray.h"
#include "TTree.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TMath.h"
#include "TLorentzVector.h"
#include "TTreeReader.h"
#include "fastjet/PseudoJet.hh"
#include "classes/DelphesClasses.h"
#include "analysis.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/ExRootAnalysis/ExRootProgressBar.h"
#include "external/ExRootAnalysis/ExRootUtilities.h"
#include <fstream>

using namespace std;
using namespace fastjet;



void AnalyseEvents(string process, ExRootTreeReader* treeReader) {

  TClonesArray 
    *branchJet       = treeReader->UseBranch("Jet"),
    *branchElectron  = treeReader->UseBranch("Electron"),
    *branchMuon      = treeReader->UseBranch("Muon"),
    *branchMissingET = treeReader->UseBranch("MissingET");

  long totalEntries = treeReader->GetEntries();
  cout << "** Chain contains " << totalEntries << " events" << endl;

  MissingET* met;
  Electron* electron;
  Jet* jet;

  ExRootProgressBar progressBar(totalEntries-1);

  for(long i = 0; i < totalEntries; i++) {
    progressBar.Update(i);
    treeReader->ReadEntry(i);

    met = (MissingET*) branchMissingET->At(0);


    clear_particle_collections();

    // Collect jets
    for (int i = 0; i < branchJet->GetEntriesFast(); i++) {
      jet = (Jet*) branchJet->At(i);
      if (jet->BTag & (1 << 0)) b_jets.push_back(jet);
      else if (jet->TauTag) tau_jets.push_back(jet);
      else untagged_jets.push_back(jet);
      jets.push_back(jet);
    }

    // Collect leptons
    for(int i = 0; i < branchElectron->GetEntriesFast(); i++)
        leptons.push_back(make_candidate((Electron*)branchElectron->At(i)));

    for(int i = 0; i < branchMuon->GetEntriesFast(); i++)
        leptons.push_back(make_candidate((Muon*) branchMuon->At(i)));

    auto update_counter = [&] (string cut_name) {
        increment_counter(process, cut_name);
    };

    update_counter("Initial");

    if (leptons.size() != 2) continue;
    update_counter("2 Leptons");
    
    if (b_jets.size()!=1 and b_jets.size()!=2) continue;
    update_counter("1/2 b-jets");

    if (tau_jets.size() != 1) continue;
    update_counter("1 tau jet");

    if (untagged_jets.size() < 2) continue;
    update_counter("2+ untagged jets");

    if (leptons[0].Charge != leptons[1].Charge) continue; 
    update_counter("SS Leptons");

    if(leptons[0].Charge==tau_jets[0]->Charge) continue;
    update_counter("OS tau jet");

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

      while (delta<0) { scale -= 0.01; update(); }
    
      double  sol1 = (-b+sqrt(delta))/(2*a),
              sol2 = (-b-sqrt(delta))/(2*a),
              pz   = abs(sol1) < abs(sol2) ? sol1 : sol2;
    
      PseudoJet W_leptonic(
         met_px+l1_px,
         met_py+l1_py,
         pz+l1_pz,
         sqrt(met_px*met_px+met_py*met_py+pz*pz) + l1_E
      );

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

    // Reconstruct H candidate
    PseudoJet H_candidate(tau_jets[0]->P4()+leptons[1].Momentum);
    fill_1D_histo("m_tautau", 40, 0, 1000, H_candidate.m());

    // Reconstruct Charged Higgs
    PseudoJet charged_higgs;
    if (w_ind==0)
      charged_higgs.reset_momentum((H_candidate+W_leptonic).four_mom());
    else
      charged_higgs.reset_momentum((H_candidate+W_hadronic).four_mom());


    // Mass cuts

    delta = 0.4;

    // Width of ditau mass window
    double w_tautau = 0.25;
    /* double w_tautauW = 0.2*mC; */

    /* double EH = (pow(mC, 2) + pow(mH, 2) - pow(mW, 2))/(2*mH); */

    /* if (!(((1 - delta - w_tautau)*mH < H_candidate.m() < (1-delta+w_tautau)*mH) */
        /* and ((mH/EH)*(charged_higgs.m() - mC - w_tautauW) */ 
            /* < H_candidate.m() - mH */ 
            /* < (mH/EH)*(charged_higgs.m() - mC + w_tautauW)))) continue; */

    /* counters[j]++; j++; */
  }

  progressBar.Finish();

}

void run_analysis(string process) {
    TChain chain("Delphes");
    FillChain(&chain, (process+"_input_list.txt").c_str());
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    AnalyseEvents(process, treeReader);
}

int main(int argc, char* argv[]) {

  string process = string(argv[1]);

  run_analysis(process);


  return 0;
}
