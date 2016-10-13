#!/usr/bin/env python
import sys, os, logging
from tqdm import tqdm
import pandas as pd
from SignalProcess import SignalProcess
from myProcesses import myProcesses
from helper_functions import cd, modify_file
from myProcesses import A_HZ

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
    
def main():
    """ Generate events for a process and a benchmark plane"""
    A_HZ_signals = define_signals(A_HZ, 'allpoints.txt')
    for signal in tqdm(A_HZ_signals, desc='Submitting event generation scripts to cluster'):
        signal.generate_events_on_cluster()

if __name__ == "__main__":
    main()
