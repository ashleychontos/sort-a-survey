import os
import datetime
import numpy as np
import pandas as pd
pd.set_option('mode.chained_assignment', None)


from sortasurvey import observing


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
    """
    After target selection process is complete, information is saved to several csvs.
    All information is stored as attributes to the Survey class but running this function
    synthesizes all the relevant information into easier-to-read files.

    Parameters
    ----------
    survey : survey.Survey
        updated Survey class object containing algorithm selections



    """
    if survey.emcee:
        if survey.verbose and survey.progress:
            survey.pbar.update(1)
        if survey.n == survey.iter:
            if survey.verbose:
                print("   - %d MC steps completed"%(int(survey.n)))
                print("   - algorithm took %d seconds to run"%(int(survey.ranking_time)))
    else:
        if survey.verbose:
            query = survey.df.query('in_other_programs != 0')
            query = query.drop_duplicates(subset = 'tic')
            print("   - algorithm took %d seconds to run"%(int(survey.ranking_time)))
            print('   - %d targets were selected'%len(query))

    if survey.save:
        if not survey.emcee:
            survey = make_directory(survey)
        else:
            if survey.n == 1:
                survey = make_directory(survey)
            if not os.path.exists('%s/%d/'%(survey.path_save,survey.n)):
                os.makedirs('%s/%d/'%(survey.path_save,survey.n))
            else:
                return
        survey = make_final_sample(survey)
        survey = make_ranking_steps(survey)
        survey = assign_priorities(survey)
        survey = final_costs(survey)
        survey = program_overlap(survey)
        get_stats(survey)


def make_directory(survey, i=1):
    """
    Makes a directory for the output files

    Parameters
    ----------
    survey : survey.Survey
        updated Survey class object containing algorithm selections

    Returns
    -------
    survey : survey.Survey
        updated Survey class object with the new 'path_save' attribute

    """
    if survey.verbose and not survey.emcee:
        print('   - Making data products, including:')
    now = datetime.datetime.now()
    name = now.strftime("%m-%d-%y")
    newdir = '%s/%s-%d'%(survey.outdir,name,i)
    if not os.path.exists(newdir):
        os.makedirs(newdir)
    else:
        while os.path.exists(newdir):
            i += 1
            newdir = '%s/%s-%d'%(survey.outdir,name,i)
        os.makedirs(newdir)
    survey.path_save = newdir
    return survey
          
  
def make_final_sample(survey, cols_to_drop=['select_DG','TSM','SC3_bin_rank','drop','false','n_select']):
    """
    Makes a directory for the output files

    Parameters
    ----------
    survey : survey.Survey
        updated Survey class object containing algorithm selections

    Returns
    -------
    survey : survey.Survey
        updated Survey class object with the new 'path_save' attribute

    """
    # SC2A has a very different observing approach than a majority of TKS programs
    changes = survey.df.query('in_SC2A == 1 and in_other_programs == 1')
    method = survey.programs.loc['SC2A', 'method']
    for i in changes.index.values.tolist():
        df_temp = changes.loc[i]
        nobs_goal = int(float((method.split('-')[1]).split('=')[-1]))
        survey.df.loc[i, "nobs_goal"] = nobs_goal
        tottime = observing.cost_function(df_temp, method, include_archival=False)
        survey.df.loc[i, "tot_time"] = round(tottime/3600.,3)
        remaining_nobs = int(nobs_goal - survey.df.loc[i, "nobs"])
        if remaining_nobs < 0:
            remaining_nobs = 0
        survey.df.loc[i, "rem_nobs"] = remaining_nobs
        lefttime = observing.cost_function(df_temp, method)
        survey.df.loc[i, "rem_time"] = round(lefttime/3600.,3)
    # same for SC4 (evolved)
    changes = survey.df.query('in_SC4 == 1 and in_other_programs == 1')
    method = survey.programs.loc['SC4', 'method']
    for i in changes.index.values.tolist():
        df_temp = changes.loc[i]
        nobs_goal = int(float((method.split('-')[1]).split('=')[-1]))
        survey.df.loc[i, "nobs_goal"] = nobs_goal
        tottime = observing.cost_function(df_temp, method, include_archival=False)
        survey.df.loc[i, "tot_time"] = round(tottime/3600.,3)
        remaining_nobs = int(nobs_goal - survey.df.loc[i, "nobs"])
        if remaining_nobs < 0:
            remaining_nobs = 0
        survey.df.loc[i, "rem_nobs"] = remaining_nobs
        lefttime = observing.cost_function(df_temp, method)
        survey.df.loc[i, "rem_time"] = round(lefttime/3600.,3)
    # we need to also add in our RM targets
    for target in survey.programs.loc['SC2Bii', 'high_priority']:
        survey.df.loc[survey.df['toi'] == target,'in_SC2Bii'] = 1
        if np.isnan(survey.df.loc[survey.df['toi'] == target, 'priority'].values.tolist()[0]):
            survey.df.loc[survey.df['toi'] == target, 'priority'] = survey.df['priority'].max()+1
    start = np.array([0]*len(survey.df))
    for science in survey.programs.index.values.tolist():
        start += survey.df['in_%s'%science].values.tolist()
    survey.df['in_other_programs'] = start
    survey.df.drop(columns=cols_to_drop, errors='ignore', inplace=True)
    if survey.save:
        if survey.emcee:
            survey.df.to_csv('%s/%d/TOIs_perfect_final.csv'%(survey.path_save, survey.n), index=False)
        else:
            survey.df.to_csv('%s/%s_final.csv'%(survey.path_save, (survey.path_sample.split('/')[-1]).split('.')[0]), index=False)
        if survey.verbose and not survey.emcee:
            print('     - a copy of the updated sample')
    survey.final = survey.df.copy()
    return survey
      
  
