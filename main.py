#!/usr/bin/env python
import os
import sys
sys.path.insert(0,'/extra/adarsh/clusterpheno')
from clusterpheno.helpers import cd, modify_file, do_parallel
from myProcesses import Hc_HW_tautau_ll_14_TeV_collection
from tqdm import tqdm
from ConfigParser import SafeConfigParser
import argparse

# Procedure
# - Create directories
# - Modify param_card
# - Copy delphes and run cards
# - Write submit scripts
# - Submit jobs to cluster

def create_directories(signals):
    # to be done on an Ocelote node
    do_parallel(lambda x: x.create_directory('/extra/adarsh/Tools/mg5'),
                signals,28)
    map(lambda x: x.set_parameters(), tqdm(signals))
    map(lambda x: x.copy_cards('Cards/run_cards/14_TeV_run_card.dat',
                                'Cards/pythia_cards/pythia_card.dat',
                                'Cards/delphes_cards/14_TeV.tcl'), 
                                tqdm(signals,
                                     desc='Copying cards'))

def write_pbs_scripts(processes, parser, nruns):
    for process in tqdm(processes, dynamic_ncols = True,
                        desc = 'Writing PBS submit scripts'):
        with open(parser.get('PBS Templates', 'generate_script'), 'r') as f:
            string = f.read()
        with open(process.directory+'/generate_events.pbs', 'w') as f:
            f.write(string.format(jobname =process.index,
                                  username = parser.get('Cluster', 'username'),
                                  email = parser.get('Cluster', 'email'),
                                  group_list = parser.get('Cluster', 'group_list'),
                                  nruns = str(nruns),
                                  cput = str(28*nruns), # cputime in hrs
                                  walltime = str(1*nruns), # walltime in hrs
                                  cwd = os.getcwd(),
                                  mg5_process_dir = process.directory))

def make_signal_feature_arrays(signals):
    for signal in tqdm(signals):
        scriptName = signal.index+'.pbs'
        with open(scriptName,'w') as f:
            f.write('''\
#!/bin/bash
#PBS -M adarsh@email.arizona.edu
#PBS -W group_list=shufang
#PBS -N {proc_name}
#PBS -q windfall
#PBS -l select=1:ncpus=1:mem=6gb:pcmem=6gb
#PBS -l place=free:shared
#PBS -l cput=5:0:0
#PBS -l walltime=5:0:0
date
cd /xdisk/adarsh/ExoticHiggs/MakeFeatureArrays/Build
./analyze.sh {proc_name}
date
exit 0
'''.format(proc_name = signal.index))
        sp.call(['qsub',scriptName],stdout=open(os.devnull,'w'))
        os.remove(scriptName)

def data_cleaning(proc_name):
    header = 'ptl1,ptl2,ptb1,ptb2,mll,mbb,mllbb,mR,mTR,MET,THT\n'
    with open('MakeFeatureArrays/Output/'+proc_name+'/feature_array.txt','r+') as f:
        lines = f.readlines()
        if not lines[0].startswith('p'):
            f.seek(0)
            lines.insert(0,header)
            f.writelines(lines)
            f.truncate()


processes = {
    "Hc_HW_tautau_ll_14_TeV":Hc_HW_tautau_ll_14_TeV_collection,
}

def write_nevents_to_file(signal):
    """ Scan over a range of bdt cuts and write the results to a file. """
        classifier = BDTClassifier(signal)
        # with open(signal.directory+'/MakeFeatureArray/nevents.csv', 'w') as f:
        with open('MakeFeatureArrays/Output/'+signal.index+'/nevents.csv', 'w') as f:
            print('ok so far')
            f.write('bdt_cut,nS,nB,significance\n')
            for bdt_cut in bdt_cut_range:
                table = make_bdt_cut_flow_table(classifier, bdt_cut)
                nS = table['Signal_events'][-1]
                nB = table['bg_events_tot'][-1]
                sig = table['Significance'][-1]
                f.write('{},{},{},{}\n'.format(str(bdt_cut),
                        str(int(nS)), str(int(nB)), str(sig)))
                                              
    except:
        pass

def main():
    mg5_path = '/extra/adarsh/Tools/mg5/'
    configparser = SafeConfigParser()
    configparser.read('config.ini')

    argparser = argparse.ArgumentParser(description="""\
    An interface for performing event generation and analysis on the cluster.""")
    argparser.add_argument("-cd","--create_dirs",
                        help = "Create MG5 directories for the process",
                        action="store_true")
    argparser.add_argument("-sj","--submit_jobs",
                        help = "Submit event generation jobs to cluster",
                        action="store_true")
    argparser.add_argument("-mfa","--make_feature_arrays",
                        help = "Make signal feature arrays",
                        action="store_true")
    argparser.add_argument("--bdt_scan",
                        help = "Perform BDT scan",
                        action="store_true")
    args = argparser.parse_args()

    if args.create_dirs: 
        create_directories(processes["Hc_HW_tautau_ll_14_TeV"])
    if args.submit_jobs: 
        write_pbs_scripts(processes["Hc_HW_tautau_ll_14_TeV"], configparser, 1)
        map(lambda x: x.generate_events(),
            tqdm(processes["Hc_HW_tautau_ll_14_TeV"], desc = "submitting PBS jobs"))
    if args.make_feature_arrays:
        make_signal_feature_arrays(processes["Hc_HW_tautau_ll_14_TeV"])
    if args.bdt_scan:
        do_parallel(write_nevents_to_file,processes["Hc_HW_tautau_ll_14_TeV"], 14)
if __name__ == '__main__':
    main()
