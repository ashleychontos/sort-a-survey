import os
import datetime
import numpy as np
import pandas as pd
from observing import *
pd.set_option('mode.chained_assignment', None)


def Track(object):

    def __init__(self, args, track={}):
        print('it is being initialized')
        for n in range(args.mciter):
            print(n)
            track[n] = {}
        self.track = track


    def reset_track(self, survey):
        survey.candidates = survey.df.copy()
        survey.sciences = survey.programs.copy()
        self.track[survey.n][0] = {}
        for pp, hh in zip(survey.sciences.index.values.tolist(), survey.sciences.remaining_hours.values.tolist()):
            self.track[survey.n][0][pp] = {}
            self.track[survey.n][0][pp] = round(hh, 3)
        self.track[survey.n][0]['total_time'] = round(np.sum(survey.sciences.remaining_hours.values.tolist()), 3)
        self.track = track
        self.stuck = 0
        self.stuck_sc1b = 0
        self.priority = 1
        self.i = 1
        return survey


    def add_program_pick(self, survey, pick, program):
        self.track[survey.n][self.i] = {}
        self.track[survey.n][self.i]['program'] = program
        self.track[survey.n][self.i]['program_pick'] = survey.sciences.loc[program]['pick_number']+1
        self.track[survey.n][self.i]['toi'] = float(pick.toi)
        self.track[survey.n][self.i]['tic'] = int(pick.tic)
        self.track[survey.n][self.i]['jump'] = pick.cps_name


    def update_program_hours(self, survey):
        for science, hours in zip(survey.sciences.index.values.tolist(), survey.sciences.remaining_hours.values.tolist()):
            self.track[survey.n][self.i][science] = {}
            self.track[survey.n][self.i][science] = round(hours, 3)
        self.track[survey.n][self.i]['total_time'] = round(np.sum(survey.sciences.remaining_hours.values.tolist()), 3)


    def update(self, survey, pick, program, stuck):
        if not stuck:
            # this makes sure a program has targets left
            if program == 'SC1B':
                survey.check_2D_overlap(pick)
            self.add_program_pick(self, survey, pick, program)
            survey.sciences.loc[program, "n_targets_left"] -= 1
            survey.sciences.loc[program, "pick_number"] += 1
            survey = check_observing(survey, pick, program)
            if not int(pick.in_other_programs):
                net = {program:-1.*(float(pick.actual_cost)/3600.)}
                self.track[survey.n][self.i]['overall_priority'] = self.priority
                survey.candidates.loc[survey.candidates['tic'] == int(pick.tic), 'priority'] = int(self.priority)
                self.priority += 1
            else:
                net = adjust_costs(survey, pick, program)
                idx = survey.candidates.loc[survey.candidates['tic'] == int(pick.tic)].index.values.tolist()[0]
                self.track[survey.n][self.i]['overall_priority'] = int(survey.candidates.loc[idx, 'priority'])
            for key in net.keys():
                survey.sciences.loc[key, 'remaining_hours'] += net[key]
            self.update_program_hours(survey)
            survey.candidates.loc[survey.candidates['tic'] == int(pick.tic), 'in_'+program] = 1
            survey.update_targets()
            self.i += 1
            survey.stuck = 0
        else:
            survey.stuck += 1
        return survey


def pick_program(programs):
    """Given a set of programs, selects a program randomly based on the proportional
    time remaining in each program. This is done by creating a cumulative distribution 
    function (CDF) using all programs "remaining_hours", draws a random number from U~[0,1],
    which then maps back to the list of programs.

    Parameters
    ----------
    programs : dict
        programs dict attribute of Survey object. Note: this requires the "remaining_hours"
        keyword in the programs dict

    Returns
    -------
    program : str
        the selected program which comes directly from the input programs dict keys

    """
    cdf = list(np.cumsum(programs.remaining_hours.values.tolist())/np.sum(programs.remaining_hours.values.tolist()))
    cdf.insert(0, 0.)
    pick = np.random.random()
    for i in range(len(cdf)-1):
        if cdf[i] < pick and cdf[i+1] > pick:
            break
    program = programs.index.values.tolist()[i]
    return program


def make_data_products(survey, track):
    if survey.verbose:
        if not survey.emcee:
            query = survey.df.query('in_other_programs != 0')
            query = query.drop_duplicates(subset = 'tic')
            print('  - %d targets were selected'%len(query))
        print("  - algorithm took %d seconds to run"%(int(survey.ranking_time)))
    if survey.save:
        survey = make_directory(survey)
    final = make_final(survey)
    ranking_steps = make_ranking_steps(track)
    observed = assign_priorities(survey)
    costs = final_costs(survey)
    overlap = program_overlap(survey)
    if survey.save and jump:
        jump_program(survey)
        individual_jump_programs(survey)
    if survey.ranked != {}:
        emcee_df = emcee_rankings(survey.ranked)
    get_stats(survey, overlap, init_path)


