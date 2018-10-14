import sys
from myProcesses import (C_HW_tataW_100_TeV_processes,
                         C_HW_ttW_100_TeV_processes)

from clusterpheno.helpers import cd, modify_file
import shutil as sh
import os

processes_dict = {
    'C_HW_tataW': C_HW_tataW_100_TeV_processes,
    'C_HW_ttW': C_HW_ttW_100_TeV_processes,
}

def copy_cards_and_set_parameters(process, proc_name):
    """ Copy cards and set parameters for the process """
    cards_dir = '/home/u13/adarsh/ExoticHiggs/Cards'
    with cd('/tmp/'+proc_name):
        sh.copy(cards_dir+'/delphes_cards/delphes_card_with_top_tagging.tcl',
                'Cards/delphes_card.dat')
        sh.copy(cards_dir+'/run_cards/run_card.dat',
                'Cards/run_card.dat')
        process.set_parameters()

def get_proc(mC, mH, tb, collection):
    return filter(
        lambda x: (
            x.bp['mC'] == mC 
            and x.bp['mH'] == mH
            and x.bp['tb'] == tb
        ),
        collection
    )[0]

if __name__ == '__main__':
    mC = sys.argv[2]
    mH = sys.argv[3]
    tb = sys.argv[4]
    proc = sys.argv[5]

    myproc = get_proc(mC, mH, tb, processes_dict[proc][sys.argv[1]])
    copy_cards_and_set_parameters(myproc, proc_name)
