from Process import Process
from SignalProcess import SignalProcess
import numpy as np
import itertools as it
import pandas as pd

class myProcesses(object):
    def __init__(self):
        self.backgrounds = self.define_backgrounds()
        self.all_processes = self.backgrounds

    def define_backgrounds(self):
        # Defining our processes
        # tt (fully leptonic decay chain)
        tt = Process('tt_fully_leptonic', 'Background')
        tt.mg5_generation_syntax = """\
        generate p p > t t~, (t > w+ b, w+ > l+ vl), (t~ > w- b~, w- > l- vl~)
        """
        tt.xsection = 17425.0 

        # Zbb (Z decays leptonically)
        Zbb = Process('Zbb', 'Background')
        Zbb.mg5_generation_syntax = """\
        generate p p > Z b b~, (Z > l+ l-)
        """
        Zbb.xsection = 10000.0
       
        def set_common_bg_attributes(background):
            """ Set common background process attributes. """

            background.process_type = "Background"
            background.run_card = "Cards/run_cards/run_card.dat"
            
        for background in [tt, Zbb]:
            set_common_bg_attributes(background)
        
        return [tt, Zbb]

class A_HZ(SignalProcess):
    """ Represents the :math:`A \\rightarrow HZ` exotic Higgs decay channel. """
    def __init__(self, *args, **kwargs):
        self.name = 'A_HZ'
        SignalProcess.__init__(self, *args, **kwargs)
        self.mg5_generation_syntax = """\
        generate g g > h3 , ( h3 > h2 z , h2 > b b~ , z > l+ l- )
        """

