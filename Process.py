import os, re, logging, glob
import pandas as pd
import subprocess as sp
import shutil as sh
from helper_functions import cd, modify_file
from cluster_configuration import cluster_config 

class Process(object):

    def __init__(self, name, decay_channel, process_type, xsection, mg5_generation_syntax):
        self.name = name
        self.process_type = process_type
        self.decay_channel = decay_channel
        self.mg5_generation_syntax = mg5_generation_syntax
        self.common_path = '/'.join([self.process_type+'s', self.name, self.decay_channel])
        self.proc_card_path = "Cards/proc_cards/"self.common_path+"_proc_card.dat"
        self.process_directory = "mg5_processes/"+self.common_path
        self.events_directory = "Events/"+self.process_type+"s/"+self.name+'/'+self.decay_channel
        self.xsection = xsection

    def copy_delphes_card(self, delphes_card_path):
        sh.copy(delphes_card_path, self.process_directory+'/Cards/delphes_card.dat')

    def copy_run_card(self, run_card_path):
        sh.copy(run_card_path, self.process_directory+'/Cards/run_card.dat')

    def copy_pythia_card(self, pythia_card_path):
        sh.copy(pythia_card_path, self.process_directory+'/Cards/pythia_card.dat')

    def write_proc_card(self):
        with open(self.proc_card_path, 'w') as f:
            f.write(self.mg5_generation_syntax)
            f.write('output '+self.process_directory)

    def create_mg5_process_directory(self, relative_mg5_path):
        """ 
        Create MadGraph5 process directory 
        
        Parameters
        ----------
        process_name : String
            The name of the process. 
        
        proc_card : String
            Relative path to the file containing the MadGraph5 commands, typically named
            something like ``proc_card.dat``.

        process_directory : String
            Directory in which the MadGraph process directory is to be placed.
        """
        self.write_proc_card()
        devnull = open(os.devnull, 'w')
        sp.call(['./'+relative_mg5_path+'/bin/mg5_aMC', self.proc_card_path],
                stdout = devnull)

    def write_generation_script(self):
        with open('generation_script.sh', 'w') as f:
            f.write('rm RunWeb\n')
            f.write('./bin/madevent multi_run -f --laststep=delphes\n')
            f.write('mv Events/run_01/tag_1_delphes_events.lhco.gz')
            f.write('rm Events/*/*.root')

    def generate_events_locally(self, nevents = 50000, nruns = 1):
        """ Modify the run card to generate the specified number of events.

        Parameters
        ----------

        nevents : int 
            The number of events to generate. """

        with cd(self.process_directory):
            devnull = open(os.devnull, 'w')
            modify_file('Cards/run_card.dat', 
                lambda x: re.sub(r'\d* = nev', str(int(nevents))+" = nev", x))
            self.write_generation_script()
            for i in range(0, nruns):
                sp.call(['sh','generation_script.sh'])

    def write_pbs_submission_script(self):
            pbs_script_template = """\
#!/bin/bash
#PBS -m bea
#PBS -N {process_name}
#PBS -M {email}
#PBS -W group_list={group_list}
#PBS -q standard
#PBS -l jobtype=htc_only
#PBS -l select=1:ncpus=5:mem=23gb:localscratch=1
#PBS -l cput=0:{cput}:0
#PBS -l walltime=0:{walltime}:0
cd /extra/{username}/ExoticHiggs/{cwd}
module load intel
module load root
date
pwd
for i in {{1..{nb_run}}}:
do
  sh generation_script.sh
done
date
echo "DONE"
exit 0"""

            with open("cluster_submission_script.pbs", 'w') as f:
                f.write(pbs_script_template.format(
                    username = cluster_config['username'],
                    email = cluster_config['email'],
                    group_list = cluster_config['group_list'],
                    process_name = self.name,
                    cput = nb_run*15,
                    walltime = nb_run*30,
                    cwd = self.process_directory ))

    def generate_events_on_cluster(self, nevents=50000, ebeam = 7000):
        """ Generate events on the cluster. For this option, only one run at a
        time is supported. The reasoning is that we are going to leverage the 
        power of distributed computing to generate events for many benchmark
        points at the same time. Requesting CPU time on the cluster for multiple
        runs would push us down the queue, and ultimately slow down the event
        generation.

        Parameters
        ----------

        nevents : int
            Number of events to generate for this run.
        ebeam : int
            Energy of each colliding beam.
            
        """
        
        with cd(self.process_directory):
            def set_beam_energy(line): 
                if 'ebeam1' in line.split(): 
                    return str(ebeam)+' = ebeam1 ! beam1 total energy in GeV\n'
                elif 'ebeam2' in line.split(): 
                    return str(ebeam)+' = ebeam2 ! beam2 total energy in GeV\n'
                else: 
                    return line

            def set_nb_core(line): 
                if 'nb_core' in line.split(): return 'nb_core=5\n'
                else: return line

            def set_compiler(line):
                if 'cpp_compiler' in line: return 'cpp_compiler=icc\n'
                else: return line
            def remove_stdlib_cpp_flag(line):
                if 'lstdc++' in line: return '#STDLIB=-lstdc++\n'
                else: return line

            modify_file('Cards/run_card.dat', 
                lambda x: re.sub(r'\d* = nev', str(nevents)+" = nev", x))
            modify_file('Cards/run_card.dat',set_beam_energy) 
            modify_file('Cards/me5_configuration.txt', set_nb_core)
            modify_file('Cards/me5_configuration.txt', set_compiler)
            modify_file('Source/make_opts', remove_stdlib_cpp_flag)

            self.write_generation_script()
            self.write_pbs_submission_script()          
            devnull = open(os.devnull, 'w')
            sp.call(['qsub', 'cluster_submission_script.pbs'], stdout=devnull)
    
    def make_original_input_list(self, analysis_directory):
        """ Gathers filepaths for the events and writes them to the Input sub-
        directory of the analysis directory. """

        with cd(self.process_directory):
            cwd = os.getcwd()
            inputfiles = glob.glob('*/*/*.lhco.gz')
            inputfiles = [cwd+'/'+path for path in inputfiles]

        with cd(analysis_directory):
            with open('Input/Originals/'+self.name, 'w') as f:
                [f.write(filepath+'\n') for filepath in inputfiles]

    def analyze_originals(self, analysis_directory, analysis_name):
        devnull = open(os.devnull, 'w')

        with cd(analysis_directory+'/Build/'):
            sp.call('./MadAnalysis5job ../Input/Originals/'+
                    self.name, shell=True, stdout = devnull, stderr = devnull)
                    
        if os.path.exists(analysis_directory+'/Output/'+self.name):
            with cd(analysis_directory+'/Output/'+self.name):
                sp.call(['mv', 'Analysis_0', analysis_name])