def make_directory(survey, i=1):
    if survey.verbose:
        print('  - making data products')
    now = datetime.datetime.now()
    dir = 'results/' 
    name = now.strftime("%B %d %Y - ")
    newdir = dir+name+'%d'%i
    if not os.path.exists(newdir):
        os.makedirs(newdir)
    else:
        while os.path.exists(newdir):
            i += 1
            newdir = dir+name+'%d'%i
        os.makedirs(newdir)
    survey.path = newdir
    return survey
          
  
def make_final(survey):
    changes = survey.df.query('in_SC2A == 1 and in_other_programs == 1')
    method = survey.programs.loc['SC2A', 'method']
    for i in changes.index.values.tolist():
        df_temp = changes.loc[i]
        nobs_goal = int(float((method.split('-')[1]).split('=')[-1]))
        survey.df.loc[i, "nobs_goal"] = nobs_goal
        tottime = get_hires_time(df_temp, method, include=False)
        survey.df.loc[i, "tot_time"] = round(tottime/3600.,3)
        remaining_nobs = int(nobs_goal - survey.df.loc[i, "nobs"])
        if remaining_nobs < 0:
            remaining_nobs = 0
        survey.df.loc[i, "rem_nobs"] = remaining_nobs
        lefttime = get_hires_time(df_temp, method)
        survey.df.loc[i, "rem_time"] = round(lefttime/3600.,3)
    changes = survey.df.query('in_SC4 == 1 and in_other_programs == 1')
    method = survey.programs.loc['SC4', 'method']
    for i in changes.index.values.tolist():
        df_temp = changes.loc[i]
        nobs_goal = int(float((method.split('-')[1]).split('=')[-1]))
        survey.df.loc[i, "nobs_goal"] = nobs_goal
        tottime = get_hires_time(df_temp, method, include=False)
        survey.df.loc[i, "tot_time"] = round(tottime/3600.,3)
        remaining_nobs = int(nobs_goal - survey.df.loc[i, "nobs"])
        if remaining_nobs < 0:
            remaining_nobs = 0
        survey.df.loc[i, "rem_nobs"] = remaining_nobs
        lefttime = get_hires_time(df_temp, method)
        survey.df.loc[i, "rem_time"] = round(lefttime/3600.,3)
    if survey.save:
        survey.df.to_csv(survey.path+'/TOIs_perfect_final.csv', index=False)
        if survey.verbose:
            print('  - copy of updated TOI spreadsheet saved to %s'%(survey.path+'/TOIs_perfect_final.csv'))
    final = survey.df.copy()
    return final


def get_columns(type):
    if type == 'track':
        reorder = ['program', 'program_pick', 'overall_priority', 'tic', 'toi', 'jump', 'SC1A', 'SC1B', 'SC1C', 
                   'SC1D', 'SC1E', 'SC2A', 'SC2Bi', 'SC2Bii', 'SC2C', 'SC3', 'SC4', 'TOA', 'TOB', 'total_time']
    elif type == 'costs':
        reorder = ['priority', 'tic', 'toi', 'jump', 'SC1A', 'SC1B', 'SC1C', 'SC1D', 'SC1E', 'SC2A', 'SC2Bi', 
                   'SC2Bii', 'SC2C', 'SC3', 'SC4', 'TOA', 'TOB', 'nobs_goal', 'charged_time', 'total_time']
    elif type == 'emcee':
        reorder = ['tic', 'jump', 'n_select', 'mean', 'median', 'other_programs', 'in_SC1A', 'SC1A', 'in_SC1B', 'SC1B',
                   'in_SC1C', 'SC1C', 'in_SC1D', 'SC1D', 'in_SC1E', 'SC1E', 'in_SC2A', 'SC2A', 'in_SC2Bi', 'SC2Bi',
                   'in_SC2Bii', 'SC2Bii', 'in_SC2C', 'SC2C', 'in_SC3', 'SC3', 'in_SC4', 'SC4', 'in_TOA', 'TOA', 
                   'in_TOB', 'TOB']
    elif type == 'jump':
        reorder = {'SC1A':'tks_radiusgap.txt', 'SC1B':'tks_envelopes.txt', 'SC1C':'tks_usp.txt', 
                   'SC1D':'tks_hz.txt', 'SC1E':'tks_stellarprops.txt', 'SC2A':'tks_distantgiants.txt', 
                   'SC2Bi':'tks_eccentricity.txt', 'SC2Bii':'tks_obliquity.txt', 'SC2C':'tks_multis.txt', 
                   'SC3':'tks_atmospheres.txt', 'SC4':'tks_asteroseismology.txt', 'TOA':'tks_stellarcatalog.txt', 
                   'TOB':'tks_noise.txt'}
      
  
