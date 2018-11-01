# Aggregate the results from the cluster run

aggregate_results() {
    param_combination=$1
    intermediate_result_dir=intermediate_analysis_results/$param_combination

    parent_process=C_HW
    decay_channel=tataW

    aggregate_result_file=$parent_process\_$decay_channel\_$param_combination"_significances.txt"

    echo "mC mH tb Zd Ze" > $aggregate_result_file

    for f in $intermediate_result_dir/*; do
        awk 'NF==5 {print}' $f >> $aggregate_result_file 
        rm $f
    done
}

for param_combination in mC_mH mC_tb mC_deltaM; do
    aggregate_results $param_combination
done
