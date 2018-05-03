from __future__ import division
import os, glob
import sys
sys.path.insert(0,'/rsgrps/shufang/clusterpheno')
from clusterpheno.Process import Process
from clusterpheno.helpers import cd, modify_file, do_parallel
import subprocess as sp
import numpy as np
import shutil as sh
import gzip
import pandas as pd
from tqdm import tqdm
from ConfigParser import SafeConfigParser

def get_benchmark_points(filename):
    df = pd.read_csv('benchmark_planes/'+filename,
                     delim_whitespace=True, dtype = 'str')
    return df.iterrows()

# Get benchmark points from a text file
BP_IIB_mC_mH = get_benchmark_points('BP_IIB_mC_mH.txt')
BP_IIB_mC_tb = get_benchmark_points('BP_IIB_mC_tb.txt')
BP_IIB_mC_deltaM = get_benchmark_points('BP_IIB_mC_deltaM.txt')

# Define a collection of signal processes corresponding to the
# Benchmark point

class TwoHiggsDoubletModelProcess(Process):

    def __init__(self, name, decay_channel, mg5_generation_syntax=None, energy, benchmark_point):

        self.bp = benchmark_point
        Process.__init__(self, name, '2HDM', decay_channel, mg5_generation_syntax, energy, self.make_index()) 

    def make_index(self):
        return '_'.join(["mC", str(float(self.bp['mC'])), "mH", str(float(self.bp['mH']))])

    def set_parameters(self):
        def set_2HDM_params(line):
            words = line.split()
            if "mh1" in words: return "   25  125.09 # mh1\n"
            elif "mh2" in words: return "   35 {} # mh2\n".format(self.bp['mH'])
            elif "mh3" in words: return "   36 {} # mh3\n".format(self.bp['mA'])
            elif "mhc" in words: return "   37 {} # mhc\n".format(self.bp['mC'])
            elif "Wh1" in words: return "DECAY  25 {} # Wh1\n".format(self.bp['wh'])
            elif "Wh2" in words: return "DECAY  35 {} # Wh2\n".format(self.bp['wH'])
            elif "Wh3" in words: return "DECAY  36 {} # Wh3\n".format(self.bp['wA'])
            elif "Whc" in words: return "DECAY  37 {} # Whc\n".format(self.bp['wC'])
            else: return line

        modify_file('Cards/param_card.dat', set_2HDM_params)


C_HW_tautau_ll_100_TeV_mC_mH_collection = [TwoHiggsDoubletModelProcess(
        name = 'C_HW',
        decay_channel = 'tataW',
        energy = 100,
        benchmark_point = bp[1],
    ) for bp in list(BP_IIB_mC_mH)]

C_HW_tautau_ll_100_TeV_mC_tb_collection = [TwoHiggsDoubletModelProcess(
        name = 'C_HW',
        decay_channel = 'tataW',
        energy = 100,
        benchmark_point = bp[1],
    ) for bp in list(BP_IIB_mC_tb)]

C_HW_tautau_ll_100_TeV_mC_deltaM_collection = [TwoHiggsDoubletModelProcess(
        name = 'C_HW',
        decay_channel = 'tataW',
        energy = 100,
        benchmark_point = bp[1],
    ) for bp in list(BP_IIB_mC_deltaM)]
