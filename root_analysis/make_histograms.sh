for background in tttautau-full tttautau-semi ttll-full ttlv-full; do
    ./make_histograms $background
done
python make_histograms.py