def make_ranking_steps(track):
    track = pd.DataFrame.from_dict(track.track, orient = 'index')
    reorder = get_columns('track')
    df = pd.DataFrame(columns = reorder)
    for column in reorder:
        df[column] = track[column]
    names = df.jump.values.tolist()
    tois = df.toi.values.tolist()
    for n in range(len(names)):
        if names[n] == '-':
            names[n] = 'T%06d'%tois[n]
    names[0] = ' '
    df['jump'] = np.array(names)
    if survey.save:
        df.to_csv(survey.path+'/ranking_steps.csv')
        if survey.verbose:
            print('  - ranking steps of the algorithm have been saved to %s'%(survey.path+'/ranking_steps.csv'))
    ranking_steps = df.copy()
    return ranking_steps
    
    
def assign_priorities(survey, obs={}, m=1):
    track_sorted = survey.ranking_steps.sort_values(by = ['overall_priority'])
    for q in list(set(track_sorted.overall_priority.values.tolist())):
        if not np.isnan(q):
            prior = track_sorted[track_sorted["overall_priority"] == q]
            obs[m] = {}
            obs[m]['tic'] = int(prior.tic.values.tolist()[0])
            obs[m]['toi'] = int(np.floor(prior.toi.values.tolist()[0]))
            obs[m]['jump'] = prior.jump.values.tolist()[0]
            obs[m]['programs'] = prior.program.values.tolist()
            m += 1
    observed = pd.DataFrame.from_dict(obs, orient = 'index')
    observed.reset_index(inplace = True)
    observed = observed.rename(columns = {'index':'overall_priority'})
    if survey.save:
        observed.to_csv(survey.path+'/observing_priorities.csv', index = False)
        if survey.verbose:
            print('  - final prioritized list saved to %s'%(survey.path+'/observing_priorities.csv'))
    return observed


def jump_program(survey):
    df = pd.read_csv('info/TOIs_perfect.csv')
    df.query('finish == True', inplace=True)
    other = df.cps_name.values.tolist()
    tois = df.toi.values.tolist()
    for n in range(len(other)):
        if other[n] == '-':
            other[n] = 'T%06d'%tois[n]
    names = survey.observed.jump.values.tolist()
    names += other
    targets = sorted(names)
    f = open(survey.path+'/tks_prioritization.txt', "w")
    for target in sorted(targets):
        f.write(target+'\n')
    f.close()
    if survey.verbose:
        print('  - TKS - Prioritization saved to %s'%(survey.path+'/tks_prioritization.txt'))


def individual_jump_programs(survey):
    maps = get_columns('jump')
    for science in survey.programs.index.values.tolist():
        if science == 'TOA':
            targets = survey.observed.jump.values.tolist()
        else:
            filter = survey.overlap.query("in_%s == 'X'"%science)
            targets = filter.jump.values.tolist()
        program = sorted(targets)
        f = open(survey.path+'/%s'%maps[science], "w")
        for each in program:
            f.write(each+'\n')
        f.close()
    if survey.verbose:
        print('  - Individual jump programs have been made for each science case')
        

def final_costs(survey, costs={}):
    tics = survey.final.tic.values.tolist()
    for i, tic in enumerate(survey.observed.tic.values.tolist()):
        frac = []
        costs[i] = {}
        costs[i]['priority'] = i+1
        costs[i]['toi'] = str(int(np.floor(survey.observed.loc[i, "toi"])))
        costs[i]['tic'] = str(int(tic))
        costs[i]['jump'] = survey.observed.loc[i, "jump"]
        idx = tics.index(tic)
        nobs_goal = int(survey.final.loc[idx, "nobs_goal"])
        costs[i]['nobs_goal'] = str(nobs_goal)
        for science in survey.programs.index.values.tolist():
            cost = get_hires_time(survey.final.loc[idx], survey.programs.loc[science]['method'])
            frac.append(cost*float(survey.final.loc[idx,'in_'+science]))
        if float(np.sum(frac)) != 0.:
            fractional = frac/np.sum(frac)
        else:
            fractional = np.zeros(len(frac))
        for f, science in zip(fractional, survey.programs.index.values.tolist()):
            costs[i][science] = round(((max(frac)/3600.)*f),3)
        costs[i]['charged_time'] = round((max(frac)/3600.),3)
        if nobs_goal == 60 or nobs_goal == 100:
            total_cost = get_hires_time(survey.final.loc[idx], 'hires-nobs=%d-counts=ramp'%nobs_goal, include=False)
        else:
            total_cost = get_hires_time(survey.final.loc[idx], 'hires-nobs=%d-counts=60'%nobs_goal, include=False)
        costs[i]['total_time'] = round(total_cost/3600.,3)
    costs = pd.DataFrame.from_dict(costs, orient = 'index')
    reorder = get_columns('costs')
    df = pd.DataFrame(columns = reorder)
    for column in reorder:
        df[column] = costs[column]
    idx = len(df)
    total = df.sum(axis=0)
    df.loc[idx,'jump'] = 'Totals:'
    for science in survey.programs.index.values.tolist():
        df.loc[idx,science] = round(total[science],3)
    df.loc[idx,'charged_time'] = round(total['charged_time'],3)
    df.loc[idx,'total_time'] = round(total['total_time'],3)
    survey.charged_time = float(total['charged_time'])
    survey.total_time = float(total['total_time'])
    if survey.save:
        df.to_csv(survey.path+'/total_costs.csv', index=False)
        if survey.verbose:
            print('  - final costs saved to %s'%(survey.path+'/total_costs.csv'))
    costs = df.copy()
    return costs
        

