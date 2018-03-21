benchmark_plane=$HOME/ExoticHiggs/benchmark_planes/BP_IIB_tb_1.5.txt
read mC mH <<< `awk 'NR==10{print $3, $1}' $benchmark_plane`

bp_dirname="mC_$mC""_mH_$mH"
target_dir=/rsgrps/shufang/Events/C_HW_tataW/$bp_dirname
ls -f $target_dir/*.root > "Signal_input_list.txt"

./make_histograms $mC $mH
python make_histograms.py
