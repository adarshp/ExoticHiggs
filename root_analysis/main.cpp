#include <stdio.h>
#include <iostream>
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

struct Counter{ int counter[7] = {0}; };

struct MyPlots {
  TH1 *fMissingET;
  TH1 *fElectronPT;
  TH1 *m_W_hadronic_candidate;
};

void BookHistograms(ExRootResult *result, MyPlots *plots) {
  TLegend *legend;
  TPaveText *comment;

  plots->fElectronPT = result->AddHist1D(
    "electron_pt", "electron P_{T}",
    "electron P_{T}, GeV/c", "number of electrons",
    50, 0.0, 100.0);

  plots->m_W_hadronic_candidate = result->AddHist1D(
    "m_W_hadronic_candidate", "m_W_hadronic_candidate",
    "m_W_hadronic, GeV/c", "invariant mass of hadronic W",
    40, 10.0, 200.0);

  plots->fMissingET = result->AddHist1D(
    "missing_et", "Missing E_{T}",
    "Missing E_{T}, GeV", "number of events",
    60, 0.0, 30.0);

  // show histogram statisics for MissingET
  plots->fMissingET->SetStats();
}

template <class T>
Candidate make_candidate(T* delphes_particle) {
    Candidate candidate;
    candidate.Momentum = delphes_particle->P4(); 
    candidate.Charge = delphes_particle->Charge;
    return candidate;
}

void AnalyseEvents(ExRootTreeReader *treeReader, MyPlots *plots, Counter* counter) {
    TClonesArray *branchJet  = treeReader->UseBranch("Jet");
    TClonesArray *branchElectron  = treeReader->UseBranch("Electron");
    TClonesArray *branchMuon  = treeReader->UseBranch("Muon");
    TClonesArray *branchMissingET = treeReader->UseBranch("MissingET");

    Long64_t totalEntries = treeReader->GetEntries();

    std::cout << "** Chain contains " << totalEntries << " events" << std::endl;

    MissingET* met;
    Electron* electron;
    Jet* jet;

    ExRootProgressBar progressBar(totalEntries-1);

    // Loop over all events
    for(long i = 0; i < totalEntries; i++) {
        // Load selected branches with data from specified event
        progressBar.Update(i);
        treeReader->ReadEntry(i);

        // Analyse missing ET
        met = (MissingET*) branchMissingET->At(0);
        plots->fMissingET->Fill(met->MET);

        std::vector<Jet*> jets;
        std::vector<Jet*> untagged_jets;
        std::vector<Jet*> b_jets;
        std::vector<Jet*> tau_jets;

        std::vector<Electron*> electrons;
        std::vector<Candidate> leptons;

        for(int i = 0; i < branchJet->GetEntriesFast(); i++) {
            jet = (Jet*) branchJet->At(i);
            if (jet->BTag & (1 << 0)) b_jets.push_back(jet);
            else if (jet->TauTag) tau_jets.push_back(jet);
            else untagged_jets.push_back(jet);
            jets.push_back(jet);
        }

        Candidate W_hadronic;         
        double delta = 10000.0;
        double mW = 80.4;
        for (int i=0; i < untagged_jets.size(); i++) {
            for (int j=0; j < untagged_jets.size(); j++) {
                if (i!=j and i<j) {
                    Candidate candidate;
                    candidate.Momentum = untagged_jets[i]->P4()
                                        +untagged_jets[j]->P4(); 
                    if ((candidate.Momentum.M() - mW) < delta) {
                        delta = candidate.Momentum.M() - mW;
                        W_hadronic = candidate;
                    }
                }
            } 
        }
        plots->m_W_hadronic_candidate->Fill(W_hadronic.Momentum.M());

        int j = 0; counter->counter[j]++; j++;

        if (b_jets.size() != 1 and b_jets.size() != 2) continue; 
        counter->counter[j]++; j++;

        if (tau_jets.size() != 1) continue; 
        counter->counter[j]++; j++;

        if (untagged_jets.size() < 2) continue; 
        counter->counter[j]++; j++;

        for(int i = 0; i < branchElectron->GetEntriesFast(); i++) {
            leptons.push_back(make_candidate((Electron*) branchElectron->At(i)));
        }

        for(int i = 0; i < branchMuon->GetEntriesFast(); i++) {
            leptons.push_back(make_candidate((Muon*) branchMuon->At(i)));
        }

        if (leptons.size() != 2) continue; 
        counter->counter[j]++; j++;

        if (leptons[0].Charge != leptons[1].Charge) continue;
        counter->counter[j]++; j++;

        if (leptons[0].Charge != tau_jets[0]->Charge) continue;
        counter->counter[j]++; j++;
        
        // Neutrino reconstruction
        double a=0, b=0, c=0, delta=0, scale=1.0, mw=80.4;
        double l1_pz = leptons[0]->Pz();
        double l1_px = leptons[0]->Px();
        double l1_py = leptons[0]->Py();
        double l1_E = leptons[0]->E();
        double MET = met->MET;
        double met_px = MET*cos(met->Phi);
        double met_py = MET*sin(met->Phi);
        a=4*(l1_pz*l1_pz-l1_E*l1_E);
        b=4*l1_pz*(mw*mw+2*l1_px*scale*del_met[0].px()+2*l1_py*scale*del_met[0].py());
        c=(mw*mw+2*l1_px*scale*del_met[0].px()+2*l1_py*scale*del_met[0].py())*(mw*mw+2*l1_px*scale*del_met[0].px()+2*l1_py*scale*del_met[0].py())-4*l1_pz*l1_pz*scale*del_met[0].e()*scale*del_met[0].e();
        delta=b*b-4*a*c;
        
        while(delta<0) {
            scale-=0.01;
            a=4*(l1_pz*l1_pz-l1_E*l1_E);
            b=4*l1_pz*(mw*mw+2*l1_px*scale*del_met[0].px()+2*l1_py*scale*del_met[0].py());
            c=(mw*mw+2*l1_px*scale*del_met[0].px()+2*l1_py*scale*del_met[0].py())*(mw*mw+2*l1_px*scale*del_met[0].px()+2*l1_py*scale*del_met[0].py())-4*l1_pz*l1_pz*scale*del_met[0].e()*scale*del_met[0].e();
            delta=b*b-4*a*c;
        }
        
        Double_t pz=(abs((-b+sqrt(delta))/(2*a))<abs((-b-sqrt(delta))/(2*a)))?(-b+sqrt(delta))/(2*a):(-b-sqrt(delta))/(2*a);
        
        fastjet::PseudoJet pseudojet_tmp(del_met[0].px(),del_met[0].py(),pz,sqrt(del_met[0].px()*del_met[0].px()+del_met[0].py()*del_met[0].py()+pz*pz));
        
        del_v1=pseudojet_tmp;

    }
    progressBar.Finish();
}


