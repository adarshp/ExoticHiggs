qsub -J 1-$((`wc -l benchmark_planes/BP_IIB_tb_1.5.txt | awk '{print $1}'` - 1)) generate_mC_mH_plane_events.pbs
qsub -J 1-$((`wc -l benchmark_planes/BP_IIB_deltaM200.txt | awk '{print $1}'` - 1)) generate_mC_tb_delta_M_200_events.pbs
