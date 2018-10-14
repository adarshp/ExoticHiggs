bg_names=tttautau

for bg_name in $bg_names; do
    target_dir=/rsgrps/shufang/Events/$bg_name
    n_existing=`ls $target_dir | wc -l`
    n_new=5
    qsub -N $bg_name\_gen -J $(($n_existing + 1))-$(($n_existing + $n_new)) \
                          -v bg_name=$bg_name generate_bg_events.pbs
done
