from collections import namedtuple

Process = namedtuple('Process', [ 
                                  'name',
                                  'model',
                                  'decay_channel',
                                  'process_type',
                                  'mg5_generation_syntax',
                                ])
A_HZ_bbll = Process(
        name = 'A_HZ',
        decay_channel = 'bbll',
        process_type = 'Signal',
        model = '2HDM_HEFT',
        mg5_generation_syntax = """\
        generate g g > h3 , ( h3 > h2 z , h2 > b b~ , z > l+ l- )""",
    )

tt_bbll = Process(
        name = 'tt',
        decay_channel = 'bbll',
        process_type = 'Background',
        model = 'sm',
        mg5_generation_syntax = """\
        generate p p > t t~, (t > w+ b, w+ > l+ vl), (t~ > w- b~, w- > l- vl~)""",
    )
