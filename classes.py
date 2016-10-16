#!/usr/bin/env python

import os
import subprocess as sp
from collections import namedtuple

Process = namedtuple('Process', [ 
                                  'name',
                                  'model',
                                  'decay_channel',
                                  'process_type',
                                  'mg5_generation_syntax',
                                  'xsection',
                                ])

def create_mg5_directory(process, energy, index):
    common_path = '/'.join([process.name, process.decay_channel, energy])
    proc_card = '/'.join(['Cards', 'proc_cards', common_path+'_proc_card.dat'])
    mg5_process_dir = '/'.join(['mg5_processes', process.process_type+'s', common_path, index])
    if not os.path.exists(os.path.dirname(proc_card)):
        try:
            os.makedirs(os.path.dirname(proc_card))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(proc_card, 'w') as f:
        f.write('import model {}\n'.format(process.model))
        f.write(process.mg5_generation_syntax+'\n')
        f.write('output '+mg5_process_dir)
    sp.call(['./Tools/mg5/bin/mg5_aMC', proc_card])

def main():
    A_HZ_bbll = Process(
        name = 'A_HZ',
        decay_channel = 'bbll',
        process_type = 'Signal',
        model = '2HDM_HEFT',
        mg5_generation_syntax = """\
        generate g g > h3 , ( h3 > h2 z , h2 > b b~ , z > l+ l- )""",
        xsection = 0.589,
    )
    create_mg5_directory(A_HZ_bbll, '14_TeV', 'mA_300_tb_20')

if __name__ == '__main__':
    main()
