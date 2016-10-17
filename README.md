Exotic Higgs decays at 14 and 100 TeV
======================================

This is the Github repository for the ExoticHiggs project. Detailed documentation
can be found at http://exotichiggs.readthedocs.io

Right now, the package can be used to generate large numbers of events on a
cluster. (An option for local event generation is also available). In the
future, functionality will be added for analyzing these generated events.

Installation
------------

1. Prerequisites:
  - Python 2.7 (not 3.x)
  - [ROOT](https://root.cern.ch) 

2. If you are installing on your local machine, go ahead and do the following::

```
  git clone https://github.com/adarshp/ExoticHiggs
  cd ExoticHiggs
  make
```

For installation on the cluster, please refer to the 
[documentation](http://exotichiggs.readthedocs.io).

Notes
-----

The script `setup.py` does not install the latest version of MadGraph5, 
instead, it installs v2.2.3. The reason is that the newer versions have a
problem with high widths of the `A`. When prompted to update to the newest
version of MadGraph, select 'no'.
