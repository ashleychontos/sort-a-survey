import os
import datetime
import numpy as np
import pandas as pd
from utils import *




class Sample:
    """
    Creates a survey sample. Initialization saves initial and final sample paths.
    The most common use of this sample is during the target selection process, which
    calls the get_highest_priority method at each iteration. All other methods are
    useful for post-target selection filtering, shown in the provided Jupyter notebook.

    Attributes
    ----------
    init_path : str
        path to the total TOI (or other target) sample ** right now requires csv format
    final_path : str
        path to the vetted output sample ** right now requires csv format

    Methods
    -------

        get_vetted_sample
        -----------------
            Loads the vetted sample that was available during the survey selection process.
            Using the final csv path, it selects the sample from the most recent output directory.

            input : 

            returns : pd.DataFrame

        get_vetted_science
        -----------------
            Similar to the vetted sample method above, it loads the same sample which was (is)
            available for target selection but filters the sample to address a specific science 
            case's (or program) needs. 

            positional argument(s) 
            ----------------------
            program : str
                which program to filter the sample on ** Note: program must match original
                science case key (e.g. SC1B -> "in_%s"%program, where the latter is generated
                during the initial target selection process)

            returns : pd.DataFrame

        get_selected_sample
        -------------------
            Loads the final sample selected from the target prioritization process. Using the 
            final csv path (final_path), it selects the sample from the most recent output 
            directory and stores it to a pandas DataFrame. The df is queried for targets that 
            were selected by at least one program ("in_other_programs != 0").

            input : 

            returns : pd.DataFrame

        get_science_sample
        ------------------
            Loads the final sample selected from the target prioritization process for a 
            specific science case (or program). Using the final csv path (final_path), it 
            selects the sample from the most recent output directory and stores it to a 
            pandas DataFrame. The df is queried for targets that were selected by the
            specific program ("in_program == 1").

            positional argument(s) 
            ----------------------
            program : str
                which program to filter the sample on ** Note: program must match original
                science case key (e.g. SC1B -> "in_%s"%program, where the latter is generated
                during the initial target selection process)

            returns : pd.DataFrame

        get_science_relevant :

        get_highest_priority :

    """

    def __init__(self, df):
        self.df = df.copy()

    def get_highest_priority(self, program, programs):
        query = self.df.query(programs.loc[program,'filter'])
        query.drop_duplicates(subset='tic', inplace=True)
        query = get_actual_costs(program, programs, query)
        query = query.sort_values(by=programs.loc[program,'prioritize_by'], ascending=programs.loc[program,'ascending_by'])
        if programs.loc[program,'high_priority'] != []:
            top = pd.DataFrame(columns = query.columns.values.tolist())
            for toi in programs.loc[program,'high_priority']:
                new_filter = 'toi == %.2f'%toi
                new = self.df.query(new_filter)
                new = get_actual_costs(program, programs, new)
                top = pd.concat([top,new])
            query = pd.concat([top,query])
        query.reset_index(drop=True, inplace=True)
        for i in query.index.values.tolist():
            if not int(query.loc[i,'in_%s'%program]):
                pick = query.loc[i]
                break
#        try:
#            pick
#        except NameError as e:
#            pick = None
        return pick

    def _get_vetted_sample(self):
        list_of_files = glob.glob(self.final_path)
        latest_file = max(list_of_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        return df

    def get_vetted_science(self, drop_dup=True):
        if not hasattr(self, 'df'):
            self.df = pd.read_csv(self.init_path)
        query = self.df.query(self.programs.loc[self.program,'filter'])
        if drop_dup:
            query = query.drop_duplicates(subset='tic')
        query = get_actual_costs(self.program, self.programs, query)
        query = query.sort_values(by=self.programs.loc[self.program,'prioritize_by'], ascending=self.programs.loc[self.program,'ascending_by'])
        if self.programs.loc[self.program,'high_priority'] != []:
            top = pd.DataFrame(columns = query.columns.values.tolist())
            for toi in self.programs.loc[self.program,'high_priority']:
                new_filter = 'toi == %.2f'%toi
                new = self.df.query(new_filter)
                new = get_actual_costs(self.program, self.programs, new)
                top = pd.concat([top,new])
            query = pd.concat([top,query])
        query.reset_index(drop=True, inplace=True)
        self.query = query.copy()

    def _get_selected_sample(self):
        list_of_files = glob.glob(self.final_path)
        latest_file = max(list_of_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        df.query("in_other_programs != 0", inplace=True)
        return df

    def _get_science_sample(self, program):
        list_of_files = glob.glob(self.final_path)
        latest_file = max(list_of_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        df.query("in_%s == 1"%program, inplace=True)
        return df