def program_overlap(survey):
    names = ['tic', 'toi', 'jump', 'priority']
    cols = ['in_'+program for program in survey.programs.index.values.tolist()]
    df = pd.DataFrame(columns = names+cols+['total_programs'], index = survey.observed.index.values.tolist())
    for i in survey.observed.index.values.tolist():
        df_temp = survey.observed.loc[i]
        df.loc[i, 'tic'] = df_temp['tic']
        df.loc[i, 'toi'] = df_temp['toi']
        df.loc[i, 'jump'] = df_temp['jump']
        df.loc[i, 'priority'] = df_temp['overall_priority']
        for program in survey.programs.index.values.tolist():
            if program in df_temp['programs']:
                df.loc[i, 'in_'+program] = 'X'
            else:
                df.loc[i, 'in_'+program] = '-'
        df.loc[i, 'total_programs'] = len(df_temp['programs'])
    if survey.save:
        df.to_csv(survey.path+'/program_overlap.csv', index = False)
        if survey.verbose:
            print('  - spreadsheet containing program overlap saved to %s'%(survey.path+'/program_overlap.csv'))
    overlap = df.copy()
    return overlap


def emcee_rankings(ranked):
    columns = get_columns('emcee')
    selected = pd.DataFrame.from_dict(ranked, orient='index', columns=columns)
    for i in selected.index.values.tolist():
        prior = np.array(ranked[i]['priority'])
        check = len(prior)
        if check != selected.loc[i, 'n_select'] and survey.verbose:
            print('WARNING for TOI %d MC counts'%int(toi))
        selected.loc[i, 'mean'] = round(np.mean(prior),2)
        selected.loc[i, 'median'] = int(np.percentile(prior,50.))
    df = selected.sort_values(by = ['mean'], ascending = [True])
    for science in survey.programs.index.values.tolist():
        sample = Sample(df)
        relevant = sample.in_science(science)
        df[science] = relevant
    for i in df.index.values.tolist():
        total = 0
        for science in sciences:
            total += df.loc[i, science]
        df.loc[i, "other_programs"] = total
    df.to_csv(survey.path+'/TOIs_perfect_mc.csv')
    if survey.verbose:
        print('  - spreadsheet containing MC information saved to %s'%(survey.path+'/TOIs_perfect_mc.csv'))
    emcee_df = df.copy()
    return emcee_df
          
  
def get_stats(survey, overlap, init_path, note='', finish=False):
    df = pd.read_csv(survey.path_toi)
    if finish:
        df.query('finish == True', inplace=True)
    n_finish = len(df)
    time = datetime.datetime.now()
    note += time.strftime("%a %m/%d/%y %I:%M%p") + '\n'
    note += 'Seed no: %d\n'%survey.seed
    note += 'Out of the %d total targets:\n'%len(overlap)
    for science in survey.programs.index.values.tolist():
        if science == 'TOA':
            note += ' - %s has %d targets\n'%(science, len(df))
        else:
            a = df['in_'+science].values.tolist()
            d = {x:a.count(x) for x in a}
            try:
                note += ' - %s has %d targets\n'%(science, d['X'])
            except KeyError:
                note += ' - %s has %d targets\n'%(science, 0)
    f = open(survey.path+'/run_info.txt', "w")
    f.write(note)
    f.close()
    if survey.verbose:
        print('  - txt file containing run information saved to %s'%(survey.path+'/run_info.txt'))
        print('')
        print('--- process complete ---')
        print('')
        print(note)