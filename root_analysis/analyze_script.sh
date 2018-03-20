backgrounds="tttautau"
for p in $backgrounds; do
    ls -f /rsgrps/shufang/Events/$p/*.root > $p\_input_list.txt
done

echo "mC mH signficance" > significances.txt

analyze_bp() {
    read mC mH BR <<< $1
    local bp_dirname="mC_$mC""_mH_$mH"
    local target_dir=/rsgrps/shufang/Events/C_HW_tataW/$bp_dirname
    local input_list=$bp_dirname"_input_list.txt" 

    ls -f $target_dir/*.root > $input_list 
    significance=`./analyze $bp_dirname $mC $mH $BR`
    echo $mC $mH $significance >> significances.txt
    rm $input_list
}

export -f analyze_bp

benchmark_plane=$HOME/ExoticHiggs/benchmark_planes/BP_IIB_tb_1.5.txt
cat $benchmark_plane | awk 'NR>1{print $3, $1, $11}' | parallel --bar -j 28 analyze_bp {}
rm /tmp/mC*
rm /tmp/tttautau*
