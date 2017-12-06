processes="tt_fully_leptonic_including_taus tt_semileptonic_including_taus"
for p in $processes; do
    ls -f /rsgrps/shufang/Events/$p/*.root > $p\_input_list.txt
done
ls -f /rsgrps/shufang/Events/charged_higgs/*.root > Signal_input_list.txt
