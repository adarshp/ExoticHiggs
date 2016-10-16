import os
import re
import subprocess as sp
import shutil as sh
from helpers import *
from ClusterConfiguration import myClusterConfig

class Process(object):
    def __init__(
            self, name, model, decay_channel, 
            mg5_generation_syntax, energy, index):

        self.name = name
        self.model = model
        self.decay_channel = decay_channel
        self.mg5_generation_syntax = mg5_generation_syntax
        self.energy = str(energy)+'_TeV'
        self.index = str(index)

        self.common_path = '/'.join([self.process_type()+'s', self.name, 
                                     self.decay_channel, self.energy, self.index])
        self.directory = '/'.join(['Events', self.common_path])

    def create_directory(self):
        proc_card = '/'.join(['Cards/proc_cards', self.common_path+ '_proc_card.dat'])
        if not os.path.exists(os.path.dirname(proc_card)):
            try:
                os.makedirs(os.path.dirname(proc_card))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(proc_card, 'w') as f:
            f.write('import model {}\n'.format(self.model))
            f.write(self.mg5_generation_syntax+'\n')
            f.write('output '+self.directory)
        sp.call(['./Tools/mg5/bin/mg5_aMC', proc_card])

    def process_type(self):
        if self.model == 'sm': return 'Background'
        else: return 'Signal'

    def copy_cards(self):
        destination = self.directory+'/Cards/'
        sh.copy('Cards/run_cards/run_card.dat', destination)
        sh.copy('Cards/delphes_cards/delphes_card.dat', destination)
        sh.copy('Cards/pythia_cards/pythia_card.dat', destination)

    def write_pbs_script(self, myClusterConfig, nb_run):
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

        with open('submit.pbs', 'w') as f:
            f.write(pbs_script_template.format(
                    jobname = self.name[:15],
                    email = myClusterConfig.email,
                    group_list = myClusterConfig.group_list,
                    username = myClusterConfig.username,
                    cput = str(15*nb_run),
                    walltime = str(30*nb_run),
                    mg5_process_dir = self.directory,
                    nb_run = str(nb_run),
                  ))

    
    def setup_for_generation(self, nb_run, nevents):
        self.copy_cards()
        def set_beam_energy(line): 
            ebeam = int(self.energy.split('_')[0])*500
            if 'ebeam1' in line.split(): 
                return str(ebeam)+' = ebeam1 ! beam1 total energy in GeV\n'
            elif 'ebeam2' in line.split(): 
                return str(ebeam)+' = ebeam2 ! beam2 total energy in GeV\n'
            else: 
                return line
        with cd(self.directory):
            self.write_pbs_script(myClusterConfig, nb_run)
            modify_file('Cards/run_card.dat',set_beam_energy) 
            modify_file('Cards/run_card.dat', lambda x: re.sub(r'\d* = nev', str(nevents)+" = nev", x))

    def generate_events(self, nb_run = 1, nevents = 10000):
        self.setup_for_generation(nb_run, nevents)
        sp.call(['qsub', 'submit.pbs'], stdout = open(os.devnull, 'w')) 
