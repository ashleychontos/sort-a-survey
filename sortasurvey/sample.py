import os
import glob
import numpy as np
import pandas as pd

from sortasurvey.observing import Instrument


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

    def __init__(self, survey):
        self.df = survey.candidates.copy()
        self.programs = survey.sciences.copy()
        self.program = survey.program
        self.instrument = Instrument(survey)
        self.get_vetted_science()


    def __call__(self):
        self.get_highest_priority()
        if self.pick is not None:
            cost = float((self.pick.actual_cost))/3600.
            if cost > self.programs.loc[self.program,'remaining_hours']:
                return True
            else:
                return False
        return True


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
        self.query = self.df.query(self.programs.loc[self.program,'filter'])
        if drop_dup:
            self.query = self.query.drop_duplicates(subset='tic')
        self.get_current_costs()
        self.query_copy = self.query.sort_values(by=self.programs.loc[self.program,'prioritize_by'], ascending=self.programs.loc[self.program,'ascending_by'])
        if self.programs.loc[self.program,'high_priority'] != []:
            top = pd.DataFrame(columns=self.query.columns.values.tolist())
            for toi in self.programs.loc[self.program,'high_priority']:
                self.query = self.df.query('toi == %.2f'%toi)
                self.get_current_costs()
                top = pd.concat([top,self.query])
            self.query = pd.concat([top,self.query_copy])
        self.query.reset_index(drop=True, inplace=True)


    def get_current_costs(self, current_costs=[]):
        """
        Called during each sampling step to recompute the most up-to-date costs
        for a given target based on past algorithm selections

        Parameters
        ----------
        program : str
            selected program that is making the selection
        programs : pandas.DataFrame
            survey program dataframe
        query : pandas.DataFrame
            all targets from the vetted sample relevant for the selected program
    
        Returns
        -------
        query : pandas.DataFrame
            the relevant vetted sample updated with actual target costs
    
        """
        for index in self.query.index.values.tolist():
            costs = []
            teff, vmag, template, nobs = self.query.loc[idx, 'teff'], self.query.loc[idx,'vmag'], self.query.loc[idx,'template'], self.query.loc[idx,'nobs']
            for science in self.programs.index.values.tolist():
                if self.query.loc[index,'in_%s'%science]:
                    costs.append(self.instrument(teff, vmag, self.programs.loc[science,'method'], template=template, nobs=nobs))
            costs.append(self.instrument(teff, vmag, self.programs.loc[self.program,'method'], template=template, nobs=nobs))
            if float(np.sum(costs)) != 0.:
                fraction = costs[-1]/np.sum(costs)
                current_costs.append(fraction*max(costs))
            else:
                current_costs.append(0.)
        self.query['actual_cost'] = np.array(current_costs)
        

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
        self.pick = pick


    def get_net_costs(self, costs=[], cases=[]):
        """
        Based on the selected program's pick, calculates the credit/debit amounts
        for any program that has selected the same target.
    
        Parameters
        ----------
        survey : survey.Survey
            class object containing both the vetted sample (via survey.candidates) and the
            survey programs (via survey.sciences)
        pick : pandas.DataFrame
            a single row dataframe containing information on the selected program's current pick
        program : str
            the selected program
        cases : List[str]
            other programs that have selected a given target in past iterations
        costs : List[float]
            the cost of a target given a specific program's observing strategy
    
        Returns
        -------
        net : Dict[str,float]
            a python dictionary whose keys are other programs to credit or debit back, pointing
            to the amount of time to credit or debit the program back

        """
        index = self.df.index[self.df['tic'] == int(self.pick.tic)].tolist()[0]
        teff, vmag, template, nobs = self.df.loc[index,'teff'], self.df.loc[index,'vmag'], self.df.loc[index,'template'], self.df.loc[index,'nobs']
        for science in self.programs.index.values.tolist():
            if self.pick['in_%s'%science]:
                cases.append(science)
                costs.append(self.instrument(teff, vmag, self.programs.loc[science]['method'], template=template, nobs=nobs))
        cases.append(self.program)
        if float(np.sum(costs)) == 0.:
            net_costs = -1.*np.zeros(len(cases))
        else:
            frac = costs/np.sum(costs)
            old_costs = list((max(costs)/3600.)*frac)
            old_costs.append(0)
            costs.append(self.instrument(teff, vmag, self.programs.loc[self.program]['method'], template=template, nobs=nobs))
            new_frac = costs/np.sum(costs)
            new_costs = np.array((max(costs)/3600.)*new_frac)
            net_costs = -1.*(new_costs - np.array(old_costs))
        return dict(zip(cases,net_costs))


    def get_vetted_sample(self, final_path=None):
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
        if final_path is None:
            list_of_files = glob.glob('results/*/TKS_sample_final.csv')
            latest_file = max(list_of_files, key=os.path.getctime)
        else:
            latest_file = final_path
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
            list_of_files = glob.glob('results/*/TKS_sample_final.csv')
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