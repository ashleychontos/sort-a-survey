# sort-a-survey
#### automated, optimizable & reproducible target selection algorithm for large astronomical surveys <br>
[![PyPI](https://badge.fury.io/py/sortasurvey.svg)](https://badge.fury.io/py/sortasurvey)

## Installation

Install `sortasurvey` using pip:

```
$ pip install sortasurvey
```   

The `survey` binary should have been automatically placed in your system's path by the
command. You can test your installation by using `survey --help` to see available command-line options:

```
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
```

## Quickstart

Once you've successfully installed the package, we suggest to create a new directory to keep all your survey-related stuff in one place. The software package provides a pretty convenient `setup` feature that we highly recommend. Therefore, to get started in your terminal type: 

```
$ mkdir survey
$ cd survey
$ survey setup
```
This last command will set up the proper directories and download a couple example files to get you started via command line. If jupyter notebook is more your thing, use the notebook option (via `-nb` `--nb` `-notebook` `--notebook`) with the setup command which will also download our notebook tutorial:

```
$ survey setup -nb
```

Please visit the [notebook tutorial](https://github.com/ashleychontos/sort-a-survey/blob/main/examples/TKS.ipynb) if you don't feel like running it but would like to take a peek (there are pretty plots in there, I promise). To run the software via command line, simply execute:

```
$ survey rank
```

The verbose command is `True` by default, which should show the following output if you ran the above line:

```
 ------------------------------
 -- prioritization  starting --
 ------------------------------

   - loading sample and survey science information
   - 785 targets make the standard survey cuts
   - 242 have also passed various vetting steps
   - ranking algorithm initialized using 50.0 nights (10.0 hr/n)
   - algorithm took 53 seconds to run
   - 86 targets were selected, containing a total of 103 planets
   - Making data products, including:
     - a copy of the updated sample
     - algorithm history (via ranking steps)
     - the final prioritized list (via observing priorities)
     - final costs saved
     - program overlap
     - txt file w/ run info

 ------------------------------
 ----- process - complete -----
 ------------------------------

Thu 06/10/21 12:54PM

Out of the 86 total targets:
  - SC1A has 31 targets
  - SC1B has 30 targets
  - SC1C has 6 targets
  - SC1D has 4 targets
  - SC1E has 4 targets
  - SC2A has 44 targets
  - SC2Bi has 5 targets
  - SC2Bii has 2 targets
  - SC2C has 4 targets
  - SC3 has 21 targets
  - SC4 has 16 targets
  - TOA has 86 targets
  - TOB has 8 targets

```

And now you have our TESS-Keck Survey sample, it's as simple as that! If you'd like to see plots of this sample and/or more descriptions of what this all means, please check out the [jupyter notebook](https://github.com/ashleychontos/sort-a-survey/blob/main/examples/TKS.ipynb) or the recent paper by Chontos+2021 that discusses this all in more detail.

## Features

Can't converge on a final target list? Do multiple science goals have you tripped up? Are you having a hard time balancing
several programs within a set allocation? Have several nights of observing coming up? 

**Let `sortasurvey` do the heavy lifting for you.**

Imagine a survey sample that can be:

- *Automated*
  - takes what would be an otherwise-complicated process and make it totally hands-off
- *Optimized*
  - can be ran many times with many different scenarios to create a sample that best fits your survey needs
- *Reproduced*
  - the randomized selection process and sample can be easily reproduced with our random seed feature
- *Tested*
  - Monte-carlo-like simulation capabilities to test how robust your survey sample is
- *Visualized*
  - creates helpful summary tables and stats

## Tutorial

Follow example in

- `sort-a-survey/examples/TKS.ipynb`

-------------------------------------------------------------------------------

The work presented here was motivated by the TESS-Keck Survey (TKS), a large, dedicated radial velocity program using 
over 100 nights on Keck/HIRES to study transiting planets identified by the [NASA TESS](https://tess.mit.edu) mission. 
TKS is a collaboration between researchers at the California Institute of Technology, the University of California, the
University of Hawai'i, the University of Kansas, NASA, the NASA Exoplanet Science Institute and the W. M. Keck Observatory.
Please visit [this](https://github.com/ashleychontos/tess-keck-survey) repo for more specific details on the application of
this algorithm to the final TKS sample.

## Attribution

Written by Ashley Chontos, with contributions from BJ Fulton, Erik Petigura, Joey Murphy, Ryan Rubenzahl, Sarah Blunt,
Corey Beard, Tara Fetherolf, and Judah van Zandt.

Please cite the [TKS paper] if you make 
use of this software or the TKS sample in your work.
