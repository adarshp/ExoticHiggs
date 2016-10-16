import os, glob
import subprocess as sp
from Process import Process
import shutil as sh
from helpers import cd, modify_file

class TwoHiggsDoubletModelProcess(Process):

    def __init__(self, name, decay_channel, mg5_generation_syntax, energy, benchmark_point):

        self.bp = benchmark_point
        Process.__init__(self, name, '2HDM_HEFT', decay_channel, mg5_generation_syntax, energy, self.make_index()) 

    def make_index(self):
        return '_'.join(["mA", self.bp.mA, "tb", self.bp.tb])

    def generate_events(self, nb_run = 1, nevents = 10000):
        self.setup_for_generation(nb_run, nevents)

        def set_2HDM_params(line):
            words = line.split()
            if "mh1" in words: return "   25 {} # mh1\n".format(self.bp.mH)
            elif "mh2" in words: return "   35 {} # mh2\n".format(self.bp.mH)
            elif "mh3" in words: return "   36 {} # mh3\n".format(self.bp.mA)
            elif "mhc" in words: return "   37 {} # mhc\n".format(self.bp.mC)
            elif "Wh1" in words: return "DECAY  25 {} # Wh1\n".format(self.bp.wH)
            elif "Wh2" in words: return "DECAY  35 {} # Wh2\n".format(self.bp.wH)
            elif "Wh3" in words: return "DECAY  36 {} # Wh3\n".format(self.bp.wA)
            elif "Whc" in words: return "DECAY  37 {} # Whc\n".format(self.bp.wC)
            else: return line

        with cd(self.directory):
            modify_file('Cards/param_card.dat', set_2HDM_params)
            sp.call(['qsub', 'submit.pbs'], stdout = open(os.devnull, 'w')) 
