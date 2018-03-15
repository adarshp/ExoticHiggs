qsub -J 1-$((`wc -l benchmark_planes/BP_IIB_tb_1.5.txt | awk '{print $1}'` - 1)) generation_script.pbs
