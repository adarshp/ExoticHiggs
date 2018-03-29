#include "SampleAnalyzer/User/Analyzer/Analysis.h"
using namespace MA5;
using namespace std;

// -----------------------------------------------------------------------------
// Initialize
// function called one time at the beginning of the analysis
// -----------------------------------------------------------------------------

bool Analysis::Initialize(const MA5::Configuration& cfg, const std::map<std::string,std::string>& parameters)
{
  cout << "BEGIN Initialization" << endl;
  // initialize variables, histos
  PHYSICS -> recConfig().Reset();
  Manager()->AddRegionSelection("Signal");

  Manager()->AddCut("At least one lepton", "Signal");
  Manager()->AddHisto("MET", 40, 0, 1600, "Signal");

  cout << "END  Initialization" << endl;
  return true;
}

// -----------------------------------------------------------------------------
// Execute
// function called each time one event is read
// -----------------------------------------------------------------------------
bool Analysis::Execute(SampleFormat& sample, const EventFormat& event)
{
    double myEventWeight = 1.;
    Manager()->InitializeForNewEvent(myEventWeight);

    // Declaration of all particle containers
    std::vector<const RecLeptonFormat*> electrons, muons, leptons;
    std::vector<const RecJetFormat*> jets, b_jets;

    // Clear particle containers
    electrons.clear(); muons.clear(); leptons.clear();
    jets.clear(); b_jets.clear();

    //Filling all particle containers
    for (unsigned int i = 0; i < event.rec()->electrons().size(); i++) {
        const RecLeptonFormat* electron = &(event.rec()->electrons()[i]);
        if (electron->pt() > 15. and fabs(electron->eta()) < 2.5) {
            electrons.push_back(electron); leptons.push_back(electron);
        }
    }

    for (unsigned int i = 0; i < event.rec()->muons().size(); i++) {
        const RecLeptonFormat* muon = &(event.rec()->muons()[i]);
        if (muon->pt() > 15. and fabs(muon->eta() < 2.5)) {
            muons.push_back(muon); leptons.push_back(muon);
        }
    }
    for (unsigned int i = 0; i < event.rec()->jets().size(); i++) {
        const RecJetFormat* jet = &(event.rec()->jets()[i]);
        if (jet->pt() > 30. and fabs(jet->eta() < 2.5)) {
            jets.push_back(jet); 
            if (jet->btag() == true) b_jets.push_back(jet);
        }
    }

    // Sorting jets and leptons by PT
    SORTER->sort(leptons, PTordering);
    SORTER->sort(jets, PTordering);
    SORTER->sort(b_jets, PTordering);

    // Trigger and identification cuts
    if(!Manager()->ApplyCut(leptons.size() != 0, "At least one lepton")) return false;
    double ptl1 = leptons[0]->pt();
    if(!Manager()->ApplyCut(ptl1 > 100., "Lepton trigger")) return false;

    // MET definition
    RecParticleFormat met_particle = event.rec()->MET();
    MAVector3 met_vector = met_particle.momentum().Vect();
    double MET = met_particle.pt();
    Manager()->FillHisto("MET", MET);

    return true;
}

// -----------------------------------------------------------------------------
// Finalize
// function called one time at the end of the analysis
// -----------------------------------------------------------------------------
void Analysis::Finalize(const SampleFormat& summary, const std::vector<SampleFormat>& files)
{
    return;
}
