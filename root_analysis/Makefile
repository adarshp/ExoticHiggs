####################################
CC             = g++ -std=c++11 -Wno-deprecated
######### ROOT #####################
ROOTCFLAGS     = $(shell root-config --cflags)
ROOTLIBS       = $(shell root-config --libs) -lMLP -lMinuit -lTreePlayer -lTMVA -lXMLIO  -lMLP -lm
######### FASTJET ##################
FASTJETSYS      = /home/u13/adarsh/MG5_aMC_v2_6_0/Delphes/external
FASTJETCFLAGS  = -I${FASTJETSYS}
######### DELPHES ##################
DELPHESSYS     = /home/u13/adarsh/MG5_aMC_v2_6_0/Delphes/
DELPHESLIBS    = -L${DELPHESSYS} -lDelphes
DELPHESCFLAGS  = -I${DELPHESSYS} -I${DELPHESSYS}/modules -I${DELPHESSYS}/classes
######### EXROOTANALYSIS ##################
EXROOTSYS      = /home/u13/adarsh/MG5_aMC_v2_6_0/Delphes/external/ExRootAnalysis
EXROOTCFLAGS   = -I${EXROOTSYS}
######### BTAGGER ##################
BTAGCFLAGS     = -I./

#########  FLAGS, LIBS  ############
CXXFLAGS       = ${ROOTCFLAGS}
CXXFLAGS      += $(FASTJETCFLAGS)
CXXFLAGS      += $(DELPHESCFLAGS)
CXXFLAGS      += $(EXROOTCFLAGS)
CXXFLAGS      += $(BTAGCFLAGS) 

CXXLIBS        = $(ROOTLIBS)
CXXLIBS       += $(FASTJETLIBS)
CXXLIBS       += $(DELPHESLIBS)

#########################################################

all: main ditop_analysis

%: %.o
	$(CC) $(CXXFLAGS) ditop.o $(CXXLIBS) -o $@
