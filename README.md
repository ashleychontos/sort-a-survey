# sort-a-survey:
hands-off target selection for large astronomical surveys

## Installation

Install `sortasurvey` using pip:

```
$ pip install sortasurvey
```   

The `survey` binary should have been automatically placed in your system's path by the
command. If your system can not find the `survey` executable, `cd` into the 
top-level `sortasurvey` directory and try running the following command:

```
$ python setup.py install
```

You may test your installation by using `survey --help` to see available command-line options:

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

## Acknowledgements

### *We recognize and acknowledge the cultural role and reverence that the summit of Maunakea has within the indigenous Hawaiian community. We are deeply grateful to have the opportunity to conduct observations from this mountain.*

We thank all the observers who have spent time collecting data over the many years on Keck/HIRES. We gratefully acknowledge 
the efforts and dedication of the Keck Observatory staff for support of HIRES and remote observing. We thank Ken and Gloria 
Levy, who supported the construction of the Levy Spectrometer on the Automated Planet Finder. We thank the University of 
California and Google for supporting Lick Observatory and the UCO staff for their dedicated work scheduling and operating 
the telescopes of Lick Observatory.

We are grateful to the time assignment committees of the University of California, University of Hawai'i, the California 
Institute of Technology, and NASA for supporting the TESS-Keck Survey with observing time at Keck Observatory and on the 
Automated Planet Finder. We thank NASA for funding associated with our Key Strategic Mission Support project. 
