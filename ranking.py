#!/usr/local/bin/python3

import numpy as np
import pandas as pd
import time as clock
from tqdm import tqdm
from argparse import ArgumentParser
from survey import Survey
from sample import Sample
from track import Track
from utils import *
pd.set_option('mode.chained_assignment', None)


def main(args):

    TKS = ranking_scheme(args)
#    data = DataProducts(TKS)
#    data.get_stats()

    return


##########################################################################################
#                                                                                        #
#                                MAIN RANKING ALGORITHM                                  #
#                                                                                        #
##########################################################################################


def ranking_scheme(args):

    # initiate Survey class
    # contains survey science information and vetted sample
    TKS = Survey(args)
    print(TKS.sciences)
    # initiate Track object that logs the history of the 
    # sampling process by saving each iteration
    hist = Track(args)
    print(hist)
    print(hist.track)

    # Monte-Carlo simulations of sampler (args.mciter=1 by default)
    for n in tqdm(range(args.mciter)):

        # Reset time allocations and survey sample for each iteration 
        # by making copies of the Survey programs and sample
        TKS = track.reset_track(TKS)
        TKS.init_2D_filters()
        # Set seed for reproducibility (array has length of 1000)
        np.random.seed(TKS.seeds[n])

        # Begin selection process and continue while the total remaining 
        # time allocation is greater than zero
        while np.sum(TKS.sciences.remaining_hours.values.tolist()) > 0.:

            # Select program
            program = pick_program(TKS.sciences)

            # Only continue if the selected program has targets left
            if not TKS.sciences.loc[program, "n_targets_left"]:
                continue
            stuck = False
            if program == 'SC1B':
                TKS.get_2D_filter()
            # Create an instance of the Sample class filtered by the selection 
            # criteria specified by the selected Survey program
            sample = Sample(survey=TKS,science=program)

            # pick highest priority target not yet selected
            pick = sample.get_highest_priority()
            # what is the cost of the selected target
            cost = float((pick.actual_cost))/3600.
            # if the program cannot afford the target, it is "stuck"
            if cost > TKS.sciences.loc[program, 'remaining_hours']:
                if program == 'SC1B':
                    TKS.sc1b_npick += 1
                stuck = True
            # update the 
            TKS = track.update(pick, program, TKS, stuck)
            if TKS.stuck >= len(TKS.sciences):
                break

        TKS.n += 1

    tf = clock.time()
    TKS.ranking_time = float(tf-ti)
    TKS.df = TKS.candidates

    return TKS


##########################################################################################
#                                                                                        #
#                                         INIT                                           #
#                                                                                        #
##########################################################################################


if __name__ == '__main__':

    parser = ArgumentParser(
           description = 'This is the TKS target selection function given a population of targets.', 
           prog = 'Automated Survey Target Selection'
           )
    parser.add_argument('-hpn', '--hpn', '-hours', '--hours', '-hourspernight', '--hourspernight',
                        dest='hours',
                        type=int,
                        default=10,
                        help="Number of hours per night. (default=10)",
                        )
    parser.add_argument('-n', '--n', '-night', '--night', '-nights', '--nights',
                        dest='nights',
                        type=int,
                        default=50,
                        help="Total number of allocated nights for survey.",
                        )
    parser.add_argument('-mc', '--mc', '-mciter', '--mciter', '-mc_iter', '--mc_iter',
                        dest='mciter',
                        type=int,
                        default=1,
                        help="Number of iterations to run (default=1).",
                        )
    parser.add_argument('-s', '--s', '-save', '--save',
                        dest='save',
                        action='store_false',
                        default=True,
                        help="Do not save program outputs.",
                        )
    parser.add_argument('-v', '--v', '-verbose', '--verbose',
                        dest='verbose', 
                        action = 'store_true',
                        help="Verbose output.",
                        )

    main(parser.parse_args())