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
    usage: survey [-h] [-hpn HOURS] [-night NIGHTS] [-info PATH_SURVEY]
                  [-iter ITER] [-no PATH_IGNORE] [-out OUTDIR]
                  [-prio PATH_PRIORITY] [-prog] [-sample PATH_SAMPLE] [-save]
                  [-show] [-sp [SPECIAL [SPECIAL ...]]] [-verbose]

    sort-a-survey: automated, optimizable and reproducible target selection

    optional arguments:
      -h, --help            show this help message and exit
      -hpn HOURS, --hpn HOURS, -hours HOURS, --hours HOURS, -hourspernight HOURS, --hourspernight HOURS
                        Number of hours per night. (default=10)
      -night NIGHTS, --night NIGHTS, -pool NIGHTS, --pool NIGHTS, -nights NIGHTS, --nights NIGHTS
                        Total number of allocated nights for survey.
      -info PATH_SURVEY, --info PATH_SURVEY, -survey PATH_SURVEY, --survey PATH_SURVEY
                        Path to csv containing survey information
      -iter ITER, --iter ITER, -step ITER, --step ITER, -iterations ITER, --iterations ITER, -steps ITER, --steps ITER
                        Number of selection process iterations (default=1)
      -no PATH_IGNORE, --no PATH_IGNORE, -nono PATH_IGNORE, --nono PATH_IGNORE, -ignore PATH_IGNORE, --ignore PATH_IGNORE
                        Path to save results to
      -out OUTDIR, --out OUTDIR, -outdir OUTDIR, --outdir OUTDIR, -output OUTDIR, --output OUTDIR
                        Path to save results to
      -prio PATH_PRIORITY, --prio PATH_PRIORITY, -priority PATH_PRIORITY, --priority PATH_PRIORITY
                        Path to main planet sample to select from
      -prog, --prog, -progress, --progress
                        Turn off progress bar (default=True). Only activates
                        for > 1 iteration
      -sample PATH_SAMPLE, --sample PATH_SAMPLE, -samples PATH_SAMPLE, --samples PATH_SAMPLE
                        Path to main planet sample to select from
      -save, --save         Turn off the saving of output data products and
                        figures (default=True)
      -show, --show         Show output figures (default=False)
      -sp [SPECIAL [SPECIAL ...]], --sp [SPECIAL [SPECIAL ...]], -special [SPECIAL [SPECIAL ...]], --special [SPECIAL [SPECIAL ...]]
                        For TKS, this is for a more complicated, 2D selection
                        process
      -verbose, --verbose   Turn off verbose output (default=False)
    
