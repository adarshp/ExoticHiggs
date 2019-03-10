tttautau_bg_names="tttautau-full tttautau-semi"
ttll_ttlv_bg_names="ttll-full ttlv-full"

for bg_name in $tttautau_bg_names; do
    target_dir=/rsgrps/shufang/Events/$bg_name
    mkdir -p $target_dir
    n_existing=`ls $target_dir | wc -l`
    n_new=20
    qsub -N $bg_name\_gen -J $(($n_existing + 1))-$(($n_existing + $n_new)) \
                          -v bg_name=$bg_name generate_bg_events.pbs
done

for bg_name in $ttll_ttlv_bg_names; do
    target_dir=/rsgrps/shufang/Events/$bg_name
    mkdir -p $target_dir
    n_existing=`ls $target_dir | wc -l`
    n_new=2
    qsub -N $bg_name\_gen -J $(($n_existing + 1))-$(($n_existing + $n_new)) \
                          -v bg_name=$bg_name generate_bg_events.pbs
done
