import ExoticHiggs
from ExoticHiggs.Process import Process
from ExoticHiggs.SignalProcess import TwoHiggsDoubletModelProcess
from myBenchmarkPlanes import BP_IA

A_HZ_bbll_14_TeV_collection = [TwoHiggsDoubletModelProcess(
        name = 'A_HZ',
        decay_channel = 'bbll',
        mg5_generation_syntax = """\
        generate g g > h3 , ( h3 > h2 z , h2 > b b~ , z > l+ l- )""",
        energy = 14,
        benchmark_point = bp,
    ) for bp in BP_IA]

tt_bbll_14_TeV_collection = [Process(
        name = 'tt',
        model = 'sm',
        decay_channel = 'bbll',
        mg5_generation_syntax = """\
        generate p p > t t~, (t > w+ b, w+ > l+ vl), (t~ > w- b~, w- > l- vl~)""",
        energy = 14,
        index = index,
    ) for index in range(0,30)]
