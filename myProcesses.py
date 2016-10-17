from ExoticHiggs.Process import Process
from ExoticHiggs.SignalProcess import TwoHiggsDoubletModelProcess
from ExoticHiggs.helpers import get_benchmark_points

# Get benchmark points from a text file
BP_IA = get_benchmark_points('benchmark_planes/BP_IA.txt')

# Define a collection of signal processes corresponding to the
# Benchmark point

A_HZ_bbll_14_TeV_collection = [TwoHiggsDoubletModelProcess(
        name = 'A_HZ',
        decay_channel = 'bbll',
        mg5_generation_syntax = """\
        generate g g > h3 , ( h3 > h2 z , h2 > b b~ , z > l+ l- )""",
        energy = 14,
        benchmark_point = bp,
    ) for bp in BP_IA]

# Define a collection of background processes
tt_bbll_14_TeV_collection = [Process(
        name = 'tt',
        model = 'sm',
        decay_channel = 'bbll',
        mg5_generation_syntax = """\
        generate p p > t t~, (t > w+ b, w+ > l+ vl), (t~ > w- b~, w- > l- vl~)""",
        energy = 14,
        index = index,
    ) for index in range(0,30)]
