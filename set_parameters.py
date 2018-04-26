import sys
from myProcesses import Hc_HW_tautau_ll_100_TeV_collection, Hc_HW_tautau_ll_100_TeV_deltaM_200_collection 
from clusterpheno.helpers import cd, modify_file
import shutil as sh
import os

def copy_cards_and_set_parameters(process):
    """ Copy cards and set parameters for the process """
    cards_dir = '/home/u13/adarsh/ExoticHiggs/Cards'
    with cd('/tmp/charged_higgs'):
        sh.copy(cards_dir+'/delphes_cards/delphes_card_with_top_tagging.tcl',
                'Cards/delphes_card.dat')
        sh.copy(cards_dir+'/run_cards/run_card.dat',
                'Cards/run_card.dat')
        process.set_parameters()

if __name__ == '__main__':
    p1 = float(sys.argv[2])
    p2 = float(sys.argv[3])

    if sys.argv[1] == '--mC_mH':
        myproc = filter(lambda x: float(x.bp['mC']) == p1 and float(x.bp['mH']) == p2,
                     Hc_HW_tautau_ll_100_TeV_collection)[0]
    if sys.argv[1] == '--mC_tb':
        myproc = filter(lambda x: float(x.bp['mC']) == p1 and float(x.bp['tb']) == p2,
                     Hc_HW_tautau_ll_100_TeV_deltaM_200_collection)[0]

    copy_cards_and_set_parameters(myproc)
