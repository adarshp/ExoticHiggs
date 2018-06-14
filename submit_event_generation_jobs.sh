submit_job() {
    qsub -N $1\_gen -J 1-$((`wc -l benchmark_planes/BP_IIB_$1.txt |\
            awk '{print $1}'` - 1)) -v param_combination=$1 generate_C_HW_events.pbs
}

for param_combination in mC_mH mC_tb mC_deltaM; do
    submit_job $param_combination
done
