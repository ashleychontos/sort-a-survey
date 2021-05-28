import os
import datetime
import numpy as np
import pandas as pd
from scipy.optimize import brentq
pd.set_option('mode.chained_assignment', None)


def exposure_time(vmag, counts, iod=False, t1=110., v1=8., exp1=250., iodine_factor=0.7):
    """
    Exposure Time
    -------------
    Estimate exposure time based on scaling. Cannonical exposure time
    is 110s to get to 250k on 8th mag star with iodine cell in.
    
    Parameters
    ----------
    expcounts : float 
        desired number of counts. 
        250 = 250k, 10 = 10k (CKS) i.e. SNR = 45 per pixel.
    iod (bool) : is iodine cell in or out? If out, throughput is higher 
            by 30%
    
    Returns
    -------
    exptime : float
        exposure time [seconds]
    
    """

    # flux star / flux 8th mag star
    fluxfactor = 10.0**(-0.4*(vmag-v1)) 
    exptime = t1/fluxfactor 
    exptime *= counts/exp1
    if iod == False:
        exptime *= iodine_factor
    return exptime


def exposure_counts(vmag, exptime, **kwargs):
    """
    Exposure counts
    ---------------
    Inverse of `exposure_time.` Given a magnitude and an exposure
    time, how many counts will be collected?

    Parameters
    ----------
    vmag : float
        Johnson V mag
    exptime : float
        exposure time in seconds
        **kwargs : keyword arguments passed to exposure_time
    
    Returns
    -------
    counts : float
        expected number of counts (per seconds)

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
     : float
        exposure meter setting (k)

    """

    if vmag <= v1:
        return c1

    if vmag >= v2:
        return c2

    exp_level = np.interp(vmag, xp=[v1, v2], fp=[np.log10(c1), np.log10(c2)])

    return 10**exp_level



#def cost_function(sample, method, include_archival=True, overhead=2.*60, lower=3.*60, upper=20.*60):

def get_hires_time(df, method, include=True, overtime=2.*60, lower=3.*60, upper=20.*60):
    counts = method.split('=')[-1]
    nobs = int(float((method.split('-')[1]).split('=')[-1]))
    if counts == 'ramp':
        counts = exp_ramp(df['vmag'], c1=125., c2=60.)
    else:
        counts = float(counts)
    exp = exposure_time(df['vmag'], counts, iod=True)
    exp = np.clip(exp, lower, upper)
    # include archival observations
    if include:
        rem_nobs = int(nobs-df['nobs'])
        if rem_nobs < 0:
            rem_nobs = 0
            rem_time = 0.
        else:
            rem_time = exp*rem_nobs+overtime*rem_nobs
        if not df['template']:
            exp = exposure_time(df['vmag'], 250., iod=False)
            exp = np.clip(exp, 3.*60, 45.*60)
            rem_time += (exp+overtime)
    else:
        rem_time = exp*nobs+overtime*nobs
        exp = exposure_time(df['vmag'], 250., iod=False)
        exp = np.clip(exp, 3.*60, 45.*60)
        rem_time += (exp+overtime)
    return rem_time
   

def get_actual_costs(program, programs, query):
    actual_costs=[]
    for index in query.index.values.tolist():
        df = query.loc[index]
        costs = []
        for science in programs.index.values.tolist():
            if query.loc[index,'in_%s'%science]:
                time = get_hires_time(df, programs.loc[science,'method'])
                costs.append(time)
        time = get_hires_time(df, programs.loc[program,'method'])
        costs.append(time)
        if float(np.sum(costs)) != 0.:
            fraction = costs[-1]/np.sum(costs)
            actual_costs.append(fraction*max(costs))
        else:
            actual_costs.append(0.)
    query['actual_cost'] = np.array(actual_costs)
    return query


def adjust_costs(survey, pick, program):
    cases=[]
    costs=[]
    index = survey.candidates.index[survey.candidates['tic'] == int(pick.tic)].tolist()
    df_pick = survey.candidates.loc[index[0]]
    for science in survey.sciences.index.values.tolist():
        if pick['in_'+science]:
            time = get_hires_time(df_pick, survey.sciences.loc[science]['method'])
            cases.append(science)
            costs.append(time)
    cases.append(program)
    if float(np.sum(costs)) == 0.:
        net_costs = -1.*np.zeros(len(cases))
    else:
        frac = costs/np.sum(costs)
        old_costs = list((max(costs)/3600.)*frac)
        old_costs.append(0)
        time = get_hires_time(df_pick, survey.sciences.loc[program]['method'])
        costs.append(time)
        new_frac = costs/np.sum(costs)
        new_costs = np.array((max(costs)/3600.)*new_frac)
        net_costs = -1.*(new_costs - np.array(old_costs))
    net = dict(zip(cases,net_costs))
    return net


def check_observing(survey, pick, program, overtime = 2.*60):
    method = survey.sciences.loc[program, "method"]
    nobs_goal = int(float((method.split('-')[1]).split('=')[-1]))
    idx = survey.candidates.loc[survey.candidates['tic'] == int(pick.tic)].index.values.tolist()
    if nobs_goal > survey.candidates.loc[idx[0], 'nobs_goal']:
        for index in idx:
            survey.candidates.loc[index, 'nobs_goal'] = nobs_goal
    return survey