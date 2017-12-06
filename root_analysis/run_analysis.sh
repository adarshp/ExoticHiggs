make
processes="Signal tt_fully_leptonic_including_taus tt_semileptonic_including_taus"
for p in $processes; do
    rm -rf $p
    mkdir -p $p/histo_data
    ./main $p
done
