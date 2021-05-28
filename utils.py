import os
import datetime
import numpy as np
import pandas as pd
from observing import *
pd.set_option('mode.chained_assignment', None)


def pick_program(programs):
    """
    Given a set of programs, selects a program randomly based on the proportional time remaining 
    for each program in a Survey. This is done by creating a cumulative distribution function (CDF) 
    using all programs "remaining_hours", normalizing by the total remaining time (Ttot), then draws 
    a random number from U~[0,1), which then maps back to the list of programs.

    Parameters
    ----------
    programs : dict
        program dictionary of Survey object (must have 'remaining_hours' as a key for each program)

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


def make_data_products(survey):
    if survey.verbose:
        query = survey.df.query('in_other_programs != 0')
        query = query.drop_duplicates(subset = 'tic')
        print("  - algorithm took %d seconds to run"%(int(survey.ranking_time)))
        print('  - %d targets were selected'%len(query))
    if survey.save:
        survey = make_directory(survey)
    final = make_final(survey)
    ranking_steps = make_ranking_steps(track)
    observed = assign_priorities(survey)
    costs = final_costs(survey)
    overlap = program_overlap(survey)
    get_stats(survey, overlap, init_path)


def make_directory(survey, i=1):
    if survey.verbose:
        print('  - making data products')
    now = datetime.datetime.now()
    name = now.strftime("%B %d %Y - ")
    newdir = '%s%s%d'%(survey.outdir,name,i)
    if not os.path.exists(newdir):
        os.makedirs(newdir)
    else:
        while os.path.exists(newdir):
            i += 1
            newdir = '%s%s%d'%(survey.outdir,name,i)
        os.makedirs(newdir)
    survey.path_save = newdir
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
        survey.df.to_csv(survey.path_save+'/TOIs_perfect_final.csv', index=False)
        if survey.verbose:
            print('  - copy of updated TOI spreadsheet saved to %s'%(survey.path_save+'/TOIs_perfect_final.csv'))
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
        df.to_csv('%s/ranking_steps.csv'%survey.path_save)
        if survey.verbose:
            print('  - ranking steps of the algorithm have been saved to %s/ranking_steps.csv'%survey.path_save)
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
        observed.to_csv('%s/observing_priorities.csv'%survey.path_save, index = False)
        if survey.verbose:
            print('  - final prioritized list saved to %s/observing_priorities.csv'%survey.path_save)
    return observed

        
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