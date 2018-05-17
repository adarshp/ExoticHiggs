# sh setupAnalysis.sh
# qsub -J 1-$((`wc -l ../benchmark_planes/BP_IIB_mC_mH.txt | awk '{print $1}'` - 1)) mC_mH_analysis.sh
# qsub -J 1-$((`wc -l ../benchmark_planes/BP_IIB_mC_deltaM.txt | awk '{print $1}'` - 1)) mC_deltaM_analysis.sh
qsub -J 1-$((`wc -l ../benchmark_planes/BP_IIB_mC_tb.txt | awk '{print $1}'` - 1)) mC_tb_analysis.sh
