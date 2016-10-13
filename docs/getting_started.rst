Getting started
===============

The first step in the pheno analysis pipeline is to identify a promising search
channel. A few promising channels and benchmark planes have been proposed in
the paper `Anatomy of Exotic Higgs Decays in 2HDM`_.

1. Prerequisites:
  - Python 2.7 (not 3.x)
  - ROOT

2. Installation:

If you are installing on your local machine, go ahead and do the following::

    git clone https://github.com/adarshp/ExoticHiggs
    cd ExoticHiggs
    make

If you are installing on the cluster, there are a few :doc:`extra steps </cluster_issues>` 
you need to do before doing the above.

Notes
-----

#. The script :mod:`setup` does not install the latest version of MadGraph5, 
   instead, it installs v2.2.3. The reason is that the newer versions have a
   problem with high widths of the `A`. When prompted to update to the newest
   version of MadGraph, select 'no'.

.. toctree::
  :maxdepth: 2

.. _Anatomy of Exotic Higgs Decays in 2HDM: https://arxiv.org/abs/1604.01406
