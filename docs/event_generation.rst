Event Generation
================

Here is a primer on event generation using this package.

Creating MG5 directories
-------------------------------

Here is an example of how to generate the following signal process at 14 TeV:

.. math::
  gg \rightarrow A \rightarrow HZ \rightarrow bbll

The primary backgrounds for this process are :math:`t\overline{t}` with a fully
leptonic decay chain, and :math:`Zbb`, with the Z boson decaying leptonically.

The points that represent the benchmark plane we are investigating reside in
the file ``benchmark_planes/BP_IA.txt``. To create the MadGraph directories
corresponding to them, you can do the following::

    from ExoticHiggs.Process import Process
    from ExoticHiggs.SignalProcess import TwoHiggsDoubletModelProcess
    from ExoticHiggs.helpers import get_benchmark_points
    from tqdm import tqdm

    # Get benchmark points from a text file
    BP_IA = get_benchmark_points('benchmark_planes/BP_IA.txt')

    # Make a list of signal processes corresponding to the
    # benchmark points

    A_HZ_bbll_14_TeV_collection = [TwoHiggsDoubletModelProcess(
            name = 'A_HZ', # Name of the Exotic Higgs decay process
            decay_channel = 'bbll', # Final state
            mg5_generation_syntax = """\
            generate g g > h3 , ( h3 > h2 z , h2 > b b~ , z > l+ l- )""",
            energy = 14, # Energy in TeV
            benchmark_point = bp,
        ) for bp in BP_IA]

    # Create the MadGraph output directories
    for process in tqdm(A_HZ_bbll_14_TeV_collection, 
                        desc = "Creating MG5 process directories"):
        process.create_directory()

This will create directories of the form ``Events/Signals/A_HZ/bbll/14_TeV/mA_300_tb_1``.

For background events, you need do something a bit different. For example, for the process
.. math::
   pp \rightarrow t\overline{t} \rightarrow W^+bW^-\overline{b}\rightarrow bbll\nu\nu

You would define the collection as follows::
    tt_bbll_14_TeV_collection = [Process(
        name = 'tt',
        model = 'sm',
        decay_channel = 'bbll',
        mg5_generation_syntax = """\
        generate p p > t t~, (t > w+ b, w+ > l+ vl), (t~ > w- b~, w- > l- vl~)""",
        energy = 14,
        index = index,
    ) for index in range(0,30)]

Here, we create thirty copies of the background process - since we will need a much
larger number of simulated background events - we will independently generate
events on thirty nodes on the cluster at once.

Generating signal events
------------------------

Once the event directories have been created, you can submit event generation jobs
to the cluster as follows::

  for process in tqdm(A_HZ_bbll_14_TeV_collection, 
                        desc = "Submitting jobs to the cluster"):
        process.generate_events(nruns = 5, nevents = 50000)

The above command will perform five runs in the process directory, each with 
50,000 events.

To generate events locally instead, you can do the following::
  process.generate_events_locally(nruns = 5, nevents = 50000)

It is recommended not to go beyond 50,000 events per run, due to issues with Pythia.

.. toctree::
    :maxdepth: 2

