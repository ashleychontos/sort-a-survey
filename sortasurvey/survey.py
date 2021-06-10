import numpy as np
import pandas as pd
from tqdm import tqdm
pd.set_option('mode.chained_assignment', None)


from sortasurvey import observing


class Survey:
    """
    Loads in survey information and the vetted survey sample.

    Parameters
    ----------
    args : argparse.Namespace
        command line arguments

    Attributes
    ----------
    verbose : bool
        verbose output (default is `True`)
    save : bool
        save output (default is `True`)
    outdir : str
        path to save output files
    progress : bool
        show progress bar of selection process (this will only work with the verbose output on)
    sample : pandas.DataFrame
        pandas dataframe containing the sample to select targets from  -> this is not updated, this is preserved
    candidates : pandas.DataFrame
        copy of the vetted survey sample dataframe -> this is updated during the selection process
    programs : pandas.DataFrame
        pandas dataframe containing survey information -> this is not updated, this is preserved
    sciences : pandas.DataFrame
        copy of the survey programs dataframe -> this is updated during the selection process
    track : dict
        logs each iteration of the target selection
    iter : int
        number of selection process iterations. Default is `1` (via args.iter).
    n : int
        iteration number
    emcee : bool
        `True` if iter > 1 but `False` by default.

    """
    
    def __init__(self, args, path_sample='info/TKS_sample.csv', path_survey='info/survey_info.csv',
                 path_priority='info/high_priority.csv', path_ignore='info/no_no.csv', iter=1,
                 hours_per_night=10., pool=50., progress=True, verbose=True, notebook=False):

        self.verbose = args.verbose
        self.save = args.save
        self.outdir = args.outdir
        self.iter = args.iter
        self.progress = args.progress
        self.notebook = notebook
        self.track = {}
        for n in np.arange(1,self.iter+1):
            self.track[n] = {}
        if self.verbose:
            print('\n ------------------------------\n -- prioritization  starting --\n ------------------------------\n\n   - loading sample and survey science information')
        self.get_sample(args)
        self.get_programs(args)
        self.get_seeds()
        if self.iter > 1:
            self.emcee = True
            if self.verbose and self.progress:
                self.pbar = tqdm(total=self.iter)
        else:
            self.emcee = False


    def get_sample(self, args, dec=-30., ruwe=2.):
        """
        Fixes the sample based on specific survey needs. Broadly for TKS, 
        this only required that the target is observable (dec > -30.) and 
        possessed a reasonable Gaia RUWE metric (ruwe < 2., where higher
        values typically indicate unresolved binaries).

        Parameters
        ----------
        args : argparse.Namespace
            command line arguments
        dec : float
            lowest possible declination for targets to observe with Keck HIRES
        ruwe : float
            astrometric Gaia RUWE (renormalized unit weight error) metric

        """
        df = pd.read_csv(args.path_survey, comment="#")
        self.programs = df.programs.values.tolist()
        sample = pd.read_csv(args.path_sample)
        self.path_sample = args.path_sample
        self.sample = sample.query("dec > %f and ruwe < %f"%(dec, ruwe))
        self.remove_bad()
        self.add_columns()
        # science-case-specific metrics
        self.get_sc3_info()
        self.get_counts(args)
        

    def remove_bad(self, disp=['FP','EB','NEB','BEB','SV','BD','NPC','SB1','SB2','FA']):
        """
        Removes unfavorable targets from the survey. In this case, this includes false 
        alarms and/or false positives, including nearby/blended eclipsing binaries as well
        as spectroscopic false positives (e.g., SB1, SB2).

        Parameters
        ----------
        disp : List[str]
            a list of unfavorable dispositions to ignore for the target selection process

        """
        for bad in disp:
            self.sample.query("disp != '%s'"%bad, inplace=True)
        self.sample.query("drop == False", inplace=True)
        self.sample.query("finish == False", inplace=True)
    

    def add_columns(self, cols=["npl","select_DG","in_other_programs","n_select","priority"]):
        """
        Adds in additional columns that might be relevant for the target selection.

        """

        cols += ["in_%s"%program for program in self.programs]
        for col in cols:
            if col == 'npl':
                self.sample[col] = self.sample.groupby('tic')['tic'].transform('count')
            else:
                self.sample[col] = [0]*len(self.sample)


    def get_counts(self, args):
        """
        Compute the number of targets that passed the different vetting steps.

        """
        query = self.sample.drop_duplicates(subset='tic')
        new_query = query.query("photo_vetting == 'passed' and spec_vetting != 'failed' and spec_vetting != 'do not observe' and ao_vetting != 'failed'")
        self.passed_tks = len(query)
        self.passed_vet = len(new_query)
        if self.verbose:
            print('   - %d targets make the standard survey cuts'%self.passed_tks)
            print('   - %d have also passed various vetting steps'%self.passed_vet)
            print('   - ranking algorithm initialized using %.1f nights (%.1f hr/n)'%(args.nights,args.hours))


    def get_programs(self, args, high_priority=[], no_no=[]):
        """
        Stores all relevant information for every program in the survey.
        This is initially loaded in via args.path_survey but also loads in
        any high priority targets and/or targets to ignore. 

        Parameters
        ----------
        args : argparse.Namespace
            command line arguments

        Attributes
        ----------
        programs : pandas.DataFrame
            **very important** dataframe containing all survey program information

        """

        programs = pd.read_csv(args.path_survey, comment="#")
        programs.set_index('programs', inplace=True, drop=False)
        if args.path_ignore is not None:
            nono = pd.read_csv(args.path_ignore)
        if args.path_priority is not None:
            priority = pd.read_csv(args.path_priority)

        for program in programs.index.values.tolist():
            # get initial allocation
            programs.loc[program,'total_time'] = (programs.loc[program,'allocations']/(np.sum(programs.allocations)))*args.nights*args.hours
            if not np.isnan(programs.loc[program,'remaining_hours']):
                programs.loc[program,'total_time'] += programs.loc[program,'remaining_hours']
            programs.loc[program,'remaining_hours'] = programs.loc[program,'total_time']
            # adjust filter for priority/ignore targets
            if args.path_priority is not None:
                high_priority = [float(target) for target in priority[program].values if target != '-']
            if args.path_ignore is not None:
                no_no = [float(target) for target in nono[program].values if target != '-']
            if (high_priority + no_no) != []:
                for toi in (high_priority + no_no):
                    programs.loc[program,'filter'] += " and toi != %.2f"%toi
            if programs.loc[program,'n_maximum'] != -1:
                programs.loc[program,'n_targets_left'] = programs.loc[program,'n_maximum']
            else:
                query = self.sample.query(programs.loc[program,'filter'])
                targets = query.toi.values.tolist() + high_priority
                targets = [int(np.floor(each)) for each in targets]
                programs.loc[program,'n_targets_left'] = len(list(set(targets)))
            # get the prioritization metric
            prioritize_by=[]
            for each in programs.loc[program,'prioritize_by'].strip().split('|'):
                prioritize_by.append(each)
            programs.at[program,'prioritize_by'] = prioritize_by
            ascending_by=[]
            for each in programs.loc[program,'ascending_by'].strip().split('|'):
                if each == 'True' or str(each) == 'True' or str(each) == 'TRUE':
                    ascending_by.append(True)
                else:
                    ascending_by.append(False)
            programs.at[program,'ascending_by'] = ascending_by
        programs['pick_number'] = np.zeros(len(programs)).astype('int64')
        programs['n_targets_left'] = programs['n_targets_left'].astype('int64')
        programs.rename(columns={'programs':'name'}, inplace=True)
        programs.drop(columns=['allocations'], inplace=True)
        programs = programs.to_dict('index')
        for program in programs:
            if args.path_priority is not None:
                programs[program]['high_priority'] = [float(target) for target in priority[program].values if target != '-']
            else:
                programs[program]['high_priority'] = high_priority
        programs = pd.DataFrame.from_dict(programs, orient='index', columns=['name','method','filter','prioritize_by','ascending_by','remaining_hours','n_maximum','total_time','high_priority','n_targets_left','pick_number'])
        programs.to_csv('%s_copy.%s'%(args.path_survey.split('.')[0],args.path_survey.split('.')[-1]))
        self.programs = programs.copy()


    # science-case-specific functions
    def get_sc3_info(self, include_qlp=True, mask=None):
        """
        TODO

        """
        if not include_qlp:
            mask = self.sample['source'] == 'spoc'
        self.calculate_TSM(mask=mask)
        sc3_df = self.sample.copy()
        sc3_mask = pd.notnull(sc3_df['TSM'])
        rp_bins = 10**(np.linspace(0,1,6))
        rp_bins[-1] = 11.2
        sinc_bins = 10**(np.linspace(-1,4,6))
        teff_bins = np.array([2500,3900,5200,6500])
        bins = [rp_bins, sinc_bins, teff_bins]
        sc3_df['rt_5sig'] = sc3_df['rt_5sig'].replace(0., 1e-2)
        sc3_mask &= pd.notnull(sc3_df['rt_5sig'])
        sc3_df = sc3_df[sc3_mask]
        sc3_df['X'] = sc3_df['TSM']/sc3_df['rt_5sig']
        sc3_df = self.sc3_binning_function(sc3_df, bins, sort_val='X')
        sc3_df['SC3_bin_rank'] = sc3_df['SC3_bin_rank'].replace(0., np.nan)
        cols_to_use = ['toi','SC3_bin_rank']
        self.sample = self.sample.merge(sc3_df[cols_to_use], how='left', on='toi')


    def calculate_TSM(self, mask=None):
        """
        Calculate the transmission spectroscopy metric (TSM) for all targets
        in the survey.sample

        Parameters
        ----------
        mask : bool

        """
        self.sample['TSM'] = [np.nan]*len(self.sample)
        if mask is None:
            mask = np.ones(len(self.sample), dtype=bool)
        for key in ['rp','mp','a_to_R','teff','jmag','r_s']:
            mask &= pd.notnull(self.sample[key])
        def rp_to_scale_factor(rp):
            if rp < 1.5:
                scale_factor = 0.19
            elif rp > 1.5 and rp < 2.75:
                scale_factor = 1.26
            elif rp > 2.75 and rp < 4:
                scale_factor = 1.28
            else:
                scale_factor = 1.15
            return scale_factor
        scale_factors = self.sample.loc[mask,'rp'].apply(rp_to_scale_factor)
        Teqs = self.sample.loc[mask,'teff']*np.sqrt(np.reciprocal(self.sample.loc[mask,'a_to_R'])*np.sqrt(0.25))
        numerator = scale_factors*np.power(self.sample.loc[mask, 'rp'], 3)*Teqs*np.power(10, -1*self.sample.loc[mask,'jmag']/5)
        denominator = self.sample.loc[mask,'mp']*np.square(self.sample.loc[mask,'r_s'])
        self.sample.loc[mask,'TSM'] = numerator/denominator


    def sc3_binning_function(self, df, bins, sort_val='TSM', num_to_rank=5):
        """
        TODO

        """
        pre_bin = df.assign(
            rp_bin = pd.cut(df['rp'],bins=bins[0],labels = [1,2,3,4,5]),
            sinc_bin = pd.cut(df['sinc'],bins=bins[1],labels = [1,2,3,4,5]),
            teff_bin = pd.cut(df['teff'],bins=bins[2],labels = [1,2,3])
        )
        binned_df = pre_bin.dropna(subset=['rp_bin','sinc_bin','teff_bin']).\
                groupby(['rp_bin','sinc_bin','teff_bin']).apply(lambda _pre_bin:\
                _pre_bin.sort_values(by=[sort_val],ascending=False))\
                .reset_index(level = 3,drop=True)
        all_idx = binned_df.index.tolist()
        unique_idx = []
        for element in all_idx:
            if element not in unique_idx:
                unique_idx.append(element)
        binned_df['SC3_bin_rank'] = np.zeros(len(binned_df))
        for idx in unique_idx:
            bin_items = len(binned_df.loc[idx].sort_values(sort_val,ascending=False).iloc[0:num_to_rank]['toi'])
            for i in range(1, num_to_rank+1):
                if bin_items == i and bin_items <= num_to_rank:
                    for j in range(i):
                        binned_df.loc[binned_df['toi'] == binned_df.loc[idx].sort_values\
                                (sort_val,ascending=False).iloc[0:num_to_rank]['toi'].iloc[j],'SC3_bin_rank'] = j+1
                elif bin_items > num_to_rank:
                    for j in range(num_to_rank):
                        binned_df.loc[binned_df['toi'] == binned_df.loc[idx].sort_values\
                                (sort_val,ascending=False).iloc[0:num_to_rank]['toi'].iloc[j],'SC3_bin_rank'] = j+1
        return binned_df
 

    def reset_track(self):
        """
        For MC iterations > 1, this module resets all the required information 
        back to initial starting conditions, including the starting sample and
        and initial program information (e.g., allocation, etc.), as well as a 
        new survey.track to log the new selection process to.

        """
        # make copies of the original dataframes, thus resetting the information
        self.candidates = self.sample.copy()
        self.sciences = self.programs.copy()
        self.track[self.n][0] = {}
        for program, hours in zip(self.sciences.index.values.tolist(), self.sciences.remaining_hours.values.tolist()):
            self.track[self.n][0][program] = round(hours,3)
        self.track[self.n][0]['total_time'] = round(np.sum(self.sciences.remaining_hours.values.tolist()),3)
        self.track[self.n][0]['program'] = '--'
        self.track[self.n][0]['program_pick'] = 0
        self.track[self.n][0]['overall_priority'] = 0
        self.track[self.n][0]['toi'] = 0
        self.track[self.n][0]['tic'] = 0
        self.priority = 1
        self.i = 1
        np.random.seed(self.seeds[self.n-1])


    def update(self, pick, program):
        """
        Updates appropriate information and tables with new program selection. This module
        operates in roughly the following order:

        1)  adds the program and the program pick to the survey.track 
        2)  reduces the available number of targets left in a program by 1
        3)  checks if the target has been selected by other programs and if `True`, credits the
            appropriate programs back the difference in cost
        4)  after crediting/debiting all relevant programs, the remaining hours in all programs
            in the survey is logged in the survey.track, along with the overall priority of the
            selected target in the survey as well as the internal program priority

        """
        self.add_program_pick(pick, program)
        self.sciences.loc[program,'n_targets_left'] -= 1
        self.sciences.loc[program,'pick_number'] += 1
        self = observing.check_observing(self, pick, program)
        if not int(pick.in_other_programs):
            net = {program:-1.*(float(pick.actual_cost)/3600.)}
            self.track[self.n][self.i]['overall_priority'] = self.priority
            self.candidates.loc[self.candidates['tic'] == int(pick.tic),'priority'] = int(self.priority)
            self.priority += 1
        else:
            net = observing.adjust_costs(self, pick, program)
            idx = self.candidates.loc[self.candidates['tic'] == int(pick.tic)].index.values.tolist()[0]
            self.track[self.n][self.i]['overall_priority'] = int(self.candidates.loc[idx,'priority'])
        for key in net.keys():
            self.sciences.loc[key,'remaining_hours'] += net[key]
        self.update_program_hours()
        self.candidates.loc[self.candidates['tic'] == int(pick.tic),'in_%s'%program] = 1
        self.update_targets()
        self.i += 1


    def add_program_pick(self, pick, program):
        """
        Updates the survey.track with the new selection, including the program, the internal
        program priority (or pick number), the selected target's TOI and TIC.

        """
        self.track[self.n][self.i] = {}
        self.track[self.n][self.i]['program'] = program
        self.track[self.n][self.i]['program_pick'] = self.sciences.loc[program,'pick_number']+1
        self.track[self.n][self.i]['toi'] = float(pick.toi)
        self.track[self.n][self.i]['tic'] = int(pick.tic)


    def update_program_hours(self):
        """
        Updates the survey.track with the final remaining hours for each program 
        after any credits or debits were made in the single iteration (transaction).

        """
        for program, hours in zip(self.sciences.index.values.tolist(), self.sciences.remaining_hours.values.tolist()):
            self.track[self.n][self.i][program] = round(hours,3)
        self.track[self.n][self.i]['total_time'] = round(np.sum(self.sciences.remaining_hours.values.tolist()),3)


    def update_targets(self):
        """
        Updates the survey sample (via survey.candidates), which counts the number of programs 
        a given target was selected by.

        """
        start = np.array([0]*len(self.candidates))
        for science in self.sciences.index.values.tolist():
            start += self.candidates['in_%s'%science].values.tolist()
        self.candidates['in_other_programs'] = start


    def get_seeds(self):
        """
        Ensures reproducibility due to the instrinsic randomness of the algorithm.

        """
        self.seeds = [2222, 5531, 5348, 9632, 3755, 3401, 1061, 9307, 2033, 2114, 3103, 8120, 5442, 9179, 3165, 6114, 8757, 8574, 8078, 7724, 9056, 9066, 8423, 5278, 663, 4542, 6448, 7261, 6999, 7212, 3832, 3199, 6444, 1704, 8872, 2743, 9163, 1293, 8458, 5782, 7144, 9339, 3961, 9127, 4105, 3209, 7662, 5592, 4672, 2365, 8214, 3725, 2088, 1234, 6984, 2756, 3962, 7279, 9686, 112, 8936, 8807, 4149, 2535, 1541, 1422, 7991, 6445, 4384, 570, 9719, 5834, 5372, 1376, 1192, 1499, 8653, 730, 5469, 7541, 6546, 4002, 5677, 9251, 5459, 630, 908, 9074, 2675, 9517, 1015, 5272, 6846, 6820, 4516, 5632, 5671, 2126, 4440, 9670, 7768, 1405, 5330, 1854, 3156, 6949, 1119, 5257, 2999, 4251, 9674, 5362, 5009, 7526, 8293, 4518, 8641, 1365, 2492, 5061, 4804, 2710, 8823, 6637, 9382, 7928, 9219, 7840, 895, 5647, 3966, 6452, 9027, 8673, 1006, 469, 5056, 42, 8067, 7571, 3304, 6795, 9131, 6327, 5781, 5336, 4484, 5137, 3231, 4465, 91, 5135, 3303, 1890, 7593, 359, 6051, 1236, 9967, 3149, 9913, 3114, 9267, 3049, 6089, 6439, 828, 8893, 7708, 6766, 2818, 8745, 8791, 3639, 461, 3917, 8917, 2863, 1865, 9410, 1851, 617, 7563, 915, 1773, 4997, 6121, 8540, 6358, 1630, 5468, 8585, 4959, 8115, 6337, 355, 1977, 4800, 6831, 932, 1028, 8232, 1381, 3260, 2937, 7031, 6310, 5348, 2172, 3321, 4422, 1195, 2021, 481, 731, 5566, 9719, 7468, 9499, 1326, 4071, 7660, 6583, 5067, 5693, 2933, 8679, 9988, 550, 2599, 5536, 3081, 4429, 3592, 8140, 1398, 1481, 6823, 9006, 9264, 6037, 95, 9807, 2768, 4792, 7417, 6095, 8049, 79, 5070, 1457, 3099, 736, 2332, 2228, 146, 3862, 2153, 7800, 8664, 625, 2393, 88, 780, 4266, 9412, 4973, 426, 7742, 4593, 408, 7296, 1981, 867, 7636, 2455, 3519, 3093, 882, 7396, 815, 7717, 4792, 3103, 2747, 290, 8302, 2124, 2516, 3170, 8224, 3693, 5721, 3599, 9778, 5903, 8544, 69, 7648, 4860, 212, 517, 3765, 1401, 8722, 1689, 3281, 3061, 9293, 4954, 4584, 3357, 6380, 5266, 8972, 5578, 9289, 859, 486, 3746, 7928, 7240, 2861, 7615, 651, 5633, 4687, 7439, 2572, 1999, 1476, 5806, 1966, 9249, 3439, 4559, 6899, 5633, 1973, 6469, 1636, 4922, 5059, 7772, 3907, 7410, 1822, 9659, 8230, 3643, 9106, 9524, 8971, 2887, 705, 4252, 6198, 1420, 9063, 5272, 9641, 195, 5217, 1819, 2286, 431, 5379, 26, 7690, 7241, 3735, 2987, 1490, 2807, 5059, 6556, 5921, 3949, 6128, 606, 7636, 1451, 4598, 2446, 9877, 635, 876, 9594, 1742, 5887, 5355, 365, 8197, 7919, 6969, 9736, 1703, 8703, 3358, 8321, 6817, 3617, 9069, 6406, 3938, 3077, 6166, 1546, 4393, 1026, 9479, 2568, 1787, 1434, 8390, 3844, 4028, 5643, 9291, 5072, 8022, 7260, 1209, 5579, 6860, 2871, 2662, 4769, 7361, 7427, 8737, 1608, 6613, 7941, 5619, 6949, 3217, 4204, 1439, 3439, 4521, 4761, 4089, 2066, 9623, 3076, 9230, 1503, 9896, 7110, 2152, 1291, 1339, 5088, 2959, 8092, 5381, 7283, 8831, 8448, 6775, 5414, 5871, 2728, 8828, 6320, 3294, 7953, 4157, 5654, 6890, 5134, 45, 6881, 4237, 9561, 913, 9990, 9667, 650, 1353, 2963, 3896, 4368, 8162, 5630, 5889, 9093, 5298, 17, 7958, 6417, 7574, 6461, 7446, 8398, 5486, 7742, 7503, 1740, 6987, 2238, 1159, 6552, 7968, 440, 1671, 7755, 9214, 1099, 7801, 4910, 878, 3278, 667, 1813, 7540, 2082, 3182, 5580, 3256, 9619, 5890, 8902, 9635, 2516, 864, 823, 9222, 6156, 5011, 7191, 4584, 4112, 9991, 110, 2361, 2709, 6469, 9592, 9668, 6788, 7505, 4174, 3119, 5693, 429, 6224, 3174, 6134, 6902, 9692, 2620, 1532, 7973, 5644, 6105, 2495, 1368, 9342, 3747, 9358, 1039, 311, 5382, 7309, 2482, 1889, 1162, 5620, 8439, 5487, 975, 4845, 4641, 7027, 747, 1016, 5728, 6175, 5252, 598, 4920, 5544, 6273, 9336, 8096, 8059, 2467, 1098, 72, 372, 737, 4500, 2736, 7458, 3742, 3156, 8420, 5311, 8532, 7186, 9113, 7041, 6658, 2370, 2733, 8258, 139, 6127, 4489, 692, 5627, 8139, 9744, 9773, 3674, 9103, 9896, 897, 2939, 8342, 3031, 4991, 3110, 3845, 2214, 5184, 7482, 3367, 5030, 9570, 7613, 1394, 1491, 2570, 5573, 9688, 2731, 8333, 6764, 4922, 4886, 8623, 2301, 8688, 9286, 832, 439, 2502, 8934, 5356, 6584, 6322, 6958, 1542, 9526, 9040, 10000, 8659, 1672, 610, 4050, 6616, 7105, 6073, 9004, 5102, 7781, 1615, 8225, 2511, 3862, 6110, 9382, 5402, 1501, 1972, 6596, 2496, 2523, 2710, 3515, 4024, 7273, 6509, 1913, 8888, 5892, 6173, 1836, 7008, 1328, 6628, 6840, 126, 3190, 4511, 5644, 8944, 6386, 8863, 5022, 5361, 3799, 6701, 750, 785, 2069, 6609, 6429, 7252, 5477, 2309, 9163, 7957, 4056, 8866, 6815, 8583, 2891, 6979, 1242, 3795, 4564, 1785, 1292, 3009, 8132, 3837, 5357, 5549, 9030, 9177, 7603, 3764, 347, 3695, 3836, 7269, 1196, 5401, 4362, 4053, 9416, 2994, 6420, 8527, 7178, 1084, 1582, 967, 7636, 3565, 6510, 4259, 6769, 7106, 1102, 2072, 5721, 4149, 1459, 4861, 39, 1404, 44, 7296, 3745, 2023, 3162, 4885, 9147, 2716, 4395, 9489, 9240, 9882, 3761, 2755, 1862, 9856, 404, 7118, 8258, 5581, 1477, 4694, 463, 598, 9566, 9119, 6289, 5209, 6703, 4719, 8622, 9687, 8361, 5639, 812, 6559, 9332, 6663, 5722, 3930, 8141, 6207, 7787, 1572, 6012, 6052, 609, 6106, 606, 3013, 3915, 6504, 7301, 5596, 1644, 4915, 5623, 943, 1779, 1028, 5734, 8674, 6440, 5126, 5988, 4179, 2955, 9198, 4068, 7912, 6211, 8559, 7260, 193, 7662, 8317, 7231, 181, 1482, 9115, 9971, 4519, 4073, 4300, 2938, 5456, 2939, 3906, 6385, 5011, 9510, 1227, 8649, 4715, 6021, 5418, 3568, 3571, 622, 5414, 1137, 5375, 6263, 4930, 2352, 8565, 6277, 563, 1113, 4847, 1355, 3215, 5297, 8883, 8371, 6917, 5952, 3448, 6154, 52, 2204, 763, 919, 7355, 2095, 8809, 2362, 7590, 5591, 4950, 2817, 7882, 9214, 7549, 5118, 1046, 2298, 7458, 8277, 339, 2443, 8941, 2072, 324, 1350, 5502, 2501, 2680, 5925, 9935, 6294, 5578, 6686, 5888, 5921, 2690, 8177, 2405, 5438, 6754, 2331, 5550, 1591, 9183, 3714, 1097, 7171, 1552, 117, 1135, 1067, 4952, 6742, 3960, 1489, 4201, 2390, 7777, 979, 2114, 9652, 7569, 5795, 4386, 7838, 6684, 1262, 7700, 8091, 1979, 3566, 6058, 5834, 5443, 50, 1658, 6047, 4273, 9477, 3761, 5953, 2732, 7142, 81, 4457, 4703, 5029, 9303, 1936, 468, 5888, 7253, 6611, 1883, 8285, 7267, 2028, 2842, 9302, 4262, 812, 2696, 9879, 2992, 4865, 5031, 6292, 2439, 2261, 8345, 9926, 8960, 2960, 4199]