def make_ranking_steps(survey):
    """
    Saves every step of the target selection process, referred to as the 'track'
    (and is actually the attribute it is saved as in the Survey). This is saved
    as 'ranking_steps.csv' to the current run's 'path_save' directory.

    Parameters
    ----------
    survey : survey.Survey
        Survey class object containing algorithm selections

    Returns
    -------
    survey : survey.Survey
        updated Survey class object with the new 'ranking_steps' attribute

    """
    reorder = get_columns('track', survey.sciences.name.values.tolist())
    track = pd.DataFrame.from_dict(survey.track[survey.n], orient='index')
    df = pd.DataFrame(columns = reorder)
    for column in reorder:
        df[column] = track[column]
    tois = [int(target) for target in df.toi.values.tolist()]
    idx = len(df)
    for t, target in enumerate(survey.programs.loc['SC2Bii', 'high_priority']):
        idx = len(df)
        df.loc[idx+t,'program'] = 'SC2Bii'
        df.loc[idx+t,'program_pick'] = t+1
        df.loc[idx+t,'toi'] = target
        df.loc[idx+t,'tic'] = survey.df[survey.df['toi'].isin([target])]['tic'].values.tolist()[0]
        if int(np.floor(target)) not in tois:
            df.loc[idx+t,'overall_priority'] = int(df['overall_priority'].max()+1)
        else:
            new=tois.index(int(np.floor(target)))
            df.loc[idx+t,'overall_priority'] = df.loc[new,'overall_priority']
            df.loc[idx+t,'tic'] = df.loc[new,'tic']
        for program in survey.programs.index.values.tolist():
            df.loc[idx+t,program] = df.loc[idx-1,program]
        df.loc[idx+t,'total_time'] = df.loc[idx-1,'total_time']
    if survey.save:
        if survey.emcee:
            df.to_csv('%s/%d/ranking_steps.csv'%(survey.path_save,survey.n))
        else:
            df.to_csv('%s/ranking_steps.csv'%survey.path_save)
        if survey.verbose and not survey.emcee:
            print('     - algorithm history (via ranking steps)')
    survey.ranking_steps = df.copy()
    return survey
    
    
