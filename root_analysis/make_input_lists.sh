processes="tttautau"
for p in $processes; do
    ls -f /rsgrps/shufang/Events/$p/*.root > $p\_input_list.txt
done
