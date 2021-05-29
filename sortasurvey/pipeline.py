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

    # init Survey class
    survey = Survey(args)
    ti = clock.time()
    # Monte-Carlo simulations of sampler (args.iter=1 by default)
    for n in range(1,args.iter+1):
        survey.n = n
        survey.reset_track()
        # Begin selection process and continue while the total remaining 
        # time allocation is greater than zero
        while np.sum(survey.sciences.remaining_hours.values.tolist()) > 0.:
            # Select program
            program = utils.pick_program(survey.sciences)
            # Create an instance åof the Sample class w/ the updated vetted sample
            sample = Sample(program, survey=survey)
            # Only continue if the selected program has targets left
            if not survey.sciences.loc[program,'n_targets_left']:
                continue
            if program in survey.special:
                survey.get_2D_filter(program)
            # pick highest priority target not yet selected
            pick = sample.get_highest_priority()
            # what is the cost of the selected target
            cost = float((pick.actual_cost))/3600.
            # if the program cannot afford the target, it is "stuck"
            if cost > survey.sciences.loc[program,'remaining_hours']:
                if program in survey.special:
                    survey.special[program]['stuck'] += 1
                stuck += 1
            else:
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


def setup(args, note='', source='https://raw.githubusercontent.com/ashleychontos/sort-a-survey/main/info/'):
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

    note+='\n\nDownloading relevant data from source directory:\n'
    # create info directory
    if not os.path.exists(args.inpdir):
        os.mkdir(args.inpdir)
        note+=' - created input file directory: %s \n'%args.inpdir

    # get example TKS input files
    for file in ['TOIs_perfect.csv', 'high_priority.csv', 'no_no.csv', 'survey_info.csv']:
        infile='%s%s'%(source,file)
        outfile='%s%s'%(args.inpdir,file)
        subprocess.call(['curl %s > %s'%(infile, outfile)], shell=True)

    # create results directory
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)
    note+=' - results will be saved to %s \n\n'%args.outdir
    
    if args.verbose:
        print(note)