Cluster Issues
==============

By generating events on a cluster rather than your local computer, you can 
harness the power of distributed computing to greatly speed up the time needed
to simulate huge numbers of events. However, there is no free lunch, it takes
a substantial time investment to get familiar with the workings of a cluster,
and set up event generation on it. This guide focuses on the University of
Arizona HTC (High throughput computing)/HPC (High performance computing) systems.

The `official website`_ of the HTC/HPC computing systems has a wealth of 
information about the architecture of the systems and how to use them. Here,
I will summarize what I think are the important things for us to know with
respect to running MadGraph on the cluster. Here is what you need to do to get
up and running with the cluster.

Getting started with the UA cluster
-----------------------------------

1. Get an HPC account by following the instructions `here`_.
2. You can log in to the HPC system by doing::

    ssh <username>@login.hpc.arizona.edu

The first time you do this, you might have to login using two-factor
authentication, that is, they will send a text to your phone with an access
code that you can use to log in. This get tedious after a while, so you should
create an RSA key pair on your computer, and copy the public key to the HPC
system. DigitalOcean_ has a nice guide for doing this, you can follow along up
to Step 3 (no need for step 4).

3. Add the following two lines to the file ``~/.bash_profile`` (create it if
it does not already exist)::
    
    module load git
    module load root

This will enable you to use git for version control, and save you from having
to install ROOT yourself :)

4. Install the anaconda_ Python 2.7 distribution in your home directory by doing
the following::
   
    cd /home/<username>
    wget https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh
    bash Anaconda2-4.2.0-Linux-x86_64.sh

5. The first place you will land in is ``/home/username``. This has 5 GB of
storage. We will need more, so we will set up shop in another directory,
namely ``/extra/username``, which has 200 GB of storage. Once you are in that 
directory, follow the instructions on the :doc:`home page </index>` to set up
the project environment.

6. You need to set your cluster configuration in the file ``ExoticHiggs/ClusterConfiguration.py``.
You can see :mod:`ClusterConfiguration` for a description of the various parameters.

.. _anaconda : https://www.continuum.io/downloads
.. _DigitalOcean : https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2
.. _here: http://rc.arizona.edu/hpc-htc/requesting-and-sponsoring-hpc-accounts-0#requestingu
.. _official website : http://rc.arizona.edu/hpc-htc/high-performance-computing-high-throughput-computing
