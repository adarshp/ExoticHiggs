#!/bin/bash
#PBS -N bdt_scan
#PBS -M adarsh@email.arizona.edu
#PBS -W group_list=shufang
#PBS -q standard
#PBS -l select=1:ncpus=28:mem=168gb:pcmem=6gb
#PBS -l cput=672:0:0
#PBS -l walltime=24:0:0

cd ~/ExoticHiggs/root_analysis

backgrounds="tttautau"
for p in $backgrounds; do
    ls -f /rsgrps/shufang/Events/$p/*.root > $p\_input_list.txt
done

echo "mC mH significance bdt_significance" > significances.txt

analyze_bp() {
    read mC mH BR <<< $1
    local bp_dirname="mC_$mC""_mH_$mH"
    local target_dir=/rsgrps/shufang/Events/C_HW_tataW/$bp_dirname
    local input_list=$bp_dirname"_input_list.txt" 

    ls -f $target_dir/*.root > $input_list 
    read sig bdt_sig <<< `./analyze $bp_dirname $mC $mH $BR`
    echo $mC $mH $sig $bdt_sig >> significances.txt
    rm $input_list
}

export -f analyze_bp

benchmark_plane=$HOME/ExoticHiggs/benchmark_planes/BP_IIB_tb_1.5.txt
cat $benchmark_plane | awk 'NR>1{print $3, $1, $11}' | parallel --bar -k -j 28 analyze_bp {}

# for single benchmark point:
# cat $benchmark_plane | head -n 2 |  awk 'NR>1{print $3, $1, $11}' | parallel -j 1 analyze_bp {}
