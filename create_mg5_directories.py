#!/usr/bin/env python

import os
import subprocess as sp
import pandas as pd
from myProcesses import A_HZ_bbll, tt_bbll
from myBenchmarkPlanes import BP_IA
from helper_functions import common_path, mg5_process_dir
from tqdm import tqdm
    
def create_mg5_directory(process, energy, index):
    proc_card = '/'.join(['Cards', 'proc_cards', common_path(process, energy)+'_proc_card.dat'])
    if not os.path.exists(os.path.dirname(proc_card)):
        try:
            os.makedirs(os.path.dirname(proc_card))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(proc_card, 'w') as f:
        f.write('import model {}\n'.format(process.model))
        f.write(process.mg5_generation_syntax+'\n')
        f.write('output '+mg5_process_dir(process, energy, index))
    sp.call(['./Tools/mg5/bin/mg5_aMC', proc_card], stdout = open(os.devnull, 'w'))
    
def main():
    energies = ['14_TeV', '100_TeV']
    bp_names = ['_'.join(['mA', bp.mA, 'tb', bp.tb]) for bp in BP_IA]

    pbar = tqdm(total = 2*(30+len(bp_names)), desc = 'Creating MG5 Process directories')

    for index in bp_names:
        for energy in energies:
            create_mg5_directory(A_HZ_bbll, energy, index)

    for index in range(0, 30):
        for energy in energies:
            create_mg5_directory(tt_bbll, energy, str(index))

if __name__ == '__main__':
    main()
