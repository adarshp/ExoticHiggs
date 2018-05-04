qsub -J 1-$((`wc -l benchmark_planes/BP_IIB_mC_mH.txt | awk '{print $1}'` - 1)) generate_mC_mH_events.pbs
# qsub -J 1-$((`wc -l benchmark_planes/BP_IIB_mC_deltaM.txt | awk '{print $1}'` - 1)) generate_mC_deltaM_events.pbs
qsub -J 1-$((`wc -l benchmark_planes/BP_IIB_mC_tb.txt | awk '{print $1}'` - 1)) generate_mC_tb_events.pbs
