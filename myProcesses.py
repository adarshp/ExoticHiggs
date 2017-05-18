from __future__ import division
import os, glob
import sys
sys.path.insert(0,'/extra/adarsh/clusterpheno')
from clusterpheno.Process import Process
from clusterpheno.helpers import cd, modify_file
import subprocess as sp
import numpy as np
import shutil as sh
import gzip
import pandas as pd

def get_benchmark_points(filename):
    df = pd.read_csv(filename, delim_whitespace=True, dtype = 'str')
    return df.iterrows()
# Get benchmark points from a text file
BP_IIB = get_benchmark_points('benchmark_planes/BP_IIB_tb_1.5.txt')

# Define a collection of signal processes corresponding to the
# Benchmark point

def get_xsection(filename):
    """ Get matched cross section from a .lhco.gz file"""
    with gzip.open(filename, 'r') as f:
        lines = f.readlines()
        myline = [line for line in lines if 'Integrated weight' in line][0]
        xsection = float(myline.split()[-1])
        return xsection

class TwoHiggsDoubletModelProcess(Process):

    def __init__(self, name, decay_channel, mg5_generation_syntax, energy, benchmark_point):

        self.bp = benchmark_point
        Process.__init__(self, name, '2HDM', decay_channel, mg5_generation_syntax, energy, self.make_index()) 

    def make_index(self):
        return '_'.join(["mH", str(int(float(self.bp['mH']))), "mC", str(int(float(self.bp['mC'])))])

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

        with cd(self.directory):
            modify_file('Cards/param_card.dat', set_2HDM_params)

    def get_xsection(self):
        with open(self.directory+'/mean_xsection.txt','r') as f:
            return float(f.readlines()[0])

    def get_xsection_from_LHCO_files(self):
        with cd(self.directory):
            filenames = glob.glob('Events/*/*.lhco.gz')
            mean_xsection = np.mean(map(get_xsection,filenames))
            with open('mean_xsection.txt','w') as f:
                f.write(str(mean_xsection))

Hc_HW_tautau_ll_14_TeV_collection = [TwoHiggsDoubletModelProcess(
        name = 'Hc_HW',
        decay_channel = 'tautau_ll',
        mg5_generation_syntax = """\
        define hc = h+ h-
        define w = w+ w- 
        define tt = t t~
        define bb = b b~
        define ll = l+ l-
        define vv = vl vl~
        generate g g > tt bb hc , ( hc > h2 w , h2 > ta+ ta- , w > ll vv ), (tt > bb w, w > j j)
        add process g g > tt bb hc , ( hc > h2 w , h2 > ta+ ta- , w > j j ), (tt > bb w, w > ll vv)
        """,
        energy = 100,
        benchmark_point = bp[1],
    ) for bp in list(BP_IIB)]