int run_analysis(const char* inputList, MyPlots* plots, Counter* counter) {
    ExRootResult *result = new ExRootResult();
    BookHistograms(result, plots);
    TChain chain("Delphes");
    FillChain(&chain, inputList);
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    AnalyseEvents(treeReader, plots, counter);
    return 0;
}

int main(int argc, char **argv ) {
    MyPlots *signal_plots = new MyPlots;
    Counter* signal_counter = new Counter();
    Counter* bg_counter = new Counter();
    MyPlots *bg_plots = new MyPlots;
    run_analysis("signal_input_list.txt", signal_plots, signal_counter);
    run_analysis("bg_input_list.txt", bg_plots, bg_counter);
    ExRootResult *result = new ExRootResult();
    THStack *stack;
    stack = result->AddHistStack("whad", "Whad");

    signal_plots->m_W_hadronic_candidate->SetLineColor(kBlue);
    bg_plots->m_W_hadronic_candidate->SetLineColor(kRed);

    stack->Add(signal_plots->m_W_hadronic_candidate);
    stack->Add(bg_plots->m_W_hadronic_candidate);
    result->Print("pdf");

    std::vector<std::string> cutNames = {
       "Initial",
       "1/2 b-jets",
       "1 tau jet",
       "2+ untagged jets",
       "2 leptons",
       "OS Leptons",
       "OS tau jet"
    };
    std::ofstream f; f.open("cut_flow_table.txt");
    f << "Cut Name" << '\t' << "Signal MC Events" << '\t' 
      << "Background MC Events" << std::endl;
    for (int i=0; i<7; i++) {
        f << cutNames[i] << '\t' << signal_counter->counter[i] << '\t' 
          << bg_counter->counter[i] << std::endl;
    }
    f.close();
    return 0;
}
