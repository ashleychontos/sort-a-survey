#!/usr/local/bin/python3

import numpy as np
import pandas as pd
import time as clock
pd.set_option('mode.chained_assignment', None)


from survey import Survey
from sample import Sample
import utils


def main(args, stuck=0):

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

    tf = clock.time()
    survey.ranking_time = float(tf-ti)
    utils.make_data_products(survey)
