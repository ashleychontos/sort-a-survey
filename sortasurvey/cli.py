import argparse


import sortasurvey
from sortasurvey import pipeline


def main():

    parser = argparse.ArgumentParser(description="sort-a-survey: automated, optimizable and reproducible target selection")

    parser.add_argument('-hpn', '--hpn', '-hours', '--hours', '-hourspernight', '--hourspernight',
                        dest='hours',
                        type=float,
                        default=10.,
                        help="Number of hours per night. (default=10)",
                        )
    parser.add_argument('-night', '--night', '-pool', '--pool',  '-nights', '--nights',
                        dest='nights',
                        type=float,
                        default=50.,
                        help="Total number of allocated nights for survey.",
                        )
    parser.add_argument('-info', '--info', '-survey', '--survey',
                        dest='path_survey',
                        help='Path to csv containing survey information',
                        type=str,
                        default='info/survey_info.csv',
    )
    parser.add_argument('-iter', '--iter', '-step', '--step', '-iterations', '--iterations', '-steps', '--steps', 
                        dest='iter', 
                        help='Number of selection process iterations (default=1)',
                        default=1, 
                        type=int,
    )
    parser.add_argument('-no', '--no', '-nono', '--nono', '-ignore', '--ignore',
                        dest='path_ignore',
                        help='Path to save results to',
                        default='info/no_no.csv',
                        type=str,
    )
    parser.add_argument('-out', '--out', '-outdir', '--outdir', '-output', '--output',
                        dest='outdir',
                        help='Path to save results to',
                        default='results/',
                        type=str,
    )
    parser.add_argument('-prio', '--prio', '-priority', '--priority',
                        dest='path_priority',
                        help='Path to main planet sample to select from',
                        default='info/high_priority.csv', 
                        type=str,
    )
    parser.add_argument('-prog', '--prog', '-progress', '--progress',
                        dest='progress',
                        help='Turn off progress bar (default=True). Only activates for > 1 iteration',
                        default=True, 
                        action='store_false',
    )
    parser.add_argument('-sample', '--sample','-samples', '--samples',
                        dest='path_sample',
                        help='Path to main planet sample to select from',
                        default='info/TOIs_perfect.csv', 
                        type=str,
    )
    parser.add_argument('-save', '--save', 
                        dest='save',
                        help='Turn off the saving of output data products and figures (default=True)',
                        default=True, 
                        action='store_false',
    )
    parser.add_argument('-show', '--show',
                        dest='show',
                        help='Show output figures (default=False)',
                        default=False, 
                        action='store_true',
    )
    parser.add_argument('-sp', '--sp', '-special', '--special',
                        dest='special',
                        help='For TKS, this is for a more complicated, 2D selection process',
                        nargs='*',
                        type=str,
                        default=None,
                        )
    parser.add_argument('-verbose', '--verbose',
                        dest='verbose',
                        help='Turn off verbose output (default=False)',
                        default=True, 
                        action='store_false',
    )

    parser.set_defaults(func=pipeline.main)

    args = parser.parse_args()
    args.func(args)



if __name__ == '__main__':

    main()