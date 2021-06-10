import argparse


import sortasurvey
from sortasurvey import pipeline
from sortasurvey import INPDIR, OUTDIR


def main():
    parser = argparse.ArgumentParser(
                                     description="sort-a-survey: automated, optimizable and reproducible target selection",
                                     prog="sort-a-survey",
    )
    parser.add_argument('-version', '--version',
                        action='version',
                        version="%(prog)s {}".format(sortasurvey.__version__),
                        help="Print version number and exit"
    )

    # In the parent parser, we define arguments and options common to all subcommands
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('-info', '--info', '-survey', '--survey',
                               dest='path_survey',
                               help='Path to csv containing survey information',
                               type=str,
                               default='%s/survey_info.csv'%INPDIR,
    )
    parent_parser.add_argument('-in', '--in', '-inpdir', '--inpdir', '-input', '--input',
                               dest='inpdir',
                               help='Path to survey information files and input',
                               default=INPDIR,
                               type=str,
    )
    parent_parser.add_argument('-no', '--no', '-nono', '--nono', '-ignore', '--ignore',
                               dest='path_ignore',
                               help='Path to save results to',
                               default='%s/no_no.csv'%INPDIR,
    )
    parent_parser.add_argument('-out', '--out', '-outdir', '--outdir', '-output', '--output',
                               dest='outdir',
                               help='Path to save results to',
                               default=OUTDIR,
                               type=str,
    )
    parent_parser.add_argument('-prio', '--prio', '-priority', '--priority',
                               dest='path_priority',
                               help='Path to main planet sample to select from',
                               default='%s/high_priority.csv'%INPDIR, 
    )
    parent_parser.add_argument('-sample', '--sample','-samples', '--samples',
                               dest='path_sample',
                               help='Path to main planet sample to select from',
                               default='%s/TKS_sample.csv'%INPDIR, 
                               type=str,
    )
    parent_parser.add_argument('-verbose', '--verbose',
                               dest='verbose',
                               help='Turn off verbose output (default=False)',
                               default=True, 
                               action='store_false',
    )

    sub_parser = parser.add_subparsers(title='Pipeline options:', dest='subcommand')

    # Setting up
    parser_setup = sub_parser.add_parser('setup', help='Easy setup for directories and files',
                                         parents=[parent_parser])
    parser_setup.set_defaults(func=pipeline.setup)

    # Run ranking algorith

    parser_run = sub_parser.add_parser('rank', help='Rank targets for a given survey', 
                                       parents=[parent_parser])
    parser_run.add_argument('-mc', '--mc', '-iter', '--iter', '-steps', '--steps', 
                            dest='iter', 
                            help='Number of selection process iterations (default=1)',
                            default=1, 
                            type=int,
    )
    parser_run.add_argument('-prog', '--prog', '-progress', '--progress',
                            dest='progress',
                            help='Turn off progress bar (default=True). Only activates for > 1 iteration',
                            default=True, 
                            action='store_false',
    )
    parser_run.add_argument('-hpn', '--hpn', '-hours', '--hours', '-hourspernight', '--hourspernight',
                            dest='hours',
                            type=float,
                            default=10.,
                            help="Number of hours per night. (default=10)",
    )
    parser_run.add_argument('-night', '--night', '-pool', '--pool',  '-nights', '--nights',
                            dest='nights',
                            type=float,
                            default=50.,
                            help="Total number of allocated nights for survey.",
    )
    parser_run.add_argument('-save', '--save', 
                            dest='save',
                            help='Turn off the saving of output data products and figures (default=True)',
                            default=True, 
                            action='store_false',
    )

    parser_run.set_defaults(func=pipeline.rank)

    args = parser.parse_args()
    args.func(args)



if __name__ == '__main__':

    main()