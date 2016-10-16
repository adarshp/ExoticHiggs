#!/usr/bin/env python
import sys, os, logging
from tqdm import tqdm
import subprocess as sp
import re
import shutil as sh
from helper_functions import cd, modify_file
from helper_functions import common_path, mg5_process_dir
from myProcesses import A_HZ_bbll, tt_bbll
from myBenchmarkPlanes import BP_IA
from cluster_configuration import myClusterConfig

pbs_script_template = """\
#!/bin/bash
#PBS -m bea
#PBS -N {jobname}
#PBS -M {email}
#PBS -W group_list={group_list}
#PBS -q standard
#PBS -l jobtype=htc_only
#PBS -l select=1:ncpus=5:mem=23gb
#PBS -l cput=0:{cput}:0
#PBS -l walltime=0:{walltime}:0
cd /extra/{username}/ExoticHiggs/{mg5_process_dir}
for i in {{1..{nb_run}}}
do
  ./bin/generate_events -f --laststep=delphes
  ./bin/madevent remove all parton -f
  ./bin/madevent remove all pythia -f
  rm -rf Events/run_*/tag_*_delphes_events.root
done
echo "DONE"
exit 0"""

def copy_cards(process, energy, index):
    destination_dir = mg5_process_dir(process, energy, index)+'/Cards/'
    sh.copy('Cards/run_cards/run_card.dat', destination_dir)
    sh.copy('Cards/delphes_cards/delphes_card.dat', destination_dir)
    sh.copy('Cards/pythia_cards/pythia_card.dat', destination_dir)

def generate_events(process, energy = '14_TeV', index = 'myIndex', 
                    nb_run = 1, nevents = 10000):

    def write_pbs_script():
        with open('submit.pbs', 'w') as f:
            f.write(pbs_script_template.format(jobname = process.name,
                    email = myClusterConfig.email,
                    group_list = myClusterConfig.group_list,
                    username = myClusterConfig.username,
                    cput = str(15*nb_run),
                    walltime = str(30*nb_run),
                    mg5_process_dir = mg5_process_dir(process, energy, index),
                    index = str(index),
                    nb_run = str(nb_run),
                  ))

    copy_cards(process, energy, index)

    def set_beam_energy(line): 
        ebeam = int(energy.split('_')[0])*500
        if 'ebeam1' in line.split(): 
            return str(ebeam)+' = ebeam1 ! beam1 total energy in GeV\n'
        elif 'ebeam2' in line.split(): 
            return str(ebeam)+' = ebeam2 ! beam2 total energy in GeV\n'
        else: 
            return line
    
    proc_dir = mg5_process_dir(process, energy, index)

    with cd(proc_dir):
        write_pbs_script()
        modify_file('Cards/run_card.dat',set_beam_energy) 
        modify_file('Cards/run_card.dat', lambda x: re.sub(r'\d* = nev', str(nevents)+" = nev", x))
        sp.call(['qsub', 'submit.pbs'], stdout = open(os.devnull, 'w')) 
    
def main():
    bp_names = ['_'.join(['mA', bp.mA, 'tb', bp.tb]) for bp in BP_IA]

    for bp_name in bp_names:
        generate_events(A_HZ_bbll,index = bp_name, nb_run = 5)

    for index in range(0,30):
        generate_events(tt_bbll, index = index, nb_run = 1)

if __name__ == "__main__":
    main()
