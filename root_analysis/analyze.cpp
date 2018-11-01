#include <iostream>
#include <stdio.h>
#include <fstream>
#include <vector>
#include <string>

#include "TROOT.h"
#include "TSystem.h"
#include "TClonesArray.h"
#include "TMath.h"
#include "TLorentzVector.h"
#include "TTreeReader.h"

#include "fastjet/PseudoJet.hh"
#include "classes/DelphesClasses.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/ExRootAnalysis/ExRootProgressBar.h"
#include "external/ExRootAnalysis/ExRootUtilities.h"

#include "cHtb_xsection.h"
#include "analysis.h"

using namespace fastjet;
using namespace std;


void AnalyseEvents(
    string process,
    ExRootTreeReader* treeReader,
    TTree* tree
) {

  TClonesArray 
    *branchJet       = treeReader->UseBranch("Jet"),
    *branchElectron  = treeReader->UseBranch("Electron"),
    *branchMuon      = treeReader->UseBranch("Muon"),
    *branchMissingET = treeReader->UseBranch("MissingET");

  long totalEntries = treeReader->GetEntries();
  MissingET* met; Electron* electron; Jet* jet;

  ExRootProgressBar progressBar(totalEntries-1);

  for (long i = 0; i < totalEntries; i++) {
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

    int j = 0; 
    auto update_counter = [&] (string cut_name) {
        increment_counter(process, cut_name);
    };

    // Initial number of events
    update_counter("Initial");

    // Two leptons
    if (leptons.size() != 2) continue;
    update_counter("2 Leptons");
    
    // One or two b-jets
    if (b_jets.size()!=1 and b_jets.size()!=2) continue;
    update_counter("1/2 b-jets");

    // One tau jet
    if (tau_jets.size() != 1) continue;
    update_counter("1 tau jet");

    // At least two untagged jets
    if (untagged_jets.size() < 2) continue;
    update_counter("2+ untagged jets");

    // SS leptons
    if (leptons[0].Charge != leptons[1].Charge) continue; 
    update_counter("SS Leptons");

    // OS tau jet
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

      auto scale_momenta = [&] () {
        a = 4*(pow(l1_pz,2)-pow(l1_E,2));
        d = pow(mW,2) + 2*scale*(l1_px*met_px+l1_py*met_py);
        b = 4*l1_pz*d;
        c = d*d-4*pow(scale*MET*l1_pz,2);
        delta=b*b-4*a*c;
      };

      scale_momenta();

      while (delta < 0) { scale -= 0.01; scale_momenta(); }
    
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

    // Reconstruct Charged Higgs
    PseudoJet charged_higgs;
    if (w_ind==0)
      charged_higgs.reset_momentum((H_candidate+W_leptonic).four_mom());
    else
      charged_higgs.reset_momentum((H_candidate+W_hadronic).four_mom());


    // Mass cuts
    delta = 0.4;

    // Width of ditau mass window
    double 
        w_tautau = 0.25,
        w_tautauW = 0.2*mC;

    double EH = (pow(mC, 2) + pow(mH, 2) - pow(mW, 2))/(2*mH);

    features["MET"] = met->MET;
    features["pt_j1"] = untagged_jets[0]->PT;
    features["pt_l1"] = leptons[0].Momentum.Pt();
    features["pt_tau"] = tau_jets[0]->PT;
    features["pt_b1"] = b_jets[0]->PT;
    features["mC"] = charged_higgs.m();
    features["mH"] = H_candidate.m();

    tree->Fill();
  }
  progressBar.Finish();
}

// Run the analysis for a given signal or background process
void run_analysis(
    string process_name,
    TTree* tree,
    double mC,
    double mH
) {
    TChain chain("Delphes");
    FillChain(&chain, (process_name+"_input_list.txt").c_str());
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    AnalyseEvents(process_name, treeReader, tree);
}



int main(int argc, char* argv[]) {

  // Get the signal name
  signal_name = string(argv[1]);

  // Get the benchmark point parameters
   mC = atof(argv[2]);
   mH = atof(argv[3]);
  double 
    tan_beta  = atof(argv[4]),
    BR_C_HW   = atof(argv[5]), // Branching ratio of C -> HW
    BR_H_tata = atof(argv[6]), // Branching ratio of H -> tau tau
    BR_W_lv = 0.216, // Branching ratio W -> lv
    BR_W_jj = 0.676; // Branching ratio W -> jj


  // Set tan beta and the signal cross-section. 
  signal_xsection = MyCrossSection_100TeV_Htb(mC, tan_beta)
                   * 1000 // Convert from picobarn to femtobarn
                   * BR_C_HW * BR_H_tata * BR_W_lv * BR_W_jj; 


  // Initialize TTrees for the signal and background processes
  TTree* signal_tree = new TTree("Signal", "");
  for (auto bg : bgNames) 
      background_ttrees[bg] = new TTree(bg.c_str(), "");


  // Create a branch for each feature on the signal tree and each background tree
  for (int i=0; i < featureNames.size(); i++){
    features[featureNames[i]] = 0.;
    signal_tree->Branch(featureNames[i].c_str(), &features[featureNames[i]]);
    for (auto bg : bgNames) {
        background_ttrees[bg]->Branch(
            featureNames[i].c_str(),
            &features[featureNames[i]]
        );
    }
  }

  // Run analysis and store the counters for the cut flow

  run_analysis(signal_name, signal_tree, mC, mH);

  for (auto bg : bgNames)
      run_analysis(bg, background_ttrees[bg], mC, mH);

  // Construct a name for the classifier
  string classifierName = string("TMVAClassification_") 
                        + string(argv[7])
                        + string("_mC_")
                        + string(argv[2])
                        + string("_mH_")
                        + string(argv[3]) 
                        + string("_tb_") 
                        + string(argv[4]);

  TTree* testTree = perform_tmva_analysis(classifierName, signal_tree);


  double Z_d, Z_e;
  tie(Z_d, Z_e) = calculate_tmva_significance(testTree); 
  cout << Z_d << " " <<  Z_e << endl; 
  /* output_histogram_to_text_file("Signal", signal_bdt_histogram); */
  /* output_histogram_to_text_file("Background", background_bdt_histogram); */

  return 0;
}
