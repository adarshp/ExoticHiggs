#!/bin/bash
#PBS -N mC_tb_analysis
#PBS -M adarsh@email.arizona.edu
#PBS -W group_list=shufang
#PBS -q windfall
#PBS -l select=1:ncpus=1:mem=2gb
#PBS -l place=free:shared
#PBS -l cput=0:20:0
#PBS -l walltime=0:20:0

cd ~/ExoticHiggs/root_analysis

backgrounds="tttautau"
proc_name=C_HW_tataW_fixed_deltaM
benchmark_plane=BP_IIB_mC_tb.txt
benchmark_plane_path=$HOME/ExoticHiggs/benchmark_planes/$benchmark_plane

read mC mH tb BR_C_HW BR_H_tata <<< `awk -v n=$(($PBS_ARRAY_INDEX + 1)) \
                'FNR == n {print $3, $1, $4, $11, $13}' $benchmark_plane_path` 

bp_dirname=mC\_$mC\_tb_$tb
target_dir=/rsgrps/shufang/Events/$proc_name/$bp_dirname
input_list=$proc_name\_$bp_dirname\_input_list.txt

ls -f $target_dir/*.root > $input_list
read Zd Ze <<< `./analyze $proc_name\_$bp_dirname $mC $mH $tb $BR_C_HW $BR_H_tata $proc_name`
echo $mC $mH $tb $Zd $Ze >> $proc_name"_significances.txt"
rm $input_list

rm default/weights/TMVAClassification_$proc_name\_mC_$mC\_mH_$mH\_tb_$tb\_BDTG.*
