import os
import glob
import numpy as np
import pandas as pd


from sortasurvey import observing


class Sample:
    """
    Creates a filtered sample based on the provided survey program. The most common 
    use of the sample is during the target selection process, which calls the 
    get_highest_priority method at each iteration. All other methods are useful 
    for post-target selection filtering, shown in the provided Jupyter notebook example (TODO).

    Attributes
    ----------
    df : pandas.DataFrame
        vetted sample from the survey.Survey
    programs : pandas.DataFrame
        survey programs from the survey.Survey 

    Parameters
    ----------
    survey : Optional[survey.Survey]
        will save the science programs and vetted sample of a given survey to the
        Sample.programs and Sample.df attributes, respectively if not `None`.
    path_init : Optional[str]
        path to vetted sample (default = 'info/TOIs_perfect.csv')
    path_final : Optional[str]
        root path to results (default = `None`)
    program : str
        selected program of interest within a survey
    

    """

    def __init__(self, program, survey=None, path_init='info/TOIs_perfect.csv', path_final=None):
        self.path_init = path_init
        self.program = program
        if survey is not None:
            self.df = survey.candidates.copy()
            self.programs = survey.sciences.copy()
            self.get_vetted_science(program)


    def get_vetted_science(self, drop_dup=True):
        """
        Similar to the vetted sample method above, it loads the same sample which was (is)
        available for target selection but filters the sample to address a specific science 
        case's (or program) needs. 

        Attributes
        ----------
        program : str
            the program used to filter the selected Sample
        query : pandas.DataFrame
            the original vetted survey sample filtered on the specific program's selection criteria

        Parameters
        ----------
        drop_dup : Optional[bool]
            option to drop duplicate targets in the sample query, since the target will only be observed once. As a result, the default is `True`.

        """
        if not hasattr(self, 'df'):
            self.df = pd.read_csv(self.path_init)
        query = self.df.query(self.programs.loc[self.program,'filter'])
        if drop_dup:
            query = query.drop_duplicates(subset='tic')
        query = observing.get_actual_costs(self.program, self.programs, query)
        query = query.sort_values(by=self.programs.loc[self.program,'prioritize_by'], ascending=self.programs.loc[self.program,'ascending_by'])
        if self.programs.loc[self.program,'high_priority'] != []:
            top = pd.DataFrame(columns = query.columns.values.tolist())
            for toi in self.programs.loc[self.program,'high_priority']:
                new_filter = 'toi == %.2f'%toi
                new = self.df.query(new_filter)
                new = observing.get_actual_costs(self.program, self.programs, new)
                top = pd.concat([top,new])
            query = pd.concat([top,query])
        query.reset_index(drop=True, inplace=True)
        self.query = query.copy()
        

    def get_highest_priority(self, pick=None):
        """
        Returns the highest priority target for a selected program that has not
        yet been selected by that program.

        Attributes
        ----------
        program : str
            the program used to filter the selected Sample
        query : pandas.DataFrame
            the original vetted survey sample filtered on the specific program's selection criteria

        Returns
        -------
        pick : pandas.DataFrame
            the selected's program's highest priority pick

        """
        for i in self.query.index.values.tolist():
            if not int(self.query.loc[i,'in_%s'%self.program]):
                pick = self.query.loc[i]
                break
        return pick


    def get_vetted_sample(self):
        """
        Loads the vetted sample that was available during the survey selection process.
        Using the final csv path, it selects the sample from the most recent output directory.

        Parameters
        ----------
        final_path : Optional[str]
            path of output csv file to read in

        Returns
        -------
        df : pandas.DataFrame
            the full vetted sample used for the target selection

        """
        list_of_files = glob.glob(self.final_path)
        latest_file = max(list_of_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        return df


    def get_selected_sample(self, final_path=None):
        """
        Loads the final sample selected from the target prioritization process. If 
        no path is provided, it will automatically load in the most recent output.

        Parameters
        ----------
        final_path : Optional[str]
            path of output csv file to read in

        

        Returns
        -------
        df : pandas.DataFrame
            the sample selected by the algorithm for a given Survey 

        """
        if final_path is None:
            list_of_files = glob.glob('results/other/*/*/TOIs_perfect_final.csv')
            latest_file = max(list_of_files, key=os.path.getctime)
        else:
            latest_file = final_path
        df = pd.read_csv(latest_file)
        df.query("in_other_programs != 0", inplace=True)
        return df


    def get_science_sample(self, program, path_final=None):
        """
        Loads the final sample selected from the target prioritization process for a 
        specific science case or program from the Survey. If no path is provided, it
        will automatically load in the most recent output.

        Parameters
        ----------
        program : str
            specific Survey program to downselect the sample for
        path_final : Optional[str]
            path of output csv file to read in

        Returns
        -------
        df : pandas.DataFrame
            the sample selected by the algorithm for a specific Survey program

        """
        list_of_files = glob.glob(self.final_path)
        latest_file = max(list_of_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        df.query("in_%s == 1"%program, inplace=True)
        return df