# Submit analyses for all parameter pairs and benchmark points to the cluster.

proc_names="C_HW_tataW C_HW_tataW_mC_deltaM C_HW_tataW_fixed_deltaM"

# Initialize files to hold the significances
for p in $proc_names; do
    echo "mC mH tb Zd Ze" >  $p"_significances.txt"
done

sh make_bg_input_lists.sh

submit_job() {
    qsub -N $1\_analysis -J 1-$((`wc -l ../benchmark_planes/BP_IIB_$1.txt |\
            awk '{print $1}'` - 1)) -v param_combination=$1 analysis.pbs
}

for param_combination in mC_mH mC_tb mC_deltaM; do
    submit_job $param_combination
done
