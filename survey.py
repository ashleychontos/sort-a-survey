import os
import datetime
import numpy as np
import pandas as pd
from utils import *
pd.set_option('mode.chained_assignment', None)


class Survey(object):
    """Creates a survey object. Initialization saves initial and final sample paths.
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
    TODO
    """
    
    def __init__(self, args, path_toi='info/TOIs_perfect.csv', path_dg='info/distant_giants_6100.csv', start=0):
        self.programs = ['SC1A', 'SC1B', 'SC1C', 'SC1D', 'SC1E', 'SC2A', 'SC2Bi', 'SC2Bii', 'SC2C', 'SC3', 'SC4', 'TOA', 'TOB']
        # does not need to add up to 1., it will normalize appropriately
        self.allocations = [0.1, 0.1, 0.1, 0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.0, 0.1]
        self.verbose = args.verbose
        self.mciter = args.mciter
        self.save = args.save
        self.pool = args.nights
        self.hours_per_night = args.hours
        self.path_toi = path_toi
        self.ranked = {}
        if self.verbose:
            print()
            print('-- prioritization starting --')
            print()
            print('  - loading TOIs and science program information')
        self.n = start
        self.df = pd.read_csv(path_toi)
        self.fix_candidates(path_dg)
        self.get_programs()
        self.candidates = self.df.copy()
        self.sciences = self.programs.copy()
        self.seeds = [2222, 5531, 5348, 9632, 3755, 3401, 1061, 9307, 2033, 2114, 3103, 8120, 5442, 9179, 3165, 6114, 8757, 8574, 8078, 7724, 9056, 9066, 8423, 5278, 663, 4542, 6448, 7261, 6999, 7212, 3832, 3199, 6444, 1704, 8872, 2743, 9163, 1293, 8458, 5782, 7144, 9339, 3961, 9127, 4105, 3209, 7662, 5592, 4672, 2365, 8214, 3725, 2088, 1234, 6984, 2756, 3962, 7279, 9686, 112, 8936, 8807, 4149, 2535, 1541, 1422, 7991, 6445, 4384, 570, 9719, 5834, 5372, 1376, 1192, 1499, 8653, 730, 5469, 7541, 6546, 4002, 5677, 9251, 5459, 630, 908, 9074, 2675, 9517, 1015, 5272, 6846, 6820, 4516, 5632, 5671, 2126, 4440, 9670, 7768, 1405, 5330, 1854, 3156, 6949, 1119, 5257, 2999, 4251, 9674, 5362, 5009, 7526, 8293, 4518, 8641, 1365, 2492, 5061, 4804, 2710, 8823, 6637, 9382, 7928, 9219, 7840, 895, 5647, 3966, 6452, 9027, 8673, 1006, 469, 5056, 42, 8067, 7571, 3304, 6795, 9131, 6327, 5781, 5336, 4484, 5137, 3231, 4465, 91, 5135, 3303, 1890, 7593, 359, 6051, 1236, 9967, 3149, 9913, 3114, 9267, 3049, 6089, 6439, 828, 8893, 7708, 6766, 2818, 8745, 8791, 3639, 461, 3917, 8917, 2863, 1865, 9410, 1851, 617, 7563, 915, 1773, 4997, 6121, 8540, 6358, 1630, 5468, 8585, 4959, 8115, 6337, 355, 1977, 4800, 6831, 932, 1028, 8232, 1381, 3260, 2937, 7031, 6310, 5348, 2172, 3321, 4422, 1195, 2021, 481, 731, 5566, 9719, 7468, 9499, 1326, 4071, 7660, 6583, 5067, 5693, 2933, 8679, 9988, 550, 2599, 5536, 3081, 4429, 3592, 8140, 1398, 1481, 6823, 9006, 9264, 6037, 95, 9807, 2768, 4792, 7417, 6095, 8049, 79, 5070, 1457, 3099, 736, 2332, 2228, 146, 3862, 2153, 7800, 8664, 625, 2393, 88, 780, 4266, 9412, 4973, 426, 7742, 4593, 408, 7296, 1981, 867, 7636, 2455, 3519, 3093, 882, 7396, 815, 7717, 4792, 3103, 2747, 290, 8302, 2124, 2516, 3170, 8224, 3693, 5721, 3599, 9778, 5903, 8544, 69, 7648, 4860, 212, 517, 3765, 1401, 8722, 1689, 3281, 3061, 9293, 4954, 4584, 3357, 6380, 5266, 8972, 5578, 9289, 859, 486, 3746, 7928, 7240, 2861, 7615, 651, 5633, 4687, 7439, 2572, 1999, 1476, 5806, 1966, 9249, 3439, 4559, 6899, 5633, 1973, 6469, 1636, 4922, 5059, 7772, 3907, 7410, 1822, 9659, 8230, 3643, 9106, 9524, 8971, 2887, 705, 4252, 6198, 1420, 9063, 5272, 9641, 195, 5217, 1819, 2286, 431, 5379, 26, 7690, 7241, 3735, 2987, 1490, 2807, 5059, 6556, 5921, 3949, 6128, 606, 7636, 1451, 4598, 2446, 9877, 635, 876, 9594, 1742, 5887, 5355, 365, 8197, 7919, 6969, 9736, 1703, 8703, 3358, 8321, 6817, 3617, 9069, 6406, 3938, 3077, 6166, 1546, 4393, 1026, 9479, 2568, 1787, 1434, 8390, 3844, 4028, 5643, 9291, 5072, 8022, 7260, 1209, 5579, 6860, 2871, 2662, 4769, 7361, 7427, 8737, 1608, 6613, 7941, 5619, 6949, 3217, 4204, 1439, 3439, 4521, 4761, 4089, 2066, 9623, 3076, 9230, 1503, 9896, 7110, 2152, 1291, 1339, 5088, 2959, 8092, 5381, 7283, 8831, 8448, 6775, 5414, 5871, 2728, 8828, 6320, 3294, 7953, 4157, 5654, 6890, 5134, 45, 6881, 4237, 9561, 913, 9990, 9667, 650, 1353, 2963, 3896, 4368, 8162, 5630, 5889, 9093, 5298, 17, 7958, 6417, 7574, 6461, 7446, 8398, 5486, 7742, 7503, 1740, 6987, 2238, 1159, 6552, 7968, 440, 1671, 7755, 9214, 1099, 7801, 4910, 878, 3278, 667, 1813, 7540, 2082, 3182, 5580, 3256, 9619, 5890, 8902, 9635, 2516, 864, 823, 9222, 6156, 5011, 7191, 4584, 4112, 9991, 110, 2361, 2709, 6469, 9592, 9668, 6788, 7505, 4174, 3119, 5693, 429, 6224, 3174, 6134, 6902, 9692, 2620, 1532, 7973, 5644, 6105, 2495, 1368, 9342, 3747, 9358, 1039, 311, 5382, 7309, 2482, 1889, 1162, 5620, 8439, 5487, 975, 4845, 4641, 7027, 747, 1016, 5728, 6175, 5252, 598, 4920, 5544, 6273, 9336, 8096, 8059, 2467, 1098, 72, 372, 737, 4500, 2736, 7458, 3742, 3156, 8420, 5311, 8532, 7186, 9113, 7041, 6658, 2370, 2733, 8258, 139, 6127, 4489, 692, 5627, 8139, 9744, 9773, 3674, 9103, 9896, 897, 2939, 8342, 3031, 4991, 3110, 3845, 2214, 5184, 7482, 3367, 5030, 9570, 7613, 1394, 1491, 2570, 5573, 9688, 2731, 8333, 6764, 4922, 4886, 8623, 2301, 8688, 9286, 832, 439, 2502, 8934, 5356, 6584, 6322, 6958, 1542, 9526, 9040, 10000, 8659, 1672, 610, 4050, 6616, 7105, 6073, 9004, 5102, 7781, 1615, 8225, 2511, 3862, 6110, 9382, 5402, 1501, 1972, 6596, 2496, 2523, 2710, 3515, 4024, 7273, 6509, 1913, 8888, 5892, 6173, 1836, 7008, 1328, 6628, 6840, 126, 3190, 4511, 5644, 8944, 6386, 8863, 5022, 5361, 3799, 6701, 750, 785, 2069, 6609, 6429, 7252, 5477, 2309, 9163, 7957, 4056, 8866, 6815, 8583, 2891, 6979, 1242, 3795, 4564, 1785, 1292, 3009, 8132, 3837, 5357, 5549, 9030, 9177, 7603, 3764, 347, 3695, 3836, 7269, 1196, 5401, 4362, 4053, 9416, 2994, 6420, 8527, 7178, 1084, 1582, 967, 7636, 3565, 6510, 4259, 6769, 7106, 1102, 2072, 5721, 4149, 1459, 4861, 39, 1404, 44, 7296, 3745, 2023, 3162, 4885, 9147, 2716, 4395, 9489, 9240, 9882, 3761, 2755, 1862, 9856, 404, 7118, 8258, 5581, 1477, 4694, 463, 598, 9566, 9119, 6289, 5209, 6703, 4719, 8622, 9687, 8361, 5639, 812, 6559, 9332, 6663, 5722, 3930, 8141, 6207, 7787, 1572, 6012, 6052, 609, 6106, 606, 3013, 3915, 6504, 7301, 5596, 1644, 4915, 5623, 943, 1779, 1028, 5734, 8674, 6440, 5126, 5988, 4179, 2955, 9198, 4068, 7912, 6211, 8559, 7260, 193, 7662, 8317, 7231, 181, 1482, 9115, 9971, 4519, 4073, 4300, 2938, 5456, 2939, 3906, 6385, 5011, 9510, 1227, 8649, 4715, 6021, 5418, 3568, 3571, 622, 5414, 1137, 5375, 6263, 4930, 2352, 8565, 6277, 563, 1113, 4847, 1355, 3215, 5297, 8883, 8371, 6917, 5952, 3448, 6154, 52, 2204, 763, 919, 7355, 2095, 8809, 2362, 7590, 5591, 4950, 2817, 7882, 9214, 7549, 5118, 1046, 2298, 7458, 8277, 339, 2443, 8941, 2072, 324, 1350, 5502, 2501, 2680, 5925, 9935, 6294, 5578, 6686, 5888, 5921, 2690, 8177, 2405, 5438, 6754, 2331, 5550, 1591, 9183, 3714, 1097, 7171, 1552, 117, 1135, 1067, 4952, 6742, 3960, 1489, 4201, 2390, 7777, 979, 2114, 9652, 7569, 5795, 4386, 7838, 6684, 1262, 7700, 8091, 1979, 3566, 6058, 5834, 5443, 50, 1658, 6047, 4273, 9477, 3761, 5953, 2732, 7142, 81, 4457, 4703, 5029, 9303, 1936, 468, 5888, 7253, 6611, 1883, 8285, 7267, 2028, 2842, 9302, 4262, 812, 2696, 9879, 2992, 4865, 5031, 6292, 2439, 2261, 8345, 9926, 8960, 2960, 4199]

    def fix_candidates(self, path_dg, dec = -30., ruwe = 2.):
        self.df = self.df.query("dec > %f and ruwe < %f"%(dec, ruwe))
        self.remove_bad()
        self.add_columns()
        # commented this out but this is helpful for any science case with specific needs, where
        # generic filters (i.e. Rp < 4, Period < 10 days) won't suffice.
        self.get_dg_info(path_dg)
        # science-specific info
        self.get_sc3_info()
        query = self.df.drop_duplicates(subset = 'tic')
        new_query = query.query("photo_vetting == 'passed' and spec_vetting != 'failed' and spec_vetting != 'do not observe' and ao_vetting != 'failed'")
        self.passed_tks = len(query)
        self.passed_vet = len(new_query)
        if self.verbose:
            print('  - %d TOIs are observable per TKS standards and have promising dispositions'%self.passed_tks)
            print('  - %d of these have also passed photometric & spectroscopic vetting'%self.passed_vet)
            print('  - ranking scheme initialized')
        
    def remove_bad(self, disp = ['FP', 'EB', 'NEB', 'BEB', 'SV', 'BD', 'NPC', 'SB1', 'SB2', 'FA']):
        for bad in disp:
            self.df.query("disp != '%s'"%bad, inplace=True)
        self.df.query("drop == False", inplace=True)
        self.df.query("finish == False", inplace=True)
    
    def add_columns(self, cols = ["npl", "select_DG", "in_other_programs", "n_select"]):
        cols += ["in_%s"%program for program in self.programs]
        for col in cols:
            if col == 'npl':
                self.df[col] = self.df.groupby('tic')['tic'].transform('count')
            else:
                self.df[col] = [0]*len(self.df)

    def get_programs(self, programs = {}, default_priority = 'actual_cost', default_method = 'hires-nobs=60-counts=ramp',
                     default_filter = "photo_vetting == 'passed' and spec_vetting != 'failed' and spec_vetting != 'do not observe' and ao_vetting != 'failed'"):
        sciences = list(self.programs)
        hours = (self.allocations/np.sum(self.allocations))*self.pool*self.hours_per_night 
        # SC1A
        science = 'SC1A'
        method = default_method
        filters = default_filter + " and rp > 1.0 and rp < 3.5"
        prioritize_by = [default_priority]
        ascending_by = [True]
        high_priority = [1347.01]
        no_no = []
        n_max = 0
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        oneA = [method, filters, prioritize_by, ascending_by, high_priority, hours[idx]/24., hours[idx], science, n_max]
        # SC1B
        science = 'SC1B'
        method = default_method
        filters = default_filter + " and rp > 1. and rp < 4. and period > 1. and period < 100."
        prioritize_by = [default_priority]
        ascending_by = [True]
        high_priority = []
        no_no = []
        n_max = 0
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        oneB = [method, filters, prioritize_by, ascending_by, high_priority, hours[idx]/24., hours[idx], science, n_max]
        # SC1C
        science = 'SC1C'
        method = default_method
        filters = default_filter + " and sinc > 650. and rp < 8."
        prioritize_by = [default_priority]
        ascending_by = [True]
        high_priority = [1436.01, 1798.01, 1444.01]
        no_no = [261.01]
        n_max = 0
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        oneC = [method, filters, prioritize_by, ascending_by, high_priority, hours[idx]/24., hours[idx], science, n_max]
        # SC1D
        science = 'SC1D'
        method = default_method
        filters = default_filter + " and sinc < 10 and evol == 'MS'"
        prioritize_by = [default_priority]
        ascending_by = [True]
        high_priority = [2088.01]
        no_no = []
        n_max = 0
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        oneD = [method, filters, prioritize_by, ascending_by, high_priority, hours[idx]/24., hours[idx], science, n_max]
        # SC1E
        science = 'SC1E'
        method = default_method
        filters = default_filter + " and m_s > 0.08 and m_s < 2.5 and feh > -1. and feh < 1."
        prioritize_by = [default_priority]
        ascending_by = [True]
        high_priority = [1436.01, 2088.01, 1801.01, 1467.01, 2013.01, 1450.01]
        no_no = []
        n_max = 0
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        oneE = [method, filters, prioritize_by, ascending_by, high_priority, hours[idx]/24., hours[idx], science, n_max]
        # SC2A
        science = 'SC2A'
        method = 'hires-nobs=15-counts=60'
        filters = "select_DG == 1"
        prioritize_by = ['vmag']
        ascending_by = [True]
        high_priority = []
        no_no = []
        n_max = 0
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        twoA = [method, filters, prioritize_by, ascending_by, high_priority, (hours[idx]+14.1)/24., hours[idx]+14.1, science, n_max]
        # SC2Bi
        science = 'SC2Bi'
        method = default_method
        filters = default_filter
        prioritize_by = [default_priority]
        ascending_by = [True]
        high_priority = []
        no_no = []
        n_max = 0
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        twoBi = [method, filters, prioritize_by, ascending_by, high_priority, hours[idx]/24., hours[idx], science, n_max]
        # SC2Bii
        science = 'SC2Bii'
        method = default_method
        filters = default_filter
        prioritize_by = [default_priority]
        ascending_by = [True]
        high_priority = [1255.01, 1272.01, 1184.01, 1347.01, 1386.01]
        no_no = []
        n_max = 5
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        twoBii = [method, filters, prioritize_by, ascending_by, high_priority, (hours[idx]-14.1)/24., hours[idx]-14.1, science, n_max]
        # SC2C
        science = 'SC2C'
        method = 'hires-nobs=100-counts=ramp'
        filters = default_filter + " and spec_vetting != 'known planet' and npl > 1 and rp < 6"
        prioritize_by = ['npl', default_priority]
        ascending_by = [False,True]
        high_priority = []
        no_no = [261.01]
        n_max = 4
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        twoC = [method, filters, prioritize_by, ascending_by, high_priority, hours[idx]/24., hours[idx], science, n_max]
        # SC3
        science = 'SC3'
        method = default_method
        filters = default_filter + " and spec_vetting != 'known planet' and (evol == 'MS' or evol == 'SG')"
        prioritize_by = ['SC3_bin_rank', default_priority]
        ascending_by = [True, True]
        high_priority = [1339.01, 1410.01, 509.01, 554.01, 469.01, 1471.01, 1430.01, 1473.01, 1736.01, 561.02, 1136.03, 669.01, 1759.01, 1247.01, 266.01]
        no_no = [1807.01, 1835.01, 1835.02]
        n_max = 0
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        three = [method, filters, prioritize_by, ascending_by, high_priority, hours[idx]/24., hours[idx], science, n_max]
        # SC4
        science = 'SC4'
        method = 'hires-nobs=30-counts=60'
        filters = "photo_vetting == 'passed' and spec_vetting != 'failed' and ao_vetting != 'failed' and "
        filters += "(ast_det_t >= 0.5 or ((evol == 'SG' or evol == 'RGB') and disp != 'KP'))"
        prioritize_by = [default_priority]
        ascending_by = [True]
        high_priority = [480.01]
        no_no = [664.01, 852.01, 1510.01, 1684.01, 1822.01, 1848.01, 2065.01]
        n_max = 0
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        four = [method, filters, prioritize_by, ascending_by, high_priority, hours[idx]/24., hours[idx], science, n_max]
        # TOA
        science = 'TOA'
        method = default_method
        filters = "(evol == 'MS' or evol == 'SG' or evol == 'RGB')"
        prioritize_by = [default_priority]
        ascending_by = [True]
        high_priority = []
        no_no = []
        n_max = 0
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        teeOA = [method, filters, prioritize_by, ascending_by, high_priority, 0., 0.*self.hours_per_night, science, n_max]
        # TOB
        science = 'TOB'
        method = 'hires-nobs=100-counts=ramp'
        filters = "photo_vetting == 'passed' and spec_vetting == 'passed' and ao_vetting != 'failed' and in_other_programs != 0 and disp != 'KP'" 
        prioritize_by = [default_priority]
        ascending_by = [True]
        high_priority = [1436.01, 1136.01, 260.01, 1807.01, 1247.01, 1473.01, 1726.01]
        no_no = [480.01, 554.01, 1410.01, 1430.01, 1437.01]
        n_max = 8
        idx = sciences.index(science)
        if no_no != []:
            for toi in no_no:
                filters += " and toi != %s"%toi
        if high_priority != []:
            for toi in high_priority:
                filters += " and toi != %s"%toi
        teeOB = [method, filters, prioritize_by, ascending_by, high_priority, hours[idx]/24., hours[idx], science, n_max]

        each = [oneA, oneB, oneC, oneD, oneE, twoA, twoBi, twoBii, twoC, three, four, teeOA, teeOB]
        cols = ['method','filter','prioritize_by','ascending_by','high_priority','total_nights','remaining_hours','name','n_maximum']
        for i in range(len(sciences)):
            programs[sciences[i]] = dict(zip(cols, each[i]))
        programs = pd.DataFrame.from_dict(programs, orient = 'index')
        programs['pick_number'] = np.zeros(len(programs)).astype('int64')
        self.programs = programs
        self.add_n_targets()

    def add_n_targets(self):
        for program in self.programs.index.values.tolist():
            if self.programs.loc[program, 'n_maximum'] != 0:
                self.programs.loc[program, 'n_targets_left'] = self.programs.loc[program, 'n_maximum']
            else:
                params = self.programs.loc[program]
                query = self.df.query(params['filter'])
                targets = list(query.toi.values.tolist() + params['high_priority'])
                targets = [int(np.floor(each)) for each in targets]
                self.programs.loc[program, 'n_targets_left'] = len(list(set(targets)))

    def get_dg_info(self, path_dg):
        df2a = pd.read_csv(path_dg)
        tics = list(set(df2a.tic.values.tolist()))
        for tic in tics:
            if tic in self.df.tic.values.tolist():
                self.df.loc[self.df['tic'] == int(tic), 'select_DG'] = 1

    def get_sc3_info(self, include_qlp = True):
        mask = None
        if not include_qlp:
            mask = self.df['source'] == 'spoc'
        self.calculate_TSM(mask = mask)
        sc3_df = self.df.copy()
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
        cols_to_use = ['toi', 'SC3_bin_rank']
        self.df = self.df.merge(sc3_df[cols_to_use], how = 'left', on = 'toi')

    def calculate_TSM(self, mask=None):
        self.df['TSM'] = [np.nan] * len(self.df)
        if mask is None:
            mask = np.ones(len(self.df), dtype=bool)
        for key in ['rp', 'mp', 'a_to_R', 'teff', 'jmag', 'r_s']:
            mask &= pd.notnull(self.df[key])
        def rp_to_scale_factor(rp):
            scale_factor = None
            if rp < 1.5:
                scale_factor = 0.19
            elif rp > 1.5 and rp < 2.75:
                scale_factor = 1.26
            elif rp > 2.75 and rp < 4:
                scale_factor = 1.28
            else:
                scale_factor = 1.15
            return scale_factor
        scale_factors = self.df.loc[mask, 'rp'].apply(rp_to_scale_factor)
        Teqs = self.df.loc[mask,'teff']*np.sqrt(np.reciprocal(self.df.loc[mask,'a_to_R'])*np.sqrt(0.25))
        numerator = scale_factors*np.power(self.df.loc[mask, 'rp'], 3)*Teqs*np.power(10, -1*self.df.loc[mask,'jmag']/5)
        denominator = self.df.loc[mask, 'mp'] * np.square(self.df.loc[mask, 'r_s'])
        self.df.loc[mask, 'TSM']  =  numerator/denominator

    def sc3_binning_function(self, df, bins, sort_val='TSM', num_to_rank=5):
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
                                (sort_val,ascending=False).iloc[0:num_to_rank]['toi'].iloc[j],'SC3_bin_rank'] = j + 1
                elif bin_items > num_to_rank:
                    for j in range(num_to_rank):
                        binned_df.loc[binned_df['toi'] == binned_df.loc[idx].sort_values\
                                (sort_val,ascending=False).iloc[0:num_to_rank]['toi'].iloc[j],'SC3_bin_rank'] = j + 1
        return binned_df

    def init_2D_filters(self, choices = {}, count = 0):
        # set up filters for a more complicated selection criteria
        # this is relevant for SC1B: whose goal is to randomly but
        # uniformly sample Rp vs Sinc (which is done by setting up
        # equal bin sizes in this parameter space, nbins=12)
        y_bins = np.arange(1,5)
        x_bins = np.logspace(0,2,5)
        science_filter = "rp > %f and rp < %f and period > %f and period < %f"
        n_bins = (len(y_bins)-1)*(len(x_bins)-1)
        for i in range(n_bins):
            x = i%(len(x_bins)-1)
            y = i%(len(y_bins)-1)
            filter = science_filter%(y_bins[y],y_bins[y+1],x_bins[x],x_bins[x+1])
            query = self.candidates.query(filter)
            query = query.drop_duplicates(subset = 'tic')
            if not query.empty:
                choices[count] = {}
                choices[count]['targets_left'] = len(query)
                choices[count]['filter'] = filter
                count += 1
        choices = pd.DataFrame.from_dict(choices, orient = 'index')
        if count != n_bins:
            choose = np.arange(1,count+1,1)
        else:
            choose = np.arange(1,n_bins+1,1)
        # it will randomize the bin filters for one entire round (using all 12 bins)
        choose = np.random.permutation(choose)[:]
        choices = choices.set_index(choose)
        choices = choices.sort_index()
        self.choices = choices
        self.sc1b_pick_number = 1

    def get_2D_filter(self):
        pick_number = self.sc1b_npick
        while True:
            n_bins = len(self.choices)
            # first check if the bin has any targets left
            if pick_number%n_bins == 0:
                # special case for the final bin in the round of choices
                check = self.choices.loc[n_bins]['targets_left']
                if check != 0:
                    # if it does, use the filter
                    filter = self.choices.loc[n_bins]['filter']
                    # reset filter choices
                    self.reset_2D_filters()
                    break
                else:
                    # if not, reset filter choices
                    self.reset_2D_filters()
            else:
                check = self.choices.loc[pick_number%n_bins]['targets_left']
                if check != 0:
                    # select filter
                    filter = self.choices.loc[pick_number%n_bins]['filter']
                    break
            # keep going until an appropriate bin/filter is selected
            pick_number += 1
        pick_number += 1
        self.sc1b_npick = pick_number
        self.sciences.loc['SC1B']['filter'] = filter

    def reset_2D_filters(self):
        # when all bins have been used, reset them (which includes randomizing them)
        new_df = self.choices.query('targets_left != 0')
        n_bins = len(new_df)
        choose = np.arange(1,n_bins+1,1)
        choose = np.random.permutation(choose)[:]
        choices = new_df.set_index(choose)
        self.choices = choices

    def check_2D_overlap(self, pick):
        # multi-planet systems (i.e. the same target) can fall into more than one bin
        # so this needs to be checked as well as the number of available targets per bin
        choices = self.choices
        tic = pick.tic
        for i in choices.index.values.tolist():
            query = self.candidates.query(choices.loc[i]['filter'])
            if tic in query.tic.values.tolist():
                choices.loc[choices.index == i, 'targets_left'] -= 1
        self.sciences.loc['SC1B', 'n_targets_left'] = np.sum(choices.targets_left.values.tolist())+1
        self.choices = choices

    def update_targets(self):
        start = np.array([0]*len(self.candidates))
        for science in self.sciences.index.values.tolist():
            start += self.candidates['in_'+science].values.tolist()
        self.candidates['in_other_programs'] = start