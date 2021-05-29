import numpy as np
import pandas as pd


from sortasurvey import observing


class Sample:
    """
    Creates a filtered sample based on the provided survey program. The most common 
    use of the sample is during the target selection process, which calls the 
    get_highest_priority method at each iteration. All other methods are useful 
    for post-target selection filtering, shown in the provided Jupyter notebook example.

    Attributes
    ----------
    init_path : str
        path to vetted sample (defaults = 'info/TOIs_perfect.csv')
    df : pandas.DataFrame
        vetted sample from survey class object, if survey is not `None`
    programs : pandas.DataFrame
        survey programs if survey is not `None`

    Parameters
    ----------
    program : str
        selected program of interest within a survey
    path_final : str
        path to the output file containing the selected sample
    

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

        program : str
            which program to filter the sample on ** Note: program must match original
            science case key (e.g. SC1B -> "in_%s"%program, where the latter is generated
            during the initial target selection process)

        returns : pd.DataFrame

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
        

    def get_highest_priority(self):
        for i in self.query.index.values.tolist():
            if not int(self.query.loc[i,'in_%s'%self.program]):
                pick = self.query.loc[i]
                break
        return pick


    def _get_vetted_sample(self):
        """
        Loads the vetted sample that was available during the survey selection process.
        Using the final csv path, it selects the sample from the most recent output directory.

        input : 

        returns : pd.DataFrame

        """
        list_of_files = glob.glob(self.final_path)
        latest_file = max(list_of_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        return df


    def _get_selected_sample(self):
        """
        Loads the final sample selected from the target prioritization process. Using the 
        final csv path (final_path), it selects the sample from the most recent output 
        directory and stores it to a pandas DataFrame. The df is queried for targets that 
        were selected by at least one program ("in_other_programs != 0").

        input : 

        returns : pd.DataFrame

        """
        list_of_files = glob.glob(self.final_path)
        latest_file = max(list_of_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        df.query("in_other_programs != 0", inplace=True)
        return df

    def _get_science_sample(self, program):
        """
        Loads the final sample selected from the target prioritization process for a 
        specific science case (or program). Using the final csv path (final_path), it 
        selects the sample from the most recent output directory and stores it to a 
        pandas DataFrame. The df is queried for targets that were selected by the
        specific program ("in_program == 1").

        program : str
            which program to filter the sample on ** Note: program must match original
            science case key (e.g. SC1B -> "in_%s"%program, where the latter is generated
            during the initial target selection process)

        returns : pd.DataFrame

        """
        list_of_files = glob.glob(self.final_path)
        latest_file = max(list_of_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        df.query("in_%s == 1"%program, inplace=True)
        return df