# Generate one run for each of the backgrounds in bg_names

bg_names="tttautau-semi ttautau-full ttll-full ttlv-full"

for bg_name in $bg_names; do
    qsub -N $bg_name -v bg_name=$bg_name single_bg_run.pbs
done
