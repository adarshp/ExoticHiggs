# decay_channel = tataW or ttW

decay_channel=$1

submit_job() {
    n_bps=$((`wc -l benchmark_planes/BP_IIB_$1.txt |\ awk '{print $1}'` - 1)) 
    qsub -N $1\_gen -J 1-$n_bps -v param_combination=$1 -v decay_channel=$2 generate_signal_events.pbs
}

for param_combination in mC_mH mC_tb mC_deltaM; do
    submit_job $param_combination $decay_channel
done
