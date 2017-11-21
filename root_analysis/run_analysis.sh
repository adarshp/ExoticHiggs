make
processes="Signal tt_full tt_semi"
for p in $processes; do
    rm -rf $p
    mkdir -p $p/histo_data
    ./main $p
done
