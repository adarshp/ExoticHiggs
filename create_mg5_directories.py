#!/usr/bin/env python

import sys, os, logging
from tqdm import tqdm
import pandas as pd
from SignalProcess import SignalProcess
from myProcesses import myProcesses
from helper_functions import cd, modify_file
from myProcesses import A_HZ

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(message)s')

def define_signals(signal_process, benchmark_points):
    """ Make a list of signal processes with associated benchmark plane
    parameters. 
    
    Parameters
    ----------
    signal_process : :class:`SignalProcess` 
        The kind of signal process to associate with the given benchmark points.
    benchmark_points : str
        The name of the file containing the relevant benchmark points, 
        for e.g., ``allpoints.txt``.

    """

    df = pd.read_csv(benchmark_points, delim_whitespace=True, dtype = 'str')
    df['BPs'] = df[['mH', 'mA', 'mC', 'tb', 'cba', 'm122', 'wh', 'wH', 
                    'wA', 'wC', 'Sigma(A)xBR(A>HV)']].apply(tuple, axis=1)
    benchmark_points = df['BPs'].tolist()
    return [signal_process(*BP) for BP in benchmark_points]

def create_mg5_dirs(signals):
    """ Create MadGraph5 output directories for the given signal processes."""

    mg5_path = "Tools/mg5"
    for signal in tqdm(signals, desc='Creating MG5 directories'):
        signal.create_mg5_process_directory(mg5_path)

    for signal in tqdm(signals, desc = 'Writing and copying 2HDM param_cards'):
        signal.write_and_copy_param_card()

    for signal in tqdm(signals, desc = 'Copying delphes cards'): 
        signal.copy_delphes_card('Cards/delphes_cards/delphes_card.dat')
        
    for signal in tqdm(signals, desc = 'Copying run cards'): 
        signal.copy_run_card('Cards/run_cards/run_card.dat')

    for signal in tqdm(signals, desc = 'Copying pythia cards'): 
        signal.copy_pythia_card('Cards/pythia_cards/pythia_card.dat')

def main():
    A_HZ_signals = define_signals(A_HZ, 'allpoints.txt')
    create_mg5_dirs(A_HZ_signals)

    
if __name__ == '__main__':
    main()
