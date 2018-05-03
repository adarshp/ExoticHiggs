#!/bin/bash
#PBS -N mC_mH
#PBS -M adarsh@email.arizona.edu
#PBS -W group_list=shufang
#PBS -q standard
#PBS -l select=1:ncpus=28:mem=168gb
#PBS -l cput=28:0:0
#PBS -l walltime=1:0:0

cd ~/ExoticHiggs/root_analysis
module load parallel

backgrounds="tttautau"

for p in $backgrounds; do
    ls -f /rsgrps/shufang/Events/$p/*.root > $p\_input_list.txt
done


proc_name=C_HW_tataW
benchmark_plane=../benchmark_planes/BP_IIB_mC_mH.txt
benchmark_plane_path=$HOME/ExoticHiggs/benchmark_planes/$benchmark_plane

echo "mC mH tb significance bdt_significance" >  $proc_name"_significances.txt"

analyze_bp() {

    read mC mH tb BR_C_HW BR_H_tata <<< $1
    local bp_dirname=mC\_$mC\_mH_$mH\_tb_$tb
    local target_dir=/rsgrps/shufang/Events/$2/$bp_dirname
    local input_list=$2\_$bp_dirname\_input_list.txt

    ls -f $target_dir/*.root > $input_list
    read sig bdt_sig <<< `./analyze $2\_$bp_dirname $mC $mH $tb $BR_C_HW $BR_H_tata $2`
    echo $mC $mH $tb $sig $bdt_sig >> $2"_significances.txt"
    rm $input_list
    rm default/weights/TMVAClassification_$2\_mC_$mC\_mH_$mH\_tb_$tb\_BDTG.*
}

export -f analyze_bp

# cat $benchmark_plane_path | head -n 2 | awk 'NR>1{print $3, $1, $4, $11, $13}' \
#                           | parallel --bar -k -j 1 analyze_bp {} $proc_name

cat $benchmark_plane_path | awk 'NR>1{print $3, $1, $4, $11, $13}' \
                          | parallel --bar -k -j 28 analyze_bp {} $proc_name
