import os
import subprocess
import numpy as np
import pandas as pd
import time as clock
pd.set_option('mode.chained_assignment', None)

import sortasurvey
from sortasurvey import utils
from sortasurvey.survey import Survey
from sortasurvey.sample import Sample


def rank(args, stuck=0):
    """
    Initializes the Survey class and runs the ranking algorithm to determine
    a final prioritized list of targets while balancing various sub-science 
    goals using the provided selection criteria and prioritization metrics. 
    The selection process will continue until either:
    1) the allocated survey time is successfully exhausted (i.e. == 0), or 
    2) all programs in the survey are 'stuck' (i.e. cannot afford their next highest priority pick).

    Parameters
    ----------
    args : argparse.Namespace
        the command line arguments
    stuck : int
        the number of programs currently 'stuck' in the Survey. This variable resets to 0 any time a new selection is made

    """

    # init Survey class
    survey = Survey(args)
    ti = clock.time()
    # Monte-Carlo simulations of sampler (args.iter=1 by default)
    for n in range(1,args.iter+1):
        survey.n = n
        survey.reset_track()
        # Begin selection process 
        while np.sum(survey.sciences.remaining_hours.values.tolist()) > 0.:
            # Select program
            program = utils.pick_program(survey.sciences)
            # Create an instance of the Sample class w/ the updated vetted sample
            sample = Sample(program, survey=survey)
            # Only continue if the selected program has targets left
            if not survey.sciences.loc[program,'n_targets_left']:
                continue
            # pick highest priority target not yet selected
            pick = sample.get_highest_priority()
            if pick is None:
                continue
            # what is the cost of the selected target
            cost = float((pick.actual_cost))/3600.
            # if the program cannot afford the target, it is "stuck"
            if cost > survey.sciences.loc[program,'remaining_hours']:
                stuck += 1
            else:
                # reset counter
                stuck = 0
                # update records with the program pick
                survey.update(pick, program)
            if stuck >= len(survey.sciences):
                break
        if survey.emcee:
            survey.df = survey.candidates.copy()
            utils.make_data_products(survey)

    tf = clock.time()
    survey.ranking_time = float(tf-ti)
    survey.df = survey.candidates.copy()
    utils.make_data_products(survey)


def setup(args, note='', source='https://raw.githubusercontent.com/ashleychontos/sort-a-survey/main/examples/'):
    """
    Running this after installation will create the appropriate directories in the current working
    directory as well as download example files to test your installation.

    Parameters
    ----------
    args : argparse.Namespace
        the command line arguments
    note : Optional[str]
        suppressed verbose output
    source : Optional[str]
        source directory to download example files to test your installation

    """
    print('\nDownloading relevant data from source directory:')
    note+='\n\nNB:\n'
    # create info directory
    if not os.path.exists(args.inpdir):
        os.mkdir(args.inpdir)
        note+=' - created input file directory: %s \n'%args.inpdir

    # get example TKS input files
    for file in ['TKS_sample.csv', 'high_priority.csv', 'no_no.csv', 'survey_info.csv']:
        infile='%sinfo/%s'%(source,file)
        outfile=os.path.join(args.inpdir,file)
        subprocess.call(['curl %s > %s'%(infile, outfile)], shell=True)

    # create results directory
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)
    note+=' - results will be saved to %s \n\n'%args.outdir

    if args.notebook:
        infile='%sTKS.ipynb'%source
        outfile=os.path.join(os.path.abspath(os.getcwd()),'TKS.ipynb')
        subprocess.call(['curl %s > %s'%(infile, outfile)], shell=True)

    if args.verbose:
        print(note)