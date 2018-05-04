import sys
from myProcesses import (C_HW_tautau_ll_100_TeV_mC_mH_collection,
                         C_HW_tautau_ll_100_TeV_mC_tb_collection,
                         C_HW_tautau_ll_100_TeV_mC_deltaM_collection)

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

    def get_proc(param1, param2, collection):
        return filter(lambda x: float(x.bp[param1]) == p1 
                            and float(x.bp[param2]) == p2,
                      collection)[0]

    if sys.argv[1] == '--mC_mH':
        myproc = get_proc('mC', 'mH', C_HW_tautau_ll_100_TeV_mC_mH_collection)
    if sys.argv[1] == '--mC_tb':
        myproc = get_proc('mC', 'tb', C_HW_tautau_ll_100_TeV_mC_tb_collection)
    if sys.argv[1] == '--mC_deltaM':
        myproc = get_proc('mC', 'mH', C_HW_tautau_ll_100_TeV_mC_deltaM_collection)

    copy_cards_and_set_parameters(myproc)
