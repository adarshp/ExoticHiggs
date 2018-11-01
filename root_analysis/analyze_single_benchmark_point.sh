#!/bin/bash
#PBS -M adarsh@email.arizona.edu
#PBS -W group_list=shufang
#PBS -q windfall
#PBS -l select=1:ncpus=1:mem=2gb
#PBS -l place=free:shared
#PBS -l cput=1:0:0
#PBS -l walltime=3:0:0


# For single job:
# ====================
PBS_ARRAY_INDEX=100
param_combination=mC_mH
# ====================

project_dir=$HOME/ExoticHiggs
benchmark_plane_dir=$project_dir/benchmark_planes
events_dir=/rsgrps/shufang/Events

parent_process=C_HW
decay_channel=tataW

dataset=$parent_process\_$decay_channel\_$param_combination
benchmark_plane=BP_IIB

benchmark_points=$benchmark_plane_dir/$benchmark_plane\_$param_combination".txt"

cd $project_dir/root_analysis

read mC mH tb BR_C_HW BR_H_tata <<< `awk -v n=$(($PBS_ARRAY_INDEX + 1)) \
                'FNR == n {print $3, $1, $4, $11, $13}' $benchmark_points` 

bp_dirname=mC\_$mC\_mH_$mH\_tb_$tb
echo $bp_dirname
target_dir=$events_dir/$dataset/$bp_dirname
input_list=$dataset\_$bp_dirname\_input_list.txt

ls -f $target_dir/*.root > $input_list
./analyze $dataset\_$bp_dirname $mC $mH $tb $BR_C_HW $BR_H_tata $dataset
# read Zd Ze <<< `./analyze $dataset\_$bp_dirname $mC $mH $tb $BR_C_HW $BR_H_tata $dataset`
intermediate_result_dir=intermediate_analysis_results/$param_combination
mkdir -p $intermediate_result_dir 
intermediate_result_file=$intermediate_result_dir/$bp_dirname"_significances.txt"
echo $mC $mH $tb $Zd $Ze
rm $input_list

rm default/weights/TMVAClassification_$dataset\_$bp_dirname\_BDTG.*
