.. _quickstart:

Getting Started
###############

.. _installation:

Installation
************

Install ``sortasurvey`` using pip:

.. code-block:: bash

    $ pip install sortasurvey

The ``survey`` binary should have been automatically placed in your system's path by the
``pip`` command. If your system can not find the ``survey`` executable, ``cd`` into the 
top-level ``sortasurvey`` directory and try running the following command:

.. code-block:: bash

    $ python setup.py install

You may test your installation by using ``survey --help`` to see available command-line options:

.. code-block:: bash
		
    $ survey --help
    usage: sort-a-survey [-h] [-version] {setup,rank} ...

    sort-a-survey: automated, optimizable and reproducible target selection

    optional arguments:
      -h, --help           show this help message and exit
      -version, --version  Print version number and exit.

    subcommands:
      {setup,rank}
        setup              Easy setup for directories and files
        rank               Rank targets for a given survey
    
