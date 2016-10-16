import os, glob, subprocess
from Process import Process
import shutil as sh
from helper_functions import cd, modify_file

devnull = open(os.devnull, 'w')

class SignalProcess(Process):

    def __init__(self, mH, mA, mC, tb, cba, m122, wh, wH, wA, wC, xs):
        self.process_type = "Signal"
                              
        self.mH = mH
        self.mA = mA
        self.mC = mC
        self.tb = tb
        self.cba = cba
        self.m122 = m122
        self.wh = wh
        self.wH = wH
        self.wA = wA
        self.wC = wC
        self.xsection = xs

        self.bp = '_'.join(["mH", self.mH, "mA", self.mA, "mC", self.mC,
                            "tb", self.tb, "cba", self.cba,"m122", self.m122])

        self.common_path = '/'.join([self.process_type+'s', self.name, self.decay_channel, self.bp])
        self.process_directory = "mg5_processes/"+self.common_path

        self.proc_card_path = "Cards/proc_cards/"+self.name+"_proc_card.dat"
        self.param_card = None

    def write_proc_card(self):
        with open(self.proc_card_path, 'w') as f:
            f.write('import model 2HDM_HEFT\n')
            f.write(self.mg5_generation_syntax)
            f.write('output '+self.process_directory)

    def make_original_input_list(self, analysis_directory):
        """ Gathers filepaths for the events and writes them to the Input sub-
        directory of the analysis directory. """

        with cd(self.process_directory+'/Events'):
            cwd = os.getcwd()
            inputfiles = glob.glob('*/*.lhco.gz')
            inputfiles = [cwd+'/'+path for path in inputfiles]

        with cd(analysis_directory):
            with open('Input/Originals/'+self.name, 'w') as f:
                [f.write(filepath+'\n') for filepath in inputfiles]

    def write_and_copy_param_card(self):
        """ Write a param card with the relevant masses and widths in the 2HDM
        and copy it to the MG5 output directory."""

        def set_params(line):
            words = line.split()

            if "mh1" in words: return "   25 {} # mh1\n".format(self.mH)
            elif "mh2" in words: return "   35 {} # mh2\n".format(self.mH)
            elif "mh3" in words: return "   36 {} # mh3\n".format(self.mA)
            elif "mhc" in words: return "   37 {} # mhc\n".format(self.mC)
            elif "Wh1" in words: return "DECAY  25 {} # Wh1\n".format(self.wH)
            elif "Wh2" in words: return "DECAY  35 {} # Wh2\n".format(self.wH)
            elif "Wh3" in words: return "DECAY  36 {} # Wh3\n".format(self.wA)
            elif "Whc" in words: return "DECAY  37 {} # Whc\n".format(self.wC)
            else: return line

        modify_file('Cards/param_cards/param_card.dat', set_params)
        sh.copy('Cards/param_cards/param_card.dat',
                self.process_directory+'/Cards/param_card.dat')
    
