from __future__ import division
import os, glob
import sys
sys.path.insert(0,'/home/u13/adarsh/clusterpheno')
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
    df = pd.read_csv(filename, delim_whitespace=True, dtype = 'str')
    return df.iterrows()

# Get benchmark points from a text file
BP_IIB = get_benchmark_points('benchmark_planes/BP_IIB_tb_1.5.txt')

# Define a collection of signal processes corresponding to the
# Benchmark point

class TwoHiggsDoubletModelProcess(Process):

    def __init__(self, name, decay_channel, mg5_generation_syntax, energy, benchmark_point):

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


Hc_HW_tautau_ll_100_TeV_collection = [TwoHiggsDoubletModelProcess(
        name = 'C_HW',
        decay_channel = 'tataW',
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

def create_signal_directory(process):
    """ Create madgraph directory for the process"""
    cards_dir = '/home/u13/adarsh/ExoticHiggs/Cards'
    proc_card = process.index+'.dat'
    with cd(cards_dir+'/mg5_proc_cards/'):
        sh.copy('charged_higgs.dat', 
                proc_card)
        modify_file(proc_card, lambda line: line.replace('charged_higgs', process.index))

    proc_collection_dir = '/xdisk/adarsh/C_HW_tataW/'
    with cd(proc_collection_dir):
        sp.call(['/home/u13/adarsh/MG5_aMC_v2_6_0/bin/mg5',
                cards_dir+'/mg5_proc_cards/'+proc_card],
                stdout=open(os.devnull, 'w')
                )
        os.remove(cards_dir+'/mg5_proc_cards/'+proc_card)

def copy_cards_and_set_parameters(process):
    """ Copy cards and set parameters for the process """
    with cd('/xdisk/adarsh/C_HW_tataW/'+process.index):
        process.set_parameters()
        sh.copy(cards_dir+'/delphes_cards/delphes_card_with_top_tagging.tcl',
                'Cards/delphes_card.dat')
        sh.copy(cards_dir+'/run_cards/run_card.dat',
                'Cards/run_card.dat')
            

parser = SafeConfigParser()
parser.read('config.ini')

def write_pbs_script(process):
    """ Write a PBS script to the signal bp directory """
    with open(parser.get('PBS Templates', 'generate_script'), 'r') as f:
        string = f.read() 

    with cd(process.directory):
        nruns = 1
        with open('generate_events.pbs', 'w') as f:
            stringify = lambda x: str(int(float(x)))
            jobname = stringify(process.bp['mC'])+'_'+stringify(process.bp['mH'])
            f.write(string.format(jobname = jobname,
                                  email = parser.get('Cluster', 'email'),
                                  group_list = parser.get('Cluster', 'group_list'),
                                  nruns = str(nruns),
                                  cput = str(28),
                                  walltime = str(1),
                                  mg5_process_dir = process.directory))
