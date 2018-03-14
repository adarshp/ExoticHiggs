# Script for generating events on the cluster.

# Set the random seed for event generation
randomseed=0

# Location of text file containing benchmark points
bp='benchmark_planes/BP_IIB_tb_1.5.txt'

# Get the charged higgs and neutral higgs mass and store them in the variables
# mC and mH
read mC mH <<< `head -n $(($1+1)) $bp | tail -n 1 | awk '{print $3, $1}'`

# Specify the location of the proc_card containing the MadGraph process
# generation syntax
procCard='~/ExoticHiggs/Cards/mg5_proc_cards/charged_higgs.dat'

# Enter /tmp directory which provides storage that is local to the node itself,
# so that we don't clog up /xdisk or /extra
cd /tmp

# Create the process directory
# mg5 $procCard 
# cd ~/ExoticHiggs
bp_dirname="mC_$mC""_mH_$mH"

# mv charged_higgs $bp_dirname
cd ~/ExoticHiggs
python set_parameters.py $mC $mH $randomseed

# Set random seed
# ... to be implemented

# Enter the process directory on /tmp
cd /tmp/$bp_dirname

# ./bin/generate_events -f --laststep=delphes
# copy files...
target_dir=/rsgrps/shufang/$bp_dirname

# Create the target directory if it does not exist
mkdir -p $target_dir

generated_sample=Events/run_01/tag_1_delphes_events.root

cp $generated_sample $target_dir/sample_`ls $target_dir | wc -l`

cd ..
rm -rf $bp_dirname
