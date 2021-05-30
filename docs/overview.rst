.. _overview:

Overview
########




=========================

Structure
*********

We recommend using the following structure under two main directories:

#. **info/** : [optional input] directory to provide prior information on the processed stars
#. **results/** : [optional output] directory for result figures and files


Input
*****

Info/
+++++

There are four main files provided:

#. **info/TOIs_perfect.csv** : the vetted `Survey` sample to select targets from. Slee

#. **info/survey_info.csv** : provides most of the information required for the algorithm to run successfully

   * "programs" [str] : star IDs that should exactly match the star provided via command line or in todo.txt
   * "allocations" [float] : stellar radius (units: solar radii)
   * "method" [str] : effective temperature (units: K)
   * "filter" [str] : surface gravity (units: dex)
   * "prioritize_by" [str] : the frequency corresponding to maximum power (units: muHz)
   * "ascending_by" [bool] : lower frequency limit to use in the find_excess module (units: muHz)
   * "remaining_hours" [float] : upper frequency limit to use in the find_excess module (units: muHz)
   * "n_maximum" [float] : lower frequency limit to use in the fit_background module (units: muHz)

#. **info/high_priority.csv** : contains any high priority targets for individual programs in the survey, with one column header per `Survey` program

#. **info/no_no.csv** : contains any targets to ignore for a given program, with one column header per `Survey` program.


Output
******

Results/
++++++++

Subdirectories are automatically created for each individually processed star.
Results for each of the two main ``pySYD`` modules (``find_excess`` and ``fit_background``) 
will be concatenated into a single csv in the upper-level results directory, which is
helpful when running many stars.

A single star will yield one summary figure (png) and one data product (csv) for each of the two
main modules, for a total of 4 output files. If the monte-carlo sampling is used to calculate uncertainties, an additional
figure will show the posterior distributions for the estimated parameters. See :ref:`examples` 
for a guide on what the output plots are showing.
