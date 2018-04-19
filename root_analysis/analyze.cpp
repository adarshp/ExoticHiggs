#include <iostream>
#include <stdio.h>
#include <fstream>
#include <vector>
#include <string>

#include "TROOT.h"
#include "TH1.h"
#include "TSystem.h"
#include "TClonesArray.h"
#include "TTree.h"
#include "TH1F.h"
#include "TMath.h"
#include "TLorentzVector.h"
#include "TTreeReader.h"

#include "TMVA/Factory.h"
#include "TMVA/DataLoader.h"
#include "TMVA/Tools.h"
#include "TMVA/IMethod.h"
#include "TMVA/MethodBase.h"
#include "TMVA/Types.h"
#include "TMVA/Config.h"

#include "fastjet/PseudoJet.hh"
#include "classes/DelphesClasses.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/ExRootAnalysis/ExRootProgressBar.h"
#include "external/ExRootAnalysis/ExRootUtilities.h"
#include "cHtb_xsection.h"

using namespace fastjet;

template <class T>
Candidate make_candidate(T* delphes_particle) {
  Candidate candidate;
  candidate.Momentum = delphes_particle->P4(); 
  candidate.Charge = delphes_particle->Charge;
  return candidate;
}

void AnalyseEvents(ExRootTreeReader* treeReader, std::vector<int>& counters,
        std::map<std::string, double>& features, TTree* tree, double mC, double mH) {

  TClonesArray 
    *branchJet       = treeReader->UseBranch("Jet"),
    *branchElectron  = treeReader->UseBranch("Electron"),
    *branchMuon      = treeReader->UseBranch("Muon"),
    *branchMissingET = treeReader->UseBranch("MissingET");

  long totalEntries = treeReader->GetEntries();
  MissingET* met; Electron* electron; Jet* jet;

  ExRootProgressBar progressBar(totalEntries-1);

  for(long i = 0; i < totalEntries; i++) {
    progressBar.Update(i);
    treeReader->ReadEntry(i);

    met = (MissingET*) branchMissingET->At(0);

    // Declare containers
    std::vector<Jet*> jets, untagged_jets, b_jets, tau_jets, top_jets;
    std::vector<Candidate> leptons;

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

    int j = 0; counters[j]++; j++;

    // Two leptons
    if (leptons.size() != 2) continue; counters[j]++; j++;
    
    // One or two b-jets
    if (b_jets.size()!=1 and b_jets.size()!=2) continue; counters[j]++; j++;

    // One tau jet
    if (tau_jets.size() != 1) continue; counters[j]++; j++;

    // At least two untagged jets
    if (untagged_jets.size() < 2) continue; counters[j]++; j++;

    // SS leptons
    if (leptons[0].Charge!=leptons[1].Charge) continue; counters[j]++; j++;

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
    if (!(((1 - delta - w_tautau)*mH < H_candidate.m() < (1-delta+w_tautau)*mH)
        and ((mH/EH)*(charged_higgs.m() - mC - w_tautauW) 
            < H_candidate.m() - mH 
            < (mH/EH)*(charged_higgs.m() - mC + w_tautauW)))) continue;
    counters[j]++; j++;
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
std::vector<int> run_analysis(std::string process, std::vector<std::string> cutNames,
        std::map<std::string, double>& features, TTree* tree, double mC, double mH) {
    std::vector<int> counters;
    for (auto cut : cutNames) counters.push_back(0);
    TChain chain("Delphes");
    FillChain(&chain, (process+"_input_list.txt").c_str());
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    AnalyseEvents(treeReader, counters, features, tree, mC, mH);
    return counters;
}

// Calculate the cut-and-count significance
double calculate_significance(std::vector< std::vector<int>> counters, double signal_xsection) {
    double 
        luminosity = 3000.0,
        tttautau_xsection = 95.71,
        n_tttautau = counters[1][counters[1].size()-1];

    n_tttautau = (n_tttautau < 3)?(n_tttautau=3):(n_tttautau=n_tttautau);

    double
        xs_signal = ((double) counters[0][counters[0].size()-1]/counters[0][0])*signal_xsection,
        xs_tttautau = ((double) n_tttautau/counters[1][0])*tttautau_xsection,
        sig = (xs_signal/sqrt(xs_tttautau))*sqrt(luminosity);

    return sig;
}

// Calculate the TMVA significance
double calculate_tmva_significance(TTree* testTree, std::vector< std::vector<int> > counters, double signal_xsection){
    float bdtout;
    char type;

    testTree->SetBranchAddress("BDTG",&bdtout);
    testTree->SetBranchAddress("className",&type);

    // Get total signal and background entries
    int 
        nS_total = 0,
        nB_total = 0,
        nS_original = counters[0][0],
        nB_original = counters[1][0],
        nS_after_preselection = counters[0][7],
        nB_after_preselection = counters[1][7],
        nS_after_bdt_cut, nB_after_bdt_cut;

    double 
        cutoff=-10,
        luminosity = 3000,
        bg_xsection = 95.71,
        signal_xsection_after_preselection,
        bg_xsection_after_preselection,
        signal_xsection_after_bdt_cut,
        bg_xsection_after_bdt_cut,
        test_sig,
        sig_from_tmva = 0;


    // Loop over different values of the bdt response cutoff, pick the maximum
    // significance achieved.

    for (int j=0; j < 200; j++){

        nS_after_bdt_cut = 0;
        nB_after_bdt_cut = 0;

        for (int i = 0; i < testTree->GetEntries(); i++){
            testTree->GetEntry(i);
            if (type=='S') {
                nS_total++;
                if (bdtout > cutoff) 
                    nS_after_bdt_cut++;
            }
            else {
                nB_total++;
                if (bdtout > cutoff) 
                    nB_after_bdt_cut++;
            }
        }

        if (nB_after_bdt_cut < 3 ) 
        nB_after_bdt_cut = 3;

        signal_xsection_after_preselection = signal_xsection*nS_after_preselection/nS_original;
        bg_xsection_after_preselection = bg_xsection * nB_after_preselection/nB_original;
        
        signal_xsection_after_bdt_cut = signal_xsection_after_preselection*((double)nS_after_bdt_cut/nS_total);
        bg_xsection_after_bdt_cut = bg_xsection_after_preselection*((double)nB_after_bdt_cut/nB_total);
        
        test_sig = sqrt(luminosity)*signal_xsection_after_bdt_cut/sqrt(bg_xsection_after_bdt_cut);
        sig_from_tmva = (test_sig > sig_from_tmva)?test_sig:sig_from_tmva;
        cutoff+=0.1;
    }
    return sig_from_tmva;
  }

int main(int argc, char* argv[]) {

  // Get the signal benchmark point from command line arguments
  std::string signal_process = argv[1];
  double 
    mC        = atof(argv[2]),
    mH        = atof(argv[3]),
    tan_beta  = atof(argv[4]),
    BR_C_HW   = atof(argv[5]),
    BR_H_tata = atof(argv[6]);

  // Specify the names of the cuts

  std::vector<std::string> cutNames = {
    "Initial",
    "2 leptons",
    "1/2 b-jets",
    "1 tau jet",
    "2+ untagged jets",
    "SS Leptons",
    "OS tau jet",
    "2D mass cut"
  };

  // Declare the feature names, create a std::map with keys corresponding to them
  std::vector<std::string> featureNames = {
    "MET", 
    "pt_j1",
    "pt_l1",
    "pt_tau",
    "pt_b1",
    "mH",
    "mC"
  };

  std::map<std::string, double> features;


  // Set tan beta and the signal cross section
  double signal_xsection = MyCrossSection_100TeV_Htb(mC, tan_beta)*BR_C_HW*BR_H_tata;

  TTree* signal_tree = new TTree("Signal", "");
  TTree* background_tree = new TTree("Background", "");


  // Create a branch for each feature on the signal tree and each background tree
  for (int i=0; i < featureNames.size(); i++){
    features[featureNames[i]] = 0.;
    signal_tree->Branch(featureNames[i].c_str(), &features[featureNames[i]]);
    background_tree->Branch(featureNames[i].c_str(), &features[featureNames[i]]);
  }

  // Run analysis and store the counters for the cut flow
  /* std::vector<int> signal_counters = run_analysis(signal_process, cutNames, features, signal_tree, mC, mH); */
  /* std::vector<int> bg_counters = run_analysis("tttautau", cutNames, features, background_tree, mC, mH); */
  /* std::vector< std::vector<int> > counters; */
  /* counters.push_back(signal_counters); */
  /* counters.push_back(bg_counters); */

  std::vector< std::vector<int> > counters = {
    run_analysis(signal_process, cutNames, features, signal_tree, mC, mH),
    run_analysis("tttautau", cutNames, features, background_tree, mC, mH)
  };

  // Calculate cut-and-count significance
  double significance = calculate_significance(counters, signal_xsection);

  TMVA::Factory* factory = new TMVA::Factory("TMVAClassification", 
    "!V:Silent:Color:!DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Classification");

  TMVA::DataLoader* dataloader = new TMVA::DataLoader();

  // Add features
  for (auto featureName : featureNames) {
    dataloader->AddVariable(featureName);
  }

  // Add signal and background trees
  dataloader->AddSignalTree(signal_tree);
  dataloader->AddBackgroundTree(background_tree);

  // Do the train-test split
  dataloader->PrepareTrainingAndTestTree("", "",
    "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V");

  // Initialize Boosted Decision Tree Classifier
  factory->BookMethod(dataloader, TMVA::Types::kBDT, "BDTG",
          "!H"
          ":!V"
          ":NTrees=1000"
          ":BoostType=Grad"
          ":Shrinkage=0.30"
          ":UseBaggedBoost"
          ":BaggedSampleFraction=0.6"
          ":SeparationType=GiniIndex"
          ":nCuts=20"
          ":MaxDepth=3");

  // Perform training and testing
  factory->TrainAllMethods();
  factory->TestAllMethods();

  // Get testing results
  TMVA::IMethod* imethod = factory->GetMethod("default", "BDTG");
  TMVA::MethodBase* method = dynamic_cast<TMVA::MethodBase*> (imethod);
  TMVA::DataSet* dataset = method->Data();

  TTree* testTree = dataset->GetTree(TMVA::Types::kTesting);
  double sig_from_tmva = calculate_tmva_significance(testTree, counters, signal_xsection);

  std::cout << significance << " " << sig_from_tmva << std::endl; 

  return 0;

}
