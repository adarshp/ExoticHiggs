Contributing
============

Version control
---------------

Contributions are welcome and encouraged. The project uses `git`_ for version
control, and is hosted on `Github`_. For a git primer, you can check out this
`interactive tutorial`_ on Codeacademy. You may also find this introduction to
the `feature branch workflow`_ useful to get an idea of the 'big picture' behind
distributed version control.

Writing documentation
---------------------

A crucial part of any software project is, of course, the documentation (hey,
that's what you're reading!). This project uses `Sphinx`_ to generate 
documentation, including API documentation from Python docstrings.

The documentation source resides in the ``sphinx/source`` directory. The
command::

    make livehtml

generates HTML versions of the documentation that you can preview at 
http://127.0.0.1:8000. Once you are satisfied with the result, you can run
the script ``update_docs.sh`` to push your changes and have them be visible at
https://adarshp.github.io/ExoticHiggs/. For consistency, please use `Numpy-style
docstrings`_ to document your classes, methods, functions, etc.

.. toctree::
   :maxdepth: 2


.. _Numpy-style docstrings: https://github.com/numpy/numpy/blob/master/doc/example.py
.. _Sphinx: http://www.sphinx-doc.org/en/stable/
.. _Github: https://github.com
.. _git: https://git-scm.com
.. _interactive tutorial:  https://www.codecademy.com/learn/learn-git
.. _feature branch workflow: https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow
