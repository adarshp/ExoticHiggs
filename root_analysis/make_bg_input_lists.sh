backgrounds="tttautau-full tttautau-semi ttll-full ttlv-full"

for b in $backgrounds; do
    ls -f /rsgrps/shufang/Events/$b/*.root > $b\_input_list.txt
done
