# Create xdisk allocation of 1TB for 45 days
xdisk -c create -m 1000

# Create MG5 directories
source create_mg5_dirs.sh

# Set benchmark point for signal in myProcesses.py, then do:
python myProcesses.py

# Generate charged higgs signal events
qsub pbs_scripts/generate_charged_higgs_events.pbs
