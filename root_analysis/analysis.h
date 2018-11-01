#include "ordered_map.h"
#include "TTree.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "classes/DelphesClasses.h"
#include "TMVA/Factory.h"
#include "TMVA/DataLoader.h"
#include "TMVA/Tools.h"
#include "TMVA/IMethod.h"
#include "TMVA/MethodBase.h"
#include "TMVA/Types.h"
#include "TMVA/Config.h"
#include "TH1.h"
#include "TH1F.h"
#include "TH2F.h"

using namespace std;

template <class T>
Candidate make_candidate(T* delphes_particle) {
  // Make a Candidate object from a delphes particle.
  Candidate candidate;
  candidate.Momentum = delphes_particle->P4(); 
  candidate.Charge = delphes_particle->Charge;
  return candidate;
}


string signal_name;
double signal_xsection;
double mC, mH;

// Declare containers
vector<Jet*> 
    jets,
    untagged_jets,
    b_jets,
    tau_jets,
    top_jets;

vector<Candidate> leptons;

// Declare the feature names, create a map with keys corresponding to them
vector<string> featureNames = {
  "MET", 
  "pt_j1",
  "pt_l1",
  "pt_tau",
  "pt_b1",
  "mH",
  "mC"
};

vector<string> bgNames = {
  "tttautau-full",
  "tttautau-semi",
  "ttll-full",
  "ttlv-full"
};

// Original cross sections in femtobarns
map<string, double> original_xsections = {
  {"tttautau-full" , 78.5728426837} ,
  {"tttautau-semi" , 125.316052165} ,
  {"ttll-full"     , 20.1135267496} ,
  {"ttlv-full"     , 55.7115}
};


map<string, TTree*> background_ttrees;
map<string, TH1F*> plots;
map<string, double> features;
map< string, tsl::ordered_map<string, int> > counters;

void fill_1D_histo(
    string plot_name,
    int nbins,
    double xmin,
    double xmax,
    double variable
) {
    if (plots.count(plot_name) == 0) 
        plots[plot_name]  = new TH1F(plot_name.c_str(), plot_name.c_str(),
                                     nbins, xmin, xmax);
    else plots[plot_name]->Fill(variable);
}

TH1F* signal_bdt_histogram = new TH1F("Signal BDT Output", "BDT Output", 40, -1., 1.);
TH1F* background_bdt_histogram = new TH1F("Background BDT Output", "BDT Output", 40, -1., 1.);

void output_histogram_to_text_file(string process_name, TH1F* histo) {
    system(("mkdir -p "+process_name+"/histo_data/").c_str());
    ofstream h(process_name+"/histo_data/"+histo->GetName()+".txt");
    h << "Bin Low Edge" << '\t'  << "Bin Width" << '\t' << "Bin Entries" << endl;
    for (int i=1; i < histo->GetNbinsX(); i++) {
    h  << histo->GetBinLowEdge(i) << '\t'
       << histo->GetBinWidth(i)   << '\t'
       << histo->GetBinContent(i) << endl;
    }
    h.close();
}

void increment_counter(string process, string cut_name) {
    if (counters[process].count(cut_name) == 0) 
        counters[process][cut_name] = 0;
    else counters[process][cut_name]++;
}

tuple<double, double> calculate_Z_values(
    double s, double b, double systematic_error = 0.1
) {

    double 
        t1 = s+b,
        sigma_b = systematic_error*b,
        t2 = pow(sigma_b, 2),
        t3 = b + t2,
        t4 = t1*t3/(b*b + t1*t2),
        t5 = b*b/t2,
        t6 = 1 + t2*s/(b*t3),
        x = sqrt(pow(t1,2) - 4*s*b*t2/t3),
        Z_d = sqrt(2*(t1*log(t4) - t5*log(t6))),
        Z_e = sqrt(2*(s - b*log((b + s + x)/(2*b)) - t5*log((b-s+x)/(2*b))) - (b+s-x)*(1+b/t2));

    return make_tuple(Z_d, Z_e);
}

void clear_particle_collections(){
    jets.clear();
    untagged_jets.clear();
    b_jets.clear();
    tau_jets.clear();
    top_jets.clear();
    leptons.clear();
}

// Calculate the TMVA significance
tuple<double, double> calculate_tmva_significance(TTree* testTree) {
    float bdtout;
    char type;
    float weight;

    testTree->SetBranchAddress("BDTG",&bdtout);
    testTree->SetBranchAddress("className",&type);
    testTree->SetBranchAddress("weight",&weight);

    
    double
        s=0,
        b=0,
        L = 3000.0;

    double 
        cutoff=-1,
        sig_from_tmva = 0,
        candidate_Zd = 0,
        candidate_Ze = 0,
        Zd = 0, Ze = 0;

    // Loop over different values of the bdt response cutoff, pick the maximum
    // significance achieved.

    double w;
    /* for (int i = 0; i < testTree->GetEntries(); i++){ */
    /*     testTree->GetEntry(i); */
    /*     if (type=='S') */ 
    /*         signal_bdt_histogram->Fill(bdtout, weight); */
    /*     else background_bdt_histogram->Fill(bdtout, weight); */
    /* } */

    for (int j=0; j < 200; j++){
        for (int i = 0; i < testTree->GetEntries(); i++){
            testTree->GetEntry(i);
            if (bdtout > cutoff) {
                if (type=='S') s+=L*weight;
                else b+=L*weight;
            }
        }
        b = (b < 3)?3:b;
        tie(candidate_Zd, candidate_Ze) = calculate_Z_values(s, b);
        Zd = (candidate_Zd > Zd)?candidate_Zd:Zd;
        Ze = (candidate_Ze > Ze)?candidate_Ze:Ze;

        cutoff+=0.01;
    }

    return {Zd, Ze};
  }

TTree* perform_tmva_analysis(string classifierName, TTree* signal_tree) {

    // Create a TMVA Factory instance
    TMVA::Factory* factory = new TMVA::Factory(
        classifierName, 
        "!V:Silent:Color:!DrawProgressBar:Transformations=I;D;P;G,D"
        ":AnalysisType=Classification"
    );

    // Create a TMVA DataLoader instance
    TMVA::DataLoader* dataloader = new TMVA::DataLoader();

    // Add features
    for (auto n : featureNames)
        dataloader->AddVariable(n);

    // Calculate signal weight
    double signal_weight = signal_xsection
                          *counters[signal_name]["OS tau jet"]/counters[signal_name]["Initial"];



    // Add signal and background trees
    dataloader->AddSignalTree(signal_tree, signal_weight);

    double bg_weight;
    for (auto bg : bgNames) {
        bg_weight = original_xsections[bg]*counters[bg]["OS tau jet"]/counters[bg]["Initial"];
        dataloader->AddBackgroundTree(background_ttrees[bg], bg_weight);
    }


    // Prepare training and test data
    dataloader->PrepareTrainingAndTestTree("", "", "nTrain_Signal=0"
            ":nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V");

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
            ":MaxDepth=3"
    );

    // Perform training and testing
    factory->TrainAllMethods();
    factory->TestAllMethods();

    // Get testing results
    TMVA::IMethod* imethod = factory->GetMethod("default", "BDTG");
    TMVA::MethodBase* method = dynamic_cast<TMVA::MethodBase*> (imethod);
    TMVA::DataSet* dataset = method->Data();

    TTree* testTree = dataset->GetTree(TMVA::Types::kTesting);

    return testTree;
}
