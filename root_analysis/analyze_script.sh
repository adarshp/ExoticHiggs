analyze() {
    n=$1
    benchmark_plane=$HOME/ExoticHiggs/benchmark_planes/BP_IIB_tb_1.5.txt
    read mC mH <<< `head -n $(($n + 1)) $benchmark_plane \
                    | tail -n 1 \
                    | awk '{print $3, $1}'`
    bp_dirname="mC_$mC""_mH_$mH"
    target_dir=/rsgrps/shufang/Events/C_HW_tataW/$bp_dirname
    input_list=$bp_dirname"_input_list.txt" 

    ls -f $target_dir > $input_list | xargs ./analyze
}
# ls -f *_input_list.txt | parallel 

analyze()