def assign_priorities(survey, obs={}, m=1):
    """
    In summary, this transforms the ranking steps into a final prioritized list.
    This module takes all information from a single algorithm iteration i.e. a 
    complete survey selection process from start to finish and synthesizes it into 
    a single prioritized target list, including all programs that selected a
    given target and the final overall target priorities.

    Parameters
    ----------
    survey : survey.Survey
        Survey class object containing the 'ranking_steps' history

    Returns
    -------
    survey : survey.Survey
        updated Survey class object with the newly prioritized 'observed' list

    """
    track_sorted = survey.ranking_steps.sort_values(by = ['overall_priority'])
    for q in list(set(track_sorted.overall_priority.values.tolist())):
        if int(q) != 0:
            prior = track_sorted[track_sorted["overall_priority"] == q]
            obs[m] = {}
            obs[m]['tic'] = int(prior.tic.values.tolist()[0])
            obs[m]['toi'] = int(np.floor(prior.toi.values.tolist()[0]))
            obs[m]['programs'] = prior.program.values.tolist()
            m += 1
    observed = pd.DataFrame.from_dict(obs, orient='index')
    observed.reset_index(inplace = True)
    observed = observed.rename(columns = {'index':'overall_priority'})
    if survey.save:
        if survey.emcee:
            observed.to_csv('%s/%d/observing_priorities.csv'%(survey.path_save,survey.n))
        else:
            observed.to_csv('%s/observing_priorities.csv'%survey.path_save, index = False)
        if survey.verbose and not survey.emcee:
            print('     - the final prioritized list (via observing priorities)')
    survey.observed = observed.copy()
    return survey

        
def final_costs(survey, costs={}):
    """
    Computes the individual costs of all selected targets for a program, 
    which incorporates both existing archival data and shared costs. Think
    of this as an itemized receipt for all targets and all programs in a
    survey.

    Parameters
    ----------
    survey : survey.Survey
        Survey class object containing the final prioritized 'observed' list

    Returns
    -------
    survey : survey.Survey
        updated Survey class object containing the final costs of all selected targets per program

    """
    tics = survey.final.tic.values.tolist()
    for i, tic in enumerate(survey.observed.tic.values.tolist()):
        frac = []
        costs[i] = {}
        costs[i]['priority'] = i+1
        costs[i]['toi'] = str(int(np.floor(survey.observed.loc[i, "toi"])))
        costs[i]['tic'] = str(int(tic))
        idx = tics.index(tic)
        nobs_goal = int(survey.final.loc[idx, "nobs_goal"])
        costs[i]['nobs_goal'] = str(nobs_goal)
        for science in survey.programs.index.values.tolist():
            cost = observing.cost_function(survey.final.loc[idx], survey.programs.loc[science]['method'])
            frac.append(cost*float(survey.final.loc[idx,'in_'+science]))
        if float(np.sum(frac)) != 0.:
            fractional = frac/np.sum(frac)
        else:
            fractional = np.zeros(len(frac))
        for f, science in zip(fractional, survey.programs.index.values.tolist()):
            costs[i][science] = round(((max(frac)/3600.)*f),3)
        costs[i]['charged_time'] = round((max(frac)/3600.),3)
        if nobs_goal == 60 or nobs_goal == 100:
            total_cost = observing.cost_function(survey.final.loc[idx], 'hires-nobs=%d-counts=ramp'%nobs_goal, include_archival=False)
        else:
            total_cost = observing.cost_function(survey.final.loc[idx], 'hires-nobs=%d-counts=60'%nobs_goal, include_archival=False)
        costs[i]['total_time'] = round(total_cost/3600.,3)
    costs = pd.DataFrame.from_dict(costs, orient = 'index')
    reorder = get_columns('costs', survey.sciences.name.values.tolist())
    df = pd.DataFrame(columns = reorder)
    for column in reorder:
        df[column] = costs[column]
    idx = len(df)
    total = df.sum(axis=0)
    df.loc[idx,'tic'] = 'Totals:'
    for science in survey.programs.index.values.tolist():
        df.loc[idx,science] = round(total[science],3)
    df.loc[idx,'charged_time'] = round(total['charged_time'],3)
    df.loc[idx,'total_time'] = round(total['total_time'],3)
    survey.charged_time = float(total['charged_time'])
    survey.total_time = float(total['total_time'])
    if survey.save:
        if survey.emcee:
            df.to_csv('%s/%d/total_costs.csv'%(survey.path_save,survey.n), index=False)
        else:
            df.to_csv('%s/total_costs.csv'%survey.path_save, index=False)
        if survey.verbose and not survey.emcee:
            print('     - final costs saved')
    survey.costs = df.copy()
    return survey
        

