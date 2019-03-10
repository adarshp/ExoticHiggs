# Create MG5 directories for the src project

# processes='tt_fully_leptonic_including_taus charged_higgs tt_semileptonic_including_taus'
processes='charged_higgs'
src=`pwd`

target_dir='/xdisk/adarsh/'
mg5='/home/u13/adarsh/MG5_aMC_v2_6_0/bin/mg5_aMC'

cd $target_dir

for process in $processes
do
    rm -rf $process
    $mg5 $src/Cards/mg5_proc_cards/$process'.dat'
    cd $process/Cards; rm delphes_card* mad* pgs* plot* ; cd ../../
    cp $src/Cards/delphes_cards/delphes_card_with_top_tagging.tcl $process/Cards/delphes_card.dat
    cp $src/Cards/run_cards/run_card.dat $process/Cards/run_card.dat
done

cd $src
