#!/usr/bin/env python

"""This script will create a directory named `Tools`, then download
and install MadGraph 2.4.3 and the latest version of Delphes, and then link them
together. It will also create a directory named `Events` with the 
subdirectories `Events/Signals` and `Events/Backgrounds` to hold the
generated events. In addition, it copies the folder ``2HDM_HEFT`` to the 
``models`` subdirectory of the MadGraph directory (located at ``Tools/mg5``."""

import subprocess as sp
import os, shutil, logging
from ExoticHiggs.helpers import cd, modify_file

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(message)s')

def install_delphes():
    """ Downloads Delphes into the current directory, and compiles it with
    8 cores."""
    
    if os.path.exists('delphes'): shutil.rmtree('delphes')
    sp.call(['git', 'clone', 'https://github.com/delphes/delphes.git'])
    with cd('delphes'):
        sp.call('./configure; make -j 8', shell = True)

def install_madgraph():
    """Downloads and installs MadGraph5 to the current directory. Also installs
    installs pythia-pgs to the MadGraph directory."""

    if os.path.exists('mg5'): 
        logging.info('mg5 directory exists, removing it for a fresh install.')
        shutil.rmtree('mg5')

    # Download MadGraph 5
    logging.info("Downloading MadGraph5 v2.2.3 ...")
    sp.call(['wget',
    'https://launchpad.net/mg5amcnlo/2.0/2.2.x/+download/MG5_aMC_v2.2.3.tar.gz'])
    sp.call(['tar','-zxvf','MG5_aMC_v2.2.3.tar.gz'])
    os.rename('MG5_aMC_v2_2_3','mg5')

    # Delete the tarball
    os.remove('MG5_aMC_v2.2.3.tar.gz')

    with cd('mg5'):
        # Write a script to install Pythia
        with open('install_pythia.cmd','w') as f:
            f.write('install pythia-pgs\n')

        # Run MG5 with the commands to install Pythia and Delphes
        sp.call(['./bin/mg5_aMC','install_pythia.cmd'])

def download_madanalysis():
    """Downloads and extracts MadAnalysis5 to the current directory. Also 
    modifies the LHCOReader.cpp file so that MadAnalysis can deal with the new
    32-bit b-tagging prescription used by Delphes. """
    
    # Download MadAnalysis5
    if os.path.exists('madanalysis5'): shutil.rmtree('madanalysis5')

    try:
        sp.call(['wget',
        'https://launchpad.net/madanalysis5/trunk/v1.4/+download/MadAnalysis5_v1.4.tar.gz'])
    except:
        print("Dowloading MadAnalysis5 v1.4 failed \
        - check https://launchpad.net/madanalysis5 for a newer version.")
    sp.call(['tar','-zxvf','MadAnalysis5_v1.4.tar.gz'])
    os.remove('MadAnalysis5_v1.4.tar.gz')

    # Modify the LHCOReader file 
    with cd('madanalysis5/tools/SampleAnalyzer/Process/Reader'):
        modify_file('LHCOReader.cpp',
                    lambda line: line.replace('tmp ==2', 'tmp == 3'))

def specify_delphes_path(line):
    """ A helper function to check if a line starts with a delphes option, 
    to specify the correct Delphes path
    
    Parameters
    ----------
    line : string
        The line to process
    delphes_path : string
        The relative path of the Delphes directory from the package directory
    """
    if line.startswith('# delphes_'):
        words = line.split(' ')
        if words[1] in ['delphes_includes', 'delphes_libs', 'delphes_path']:
            delphes_path = os.getcwd() + '/delphes'
            line = '{} = {}\n'.format(words[1], delphes_path)
    return line

def link_package_with_delphes(package_name, package_path):
    """ Links the specified package with Delphes 
    
    Parameters
    ----------
    package_name : string
        The name of the package. Available options: madgraph, madanalysis
    package_path : string
        Relative path to the package
    delphes_path : string
        Relative path to Delphes (from the package directory)
    """

    if package_name == 'madgraph': 
        configfile = 'input/mg5_configuration.txt'
    elif package_name == 'madanalysis': 
        configfile = 'madanalysis/input/installation_options.dat'
    else: print('package_name must be \'madgraph\' or \'madanalysis\'.')

    filepath = package_path + configfile
    modify_file(filepath, specify_delphes_path)

def install_SigCalc():
    if not os.path.exists('SigCalc'): 
        os.makedirs('SigCalc')
    with cd('SigCalc'):
        sp.call(['wget', 'http://hacol13.physik.uni-freiburg.de/graduiertenkolleg/lectures/Cowan/sigcalc/SigCalc.tar'])
        sp.call(['tar', '-xvzf', 'SigCalc.tar'])
        sp.call(['make', '-j'])

def install_external_packages(install_directory):
    """ 
    Installs Delphes, MadGraph5 and MadAnalysis5 to the specified directory.
    
    Parameters
    ----------
    install_directory : string
        Name of the directory to install the packages to. If it does not exist
        already, it will be created.
    """

    if not os.path.exists(install_directory): 
        os.makedirs(install_directory)

    with cd(install_directory):
        logging.info('Installing Delphes ...')
        install_delphes()
        logging.info('Installing MadGraph5 ...')
        install_madgraph()
        logging.info('Linking MadGraph5 with Delphes ... ')
        link_package_with_delphes('madgraph', 'mg5/')
        logging.info('Copying 2HDM_HEFT to Tools/mg5 ...')
        shutil.copytree('../2HDM_HEFT', 'mg5/models/2HDM_HEFT')
        logging.info('Downloading MadAnalysis5 ...')
        download_madanalysis()
        logging.info('Linking MadAnalysis5 with Delphes ... ')
        link_package_with_delphes('madanalysis', 'madanalysis5/')
        logging.info('Starting up MadAnalysis5 for the first time to compile'
                        + ' SampleAnalyzer libraries...')
        sp.call('./madanalysis5/bin/ma5')
        logging.info('Installing SigCalc ... ')
        install_SigCalc()

def setup_directory_structure():
    """ Set up a directory structure for future event generation. """
    if not os.path.exists('Events/Signals'): 
        os.makedirs('Events/Signals')
    if not os.path.exists('Events/Backgrounds'): 
        os.makedirs('Events/Backgrounds')

def main():
    """ The main function. """
    setup_directory_structure()
    install_external_packages('Tools')

if __name__ == '__main__':
    main()
