#include <iostream>
#include <stdio.h>

#include <fstream>
#include "cHtb_xsection.h"

using namespace std;

int main(int argc, char* argv[]) {

  // Get the signal benchmark point from command line arguments
  double mC = atof(argv[1]);
  double tan_beta = 1.5;
  cout <<  MyCrossSection_100TeV_Htb(mC, tan_beta) << endl;

  return 0;
}
