import sys
from myProcesses import Hc_HW_tautau_ll_100_TeV_collection 
from clusterpheno.helpers import cd, modify_file
import shutil as sh
import os

def copy_cards_and_set_parameters(process):
    """ Copy cards and set parameters for the process """
    cards_dir = '/home/u13/adarsh/ExoticHiggs/Cards'
    with cd('/tmp/'+process.index):
        sh.copy(cards_dir+'/delphes_cards/delphes_card_with_top_tagging.tcl',
                'Cards/delphes_card.dat')
        sh.copy(cards_dir+'/run_cards/run_card.dat',
                'Cards/run_card.dat')
        process.set_parameters()

if __name__ == '__main__':
    mC = float(sys.argv[1])
    mH = float(sys.argv[2])
    myproc = filter(lambda x: float(x.bp['mC']) == mC and float(x.bp['mH']) == mH,
                     Hc_HW_tautau_ll_100_TeV_collection)[0]
    copy_cards_and_set_parameters(myproc)