def program_overlap(survey):
    """
    From the final selected list, this is a simple csv that shows 
    the overlap of survey targets and programs

    Parameters
    ----------
    survey : survey.Survey
        Survey class object containing the final prioritized 'observed' list

    Returns
    -------
    survey : survey.Survey
        updated Survey with the overlap of targets and programs

    """
    columns = get_columns('overlap', survey.sciences.name.values.tolist())
    df = pd.DataFrame(columns = columns, index = survey.observed.index.values.tolist())
    for i in survey.observed.index.values.tolist():
        df_temp = survey.observed.loc[i]
        df.loc[i, 'tic'] = df_temp['tic']
        df.loc[i, 'toi'] = df_temp['toi']
        df.loc[i, 'priority'] = df_temp['overall_priority']
        for program in survey.programs.index.values.tolist():
            if program in df_temp['programs']:
                df.loc[i, 'in_'+program] = 'X'
            else:
                df.loc[i, 'in_'+program] = '-'
        df.loc[i, 'total_programs'] = len(df_temp['programs'])
    if survey.save:
        if survey.emcee:
            df.to_csv('%s/%d/program_overlap.csv'%(survey.path_save,survey.n))
        else:
            df.to_csv('%s/program_overlap.csv'%survey.path_save, index = False)
        if survey.verbose and not survey.emcee:
            print('     - program overlap')
    survey.overlap = df.copy()
    return survey


def emcee_rankings(survey):
    """
    TODO: synthesizes the selected lists across all MC iterations and counts
    the number of times a target was selected (per number of iterations)

    Parameters
    ----------
    survey : survey.Survey
        Survey class object containing the final prioritized 'observed' list

    Returns
    -------
    survey : survey.Survey
        updated Survey with the overlap of targets and programs

    """
    columns = get_columns('emcee', survey.sciences.name.values.tolist())
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
    df.to_csv('%s/TOIs_perfect_mc.csv'%survey.path_save)
    if survey.verbose:
        print('     - spreadsheet containing MC information saved')
    emcee_df = df.copy()
    return emcee_df
          
  
def get_stats(survey, note='', output='', finish=False):
    """
    Logs information from the run necessary to reproduce the sample,
    i.e. seed number, any special science cases, any ignored science 
    cases, etc.

    Parameters
    ----------
    survey : survey.Survey
        Survey class object containing the final prioritized 'observed' list
    note : str
        logs all relevant information and will save this as a basic text file
    finish : bool
        todo

    """
    if finish:
        df = pd.read_csv(survey.path_sample)
        df.query('finish == True', inplace=True)
        n_finish = len(df)
    df = survey.overlap.copy()
    time = datetime.datetime.now()
    note += time.strftime("%a %m/%d/%y %I:%M%p") + '\n'
    output += time.strftime("%a %m/%d/%y %I:%M%p") + '\n\n'
    note += 'Seed no: %d\n'%survey.seeds[survey.n-1]
    note += 'Out of the %d total targets:\n'%len(df)
    output += 'Out of the %d total targets:\n'%len(df)
    for science in survey.programs.index.values.tolist():
        if science == 'TOA':
            note += '  - %s has %d targets\n'%(science, len(df))
            output += '  - %s has %d targets\n'%(science, len(df))
        else:
            a = df['in_'+science].values.tolist()
            d = {x:a.count(x) for x in a}
            try:
                note += '  - %s has %d targets\n'%(science, d['X'])
                output += '  - %s has %d targets\n'%(science, d['X'])
            except KeyError:
                note += '  - %s has %d targets\n'%(science, 0)
                output += '  - %s has %d targets\n'%(science, 0)
    if survey.save:
        if survey.emcee:
            f = open('%s/%d/run_info.txt'%(survey.path_save,survey.n), "w")
        else:
            f = open('%s/run_info.txt'%survey.path_save, "w")
        f.write(note)
        f.close()
        if survey.verbose and not survey.emcee:
            print('     - txt file w/ run info')
            print('\n ------------------------------')
            print(' ----- process - complete -----')
            print(' ------------------------------')
            print('')
            print(output)


def get_columns(type, sciences):
    """
    Get the relevant columns for different output files.

    Parameters
    ----------
    type : str
        which output file the columns are needed for, options are ['track', 'costs', 'overlap']
    sciences : List[str]
        the list of programs in the survey

    Returns
    -------
    program : str
        the selected program which comes directly from the input programs dict keys

    """
    if type == 'track':
        columns = ['program', 'program_pick', 'overall_priority', 'tic', 'toi'] + sciences + ['total_time']
    elif type == 'costs':
        columns = ['priority', 'tic', 'toi'] + sciences + ['nobs_goal', 'charged_time', 'total_time']
    elif type == 'overlap':
        columns = ['tic', 'toi', 'priority'] + ['in_%s'%program for program in sciences] + ['total_programs']
    else:
        columns = []
    return columns