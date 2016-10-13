Event Generation
================

Here is a primer on event generation using this package.

Creating MG5 signal directories
-------------------------------

The default process in the :mod:`create_mg5_directories` module is:

.. math::
  gg \rightarrow A \rightarrow HZ \rightarrow bbll

The primary backgrounds for this process are :math:`t\overline{t}` with a fully
leptonic decay chain, and :math:`Zbb`, with the Z boson decaying leptonically.

The points that represent the benchmark plane we are investigating reside in
the file ``allpoints.txt``. To create the MadGraph5 directories corresponding
to the benchmark plane, all one has to do is run ``./create_mg5_directories.py``. 
This creates MG5 process directories in the directory ``Events/Signals/A_HZ``.

To create MG5 directories for the other signals with the associated benchmark
planes, all one has to do is to add a class similar to :class:`A_HZ`. For
example, if you wanted to create output directories for the process 
:math:`A\rightarrow hZ` and the benchmark plane points contained in a file
named ``BP2.txt``, you would add the following to the end of the file
``myProcesses.py``::

    class A_hZ(SignalProcess):
        def __init__(self, *args, **kwargs):
            self.name = 'A_hZ'
            SignalProcess.__init__(self, *args, **kwargs)
            self.mg5_generation_syntax = """\
            generate g g > h3, (h3 > h1 z, h2 > b b~, z > l+ l-) 
            """

and the following to the the top of :mod:`create_mg5_directories` (after the
other ``import`` statements):: 

  from myProcesses import A_hZ

and the following in the ``main()`` function of :mod:`create_mg5_directories`::

  A_hZ_signals = define_signals(A_hZ, 'BP2.txt')
  create_mg5_dirs(A_hZ_signals)

After doing the above, you can run ``./create_mg5_directories.py`` from the
command line once more to create signal directories corresponding to the
processes :math:`A \rightarrow hZ` and the benchmark points in ``BP2.txt``.

Generating signal events
------------------------

If you created the MadGraph output directories on your local computer, then you 
can add the following line to the top of :mod:`generate_events` (similar to 
what we did for :mod:`create_mg5_directories`::

  from myProcesses import A_hZ

and in the ``main()`` function you can insert the lines::

  A_hZ_signals = define_signals(A_hZ, 'BP2.txt')
  for signal in tqdm(A_hZ_signals, desc='Generating events locally'):
      signal.generate_events_locally()

By default, this generates 50,000 events for each benchmark point, with
a center-of-mass energy of 14 TeV. This can be changed by the user. For example, 
to generate 10,000 events for each benchmark point, you can do::
  signal.generate_events_locally(nevents = 10000, ebeam = 50000)

(``ebeam`` is the energy of each colliding beam in GeV, and ``nevents`` is the
number of events we would like to generate for the run. It is recommended not
to go beyond 50,000 events per run, due to issues with Pythia.)


If you have set up the package on the University of Arizona :doc:`cluster </cluster_issues>`
instead,you would replace :meth:`~Process.Process.generate_events_locally()` with 
:meth:`~Process.Process.generate_events_on_cluster()`.

.. toctree::
    :maxdepth: 2

