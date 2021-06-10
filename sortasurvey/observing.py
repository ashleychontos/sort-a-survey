import numpy as np
import pandas as pd
from scipy.optimize import brentq
pd.set_option('mode.chained_assignment', None)



def cost_function(df, method, include_archival=True, overhead=2.*60, lower=3.*60, upper=20.*60):
    """
    Estimates the total amount of time needed on sky for a given target, which 
    is highly dependent on the instrument using to collect the data

    Parameters
    ----------
    df : pandas.DataFrame
        dataframe containing a target's vmag and other required information in the cost function
    method : str
        observing method of a particular program
    
    Returns
    -------
    rem_time : float
        the remaining time (in seconds) needed to achieve your specified science.

    """

    counts = method.split('=')[-1]
    nobs = int(float((method.split('-')[1]).split('=')[-1]))
    if counts == 'ramp':
        counts = exp_ramp(df['vmag'], c1=125., c2=60.)
    else:
        counts = float(counts)
    # estimate how much time a target would take, given a program's observing method
    exp = exposure_time(df['vmag'], counts, iodine=True)
    # make a cut at a survey's maximum allowable exposure time per observation
    exp = np.clip(exp, lower, upper)
    # include archival data in total time estimates
    if include_archival:
        rem_nobs = int(nobs-df['nobs'])
        if rem_nobs < 0:
            rem_nobs = 0
            rem_time = 0.
        else:
            rem_time = exp*rem_nobs+overhead*rem_nobs
        # if a template has not been acquired for a target yet
        if not df['template']:
            exp = exposure_time(df['vmag'], 250., iodine=False)
            exp = np.clip(exp, 3.*60, 45.*60)
            rem_time += (exp+overhead)
    else:
        # if not including archival data, consider the time to acquire a template
        rem_time = exp*nobs+overhead*nobs
        exp = exposure_time(df['vmag'], 250., iodine=False)
        exp = np.clip(exp, 3.*60, 45.*60)
        rem_time += (exp+overhead)
    return rem_time


def exposure_time(vmag, counts, iodine=False, t1=110., v1=8., exp1=250., iodine_factor=0.7):
    """
    Expected exposure time based on the scaling from a canonical exposure time
    of 110s to get to 250k on 8th mag star with the iodine cell in the light
    path
    
    Parameters
    ----------
    expcounts : float 
        desired number of counts 
        250 = 250k, 10 = 10k (CKS) i.e. SNR = 45 per pixel.
    iodine (bool) : is iodine cell in or out? If out, throughput is higher by 30%
    
    Returns
    -------
    exptime : float
        exposure time [seconds]
    
    """

    # flux star / flux 8th mag star
    fluxfactor = 10.0**(-0.4*(vmag-v1)) 
    exptime = t1/fluxfactor 
    exptime *= counts/exp1
    if iodine == False:
        exptime *= iodine_factor
    return exptime


def exposure_counts(vmag, exptime):
    """
    Inverse of `exposure_time.` Given a magnitude and an exposure
    time, how many counts will be collected?

    Parameters
    ----------
    vmag : float
        Johnson V mag
    exptime : float
        exposure time in seconds
    
    Returns
    -------
    counts : float
        expected number of photon counts (x1000)

    """

    f = lambda expcounts : exposure_time(vmag, expcounts, **kwargs) - exptime
    _counts = brentq(f,0,200000,)

    return _counts


def exp_ramp(vmag, v1=10.5, v2=12.0, c1=250., c2=60.):
    """
    Calculates exposure counts based on a minimum (v1) and maximum (v2)
    magnitude limits, with a linear ramp between the two magnitude limits.

    Parameters
    ----------
    vmag : float 
        target magnitude
    v1 : float 
        below this mag targets get full counts (c1)
    v2 : float
        fainter than this mag targets get c2
    c1 : float
        expcounts (k) for bright targets
    c2 : float
        expcounts (k) for the faint limit

    Returns
    -------
    counts : float
        expected number of photon counts (x1000)

    """
    if vmag <= v1:
        return c1
    if vmag >= v2:
        return c2

    exp_level = np.interp(vmag, xp=[v1, v2], fp=[np.log10(c1), np.log10(c2)])
    counts = 10.**exp_level

    return counts

   

def get_actual_costs(program, programs, query):
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
    actual_costs=[]
    for index in query.index.values.tolist():
        df = query.loc[index]
        costs = []
        for science in programs.index.values.tolist():
            if query.loc[index,'in_%s'%science]:
                time = cost_function(df, programs.loc[science,'method'])
                costs.append(time)
        time = cost_function(df, programs.loc[program,'method'])
        costs.append(time)
        if float(np.sum(costs)) != 0.:
            fraction = costs[-1]/np.sum(costs)
            actual_costs.append(fraction*max(costs))
        else:
            actual_costs.append(0.)
    query['actual_cost'] = np.array(actual_costs)
    return query


def adjust_costs(survey, pick, program):
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
    cases=[]
    costs=[]
    index = survey.candidates.index[survey.candidates['tic'] == int(pick.tic)].tolist()
    df_pick = survey.candidates.loc[index[0]]
    for science in survey.sciences.index.values.tolist():
        if pick['in_%s'%science]:
            time = cost_function(df_pick, survey.sciences.loc[science]['method'])
            cases.append(science)
            costs.append(time)
    cases.append(program)
    if float(np.sum(costs)) == 0.:
        net_costs = -1.*np.zeros(len(cases))
    else:
        frac = costs/np.sum(costs)
        old_costs = list((max(costs)/3600.)*frac)
        old_costs.append(0)
        time = cost_function(df_pick, survey.sciences.loc[program]['method'])
        costs.append(time)
        new_frac = costs/np.sum(costs)
        new_costs = np.array((max(costs)/3600.)*new_frac)
        net_costs = -1.*(new_costs - np.array(old_costs))
    net = dict(zip(cases,net_costs))
    return net


def check_observing(survey, pick, program):
    """
    Based on programs that have selected a given target, this will figure out which
    observing method requires the most observing time and then scales other program's
    costs based on that.

    Parameters
    ----------
    survey : survey.Survey
        class object containing both the vetted sample (via survey.candidates) and the
        survey programs (via survey.sciences)
    pick : pandas.DataFrame
        a single row dataframe containing information on the selected program's current pick
    program: str
        the selected program
    
    Returns
    -------
    survey : survey.Survey
        class object with updated nobs_goal information, if applicable
    """
    method = survey.sciences.loc[program, "method"]
    nobs_goal = int(float((method.split('-')[1]).split('=')[-1]))
    idx = survey.candidates.loc[survey.candidates['tic'] == int(pick.tic)].index.values.tolist()
    if nobs_goal > survey.candidates.loc[idx[0], 'nobs_goal']:
        for index in idx:
            survey.candidates.loc[index, 'nobs_goal'] = nobs_goal
    return survey