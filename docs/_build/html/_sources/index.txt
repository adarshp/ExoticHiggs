.. ExoticHiggs documentation master file, created by
   sphinx-quickstart on Fri Oct  7 16:16:54 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Exotic Higgses at 14 and 100 TeV
================================

Welcome to the documentation for the Exotic Higgs project. With this project
we aim to characterize the reach attainable at the LHC and a future 100 TeV
proton-proton collider for exotic Higgses in the Two-Higgs Doublet Model.

The first step in the pheno analysis pipeline is to identify a promising search
channel. A few promising channels and benchmark planes have been proposed in
the paper `Anatomy of Exotic Higgs Decays in 2HDM`_. The next step is to
simulate what we would see at a particle collider. This package provides an
interface to MadGraph5, Pythia and Delphes that you can use to set up large-
scale event generation on a cluster. The option to generate events locally is
also present.

**Table of Contents**

.. toctree::
    :maxdepth: 2

    getting_started
    event_generation
    cluster_issues
    contributing
    API documentation <ExoticHiggs>

**Indices**

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Anatomy of Exotic Higgs Decays in 2HDM: https://arxiv.org/abs/1604.01406
