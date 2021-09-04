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
    parent_parser.add_argument('--in', '--inpdir', '--input',
                               dest='inpdir',
                               help='Path to survey information files and input',
                               default=INPDIR,
                               type=str,
    )
    parent_parser.add_argument('--out', '--outdir', '--output',
                               dest='outdir',
                               help='Path to save results to',
                               default=OUTDIR,
                               type=str,
    )
    parent_parser.add_argument('-v', '--verbose',
                               dest='verbose',
                               help='Enable verbose output (default=False)',
                               default=False, 
                               action='store_true',
    )

    sub_parser = parser.add_subparsers(title='Pipeline options:', dest='subcommand')

    # Setting up
    parser_setup = sub_parser.add_parser('setup', help='Easy setup for directories and files',
                                         parents=[parent_parser])
    parser_setup.add_argument('-n', '--nb', '--note', '--notebook', 
                              dest='notebook', 
                              help='Use jupyter notebook instead',
                              default=False, 
                              action='store_true',
    )
    parser_setup.set_defaults(func=pipeline.setup)

    # Run ranking algorithm

    parser_run = sub_parser.add_parser('rank', help='Rank targets for a given survey', 
                                       parents=[parent_parser])
    parser_run.add_argument('-a', '--include', '--archival',
                            dest='archival',
                            help='Include archival (or already existing) data',
                            default=False, 
                            action='store_true',
    )
    parser_run.add_argument('--mc', '--iter', '--steps', 
                            dest='iter', 
                            help='Number of selection process iterations (default=1)',
                            default=1, 
                            type=int,
    )
    parser_run.add_argument('-p', '-b', '--prog', '--progress',
                            dest='progress',
                            help='Turn off progress bar (default=True). Only activates for > 1 iteration',
                            default=True, 
                            action='store_false',
    )
    parser_run.add_argument('--hpn', '--hours', '--hourspernight',
                            dest='hours',
                            type=float,
                            default=10.0,
                            help="Number of hours per night. (default=10)",
    )
    parser_run.add_argument('--inst', '--instrument',
                            dest='instrument',
                            type=str,
                            default='hires',
                            help='What instrument to use for survey',
    )
    parser_run.add_argument('--night', '--pool', '--nights',
                            dest='nights',
                            type=float,
                            default=50.0,
                            help="Total number of allocated nights for survey.",
    )
    parser_run.add_argument('--over', '--overhead',
                            dest='overhead',
                            type=float,
                            default=2.0,
                            help="Accounts for readout and slew times (minutes)",
    )
    parser_run.add_argument('-s', '--save', 
                            dest='save',
                            help='Disable the saving of output data products and figures (default=True)',
                            default=True, 
                            action='store_false',
    )
    parser_run.add_argument('--tl', '--lower', '--tlower',
                            dest='time_lower',
                            type=float,
                            default=3.0,
                            help="Minimum exposure time allowed (minutes)",
    )
    parser_run.add_argument('--tu', '--upper', '--tupper',
                            dest='time_upper',
                            type=float,
                            default=20.0,
                            help="Maximum exposure time allowed (minutes)",
    )

    parser_run.set_defaults(func=pipeline.rank)

    args = parser.parse_args()
    args.func(args)



if __name__ == '__main__':

    main()