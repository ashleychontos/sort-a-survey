#!/usr/local/bin/python

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import MultipleLocator

import warnings
warnings.filterwarnings('ignore')
plt.rcParams['mathtext.fontset'] = 'stix'




def main(show = False, save = True, all = False, case = [], label_size = 28., 
         tick_size = 22., legend_size = 24., marker_size = 100., marker_scale = 1.25):

    path = 'results/other/2020/August 21 - 11/'
    summary_plots(path, show, save, marker_scale, marker_size, 22., 18., 24.)
    make_stacked(path, show, save, label_size, tick_size, legend_size, marker_scale)
    make_single_plots(path, show, save, all, case, label_size, tick_size, legend_size, marker_size, marker_scale)

    return


##########################################################################################
#                                                                                        #
#                                    PLOT FUNCTIONS                                      #
#                                                                                        #
##########################################################################################


def make_stacked(path, show, save, label_size, tick_size, legend_size, marker_scale, parameter = 'rp'):

    df = pd.read_csv(path+'TOIs_perfect_final.csv')
    good = df.query("photo_vetting == 'passed' and spec_vetting != 'failed' and spec_vetting != 'do not observe'")
    sciences = ['SC1A', 'SC1B', 'SC1C', 'SC1D', 'SC1E', 'SC2A', 'SC2Bi', 'SC2Bii', 'SC2C',
                'SC3', 'SC4']
    colors = []
    labels = []

    full = df.query("in_other_programs != 0")

    params = full[parameter].values.tolist()
    bins = list(np.logspace(0, np.log10(20.), 20))

    values = []
    for science in sciences:
        program = good.query("in_%s == 1"%science)
        param = program[parameter].values.tolist()
        values.append(param)

    labels = [r'$\rm %s$'%science for science in sciences]
    xlabels = [r'$%.1f$'%bin for bin in bins]

    plt.figure(figsize = (14,8))
    ax = plt.subplot(1, 1, 1)

    ax.hist(values, bins = bins, histtype = 'step', stacked = True, lw = 2.5, label = labels, zorder = 3)
    ax.set_xlabel(r'$\rm R_{p} \; [R_{\oplus}]$', fontsize = label_size)
    ax.legend(fontsize = legend_size, facecolor = 'w', framealpha = 1.0, markerscale = marker_scale, loc = 'center left', bbox_to_anchor = (1, 0.5))
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.set_xticks(bins)
    ax.set_xticklabels(xlabels)
    ax.xaxis.grid(True, which = 'major', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.yaxis.grid(True, which = 'major', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.yaxis.grid(True, which = 'minor', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.tick_params(axis = 'x', which = 'minor', bottom = False)
    ax.tick_params(axis = 'x', which = 'major', top = True, zorder = 7)
    ax.tick_params(axis = 'x', which = 'major', length = 8, width = 1, direction = 'inout', zorder = 7)
    ax.tick_params(axis = 'y', which = 'both', right = True)
    ax.tick_params(labelsize = tick_size)
    loc, lab = plt.yticks()
    ylabels = []
    for l in loc:
        ylabels.append(r'$%d$'%int(l))
    ax.set_yticklabels(ylabels)
    plt.tight_layout()
    if save:
        plt.savefig('results/plots/step_hist_summary.png', dpi = 250)
    if show:
        plt.show()
    plt.close()


    plt.figure(figsize = (14,8))
    ax = plt.subplot(1, 1, 1)

    ax.hist(values, bins = bins, histtype = 'stepfilled', stacked = True, lw = 2.5, label = labels, zorder = 3)
    ax.set_xlabel(r'$\rm R_{p} \; [R_{\oplus}]$', fontsize = label_size)
    ax.legend(fontsize = legend_size, facecolor = 'w', framealpha = 1.0, markerscale = marker_scale, loc = 'center left', bbox_to_anchor = (1, 0.5))
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.set_xticks(bins)
    ax.set_xticklabels(xlabels)
    ax.xaxis.grid(True, which = 'major', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.yaxis.grid(True, which = 'major', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.yaxis.grid(True, which = 'minor', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.tick_params(axis = 'x', which = 'minor', bottom = False)
    ax.tick_params(axis = 'x', which = 'major', top = True, zorder = 7)
    ax.tick_params(axis = 'x', which = 'major', length = 8, width = 1, direction = 'inout', zorder = 7)
    ax.tick_params(axis = 'y', which = 'both', right = True)
    ax.tick_params(labelsize = tick_size)
    loc, lab = plt.yticks()
    ylabels = []
    for l in loc:
        ylabels.append(r'$%d$'%int(l))
    ax.set_yticklabels(ylabels)
    plt.tight_layout()
    if save:
        plt.savefig('results/plots/bar_hist_summary.png', dpi = 250)
    if show:
        plt.show()
    plt.close()

    return


def summary_plots(path, show, save, marker_scale, marker_size, label_size, tick_size, legend_size):

    df = pd.read_csv(path+'TOIs_perfect_final.csv')
    df2 = df.query("photo_vetting == 'passed' and spec_vetting != 'failed' and spec_vetting != 'do not observe'")
    df3 = pd.read_csv(path+'observing_priorities.csv')
    filter = df['tic'].isin(df3.tic.values.tolist())
    df3 = df[filter]

    fig = plt.figure(figsize = (18,10))

    # vmag
    vmag_all = df.vmag.values.tolist()
    vmag_some = df2.vmag.values.tolist()
    vmag_before = df3.vmag.values.tolist()
    bins = np.arange(5.5, 13.5, 0.25)

    ax = fig.add_subplot(3, 3, 1)
    ax.hist(vmag_all, bins = bins, facecolor = '0.75', zorder = 0)
    ax.hist(vmag_some, bins = bins, facecolor = 'k', zorder = 1)
    ax.hist(vmag_before, bins = bins, color = 'red', histtype = 'step', lw = 2.5, zorder = 2)
    ax.set_ylabel(r'$\rm V_{mag}$', fontsize = label_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.xaxis.set_minor_locator(MultipleLocator(0.5))
    ax.xaxis.set_major_locator(MultipleLocator(1.0))
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([6., 8., 10., 12.])
    ax.set_xticklabels([r'$6$', r'$8$', r'$10$', r'$12$'])


    # Teff
    teff_all = df.t_eff.values.tolist()
    teff_some = df2.t_eff.values.tolist()
    teff_before = df3.t_eff.values.tolist()
    bins = np.arange(3000., 8100., 250.)

    ax = fig.add_subplot(3, 3, 2)
    ax.hist(teff_all, bins = bins, facecolor = '0.75')
    ax.hist(teff_some, bins = bins, facecolor = 'k')
    ax.hist(teff_before, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$\rm Teff \; [K]$', fontsize = label_size)
    plt.xlim(2750.,8250.)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.xaxis.set_minor_locator(MultipleLocator(250))
    ax.xaxis.set_major_locator(MultipleLocator(1000))
    ax.tick_params(labelsize = tick_size)
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([3000., 4000., 5000., 6000., 7000., 8000.])
    ax.set_xticklabels([r'$3000$', r'$4000$', r'$5000$', r'$6000$', r'$7000$', r'$8000$'])


    # vsini
    vsini_all = np.array(df.vsini.values.tolist())
    mask = np.ma.getmask(np.ma.masked_invalid(vsini_all))
    vsini_all = list(vsini_all[~mask])
    vsini_some = np.array(df2.vsini.values.tolist())
    mask = np.ma.getmask(np.ma.masked_invalid(vsini_some))
    vsini_some = list(vsini_some[~mask])
    vsini_before = np.array(df3.vsini.values.tolist())
    mask = np.ma.getmask(np.ma.masked_invalid(vsini_before))
    vsini_before = list(vsini_before[~mask])
    bins = np.logspace(-1., np.log10(20.), 20)

    ax = fig.add_subplot(3, 3, 3)
    ax.hist(vsini_all, bins = bins, facecolor = '0.75')
    ax.hist(vsini_some, bins = bins, facecolor = 'k')
    ax.hist(vsini_before, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$v\,\sin\,i \; [\rm{km s}^{-1}]$', fontsize = label_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([0.1, 0.3, 1.0, 3., 10.])
    ax.set_xticklabels([r'$0.1$', r'$0.3$', r'$1$', r'$3$', r'$10$'])


    # Rs
    rs_all = df.r_s.values.tolist()
    rs_some = df2.r_s.values.tolist()
    rs_before = df3.r_s.values.tolist()
    bins = np.logspace(-1., 1., 30)

    ax = fig.add_subplot(3, 3, 4)
    ax.hist(rs_all, bins = bins, facecolor = '0.75')
    ax.hist(rs_some, bins = bins, facecolor = 'k')
    ax.hist(rs_before, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$\rm R_{\star} \; [R_{\odot}]$', fontsize = label_size)
    plt.xlim(0.3,11.)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([0.5, 1.0, 3., 10.])
    ax.set_xticklabels([r'$0.5$', r'$1$', r'$3$', r'$10$'])


    # Rp
    rp_all = df.rp.values.tolist()
    rp_some = df2.rp.values.tolist()
    rp_before = df3.rp.values.tolist()
    bins = np.logspace(-0.5, 2., 30)

    ax = fig.add_subplot(3, 3, 5)
    ax.hist(rp_all, bins = bins, facecolor = '0.75')
    ax.hist(rp_some, bins = bins, facecolor = 'k')
    ax.hist(rp_before, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$\rm R_{p} \; [R_{\oplus}]$', fontsize = label_size)
    plt.xlim(0.7,30.)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([1., 3., 10., 30.])
    ax.set_xticklabels([r'$1$', r'$3$', r'$10$', r'$30$'])


    # Incident flux
    sinc_all = np.array(df.sinc.values.tolist())
    mask = np.ma.getmask(np.ma.masked_invalid(sinc_all))
    mask_1 = ~mask
    mask_2 = np.ma.getmask(np.ma.masked_greater(sinc_all, 0.))
    maskk = mask_1*mask_2
    sinc_all = list(sinc_all[maskk])
    sinc_some = np.array(df2.sinc.values.tolist())
    mask = np.ma.getmask(np.ma.masked_invalid(sinc_some))
    mask_1 = ~mask
    mask_2 = np.ma.getmask(np.ma.masked_greater(sinc_some, 0.))
    maskk = mask_1*mask_2
    sinc_some = list(sinc_some[maskk])
    sinc_before = np.array(df3.sinc.values.tolist())
    mask = np.ma.getmask(np.ma.masked_invalid(sinc_before))
    mask_1 = ~mask
    mask_2 = np.ma.getmask(np.ma.masked_greater(sinc_before, 0.))
    maskk = mask_1*mask_2
    sinc_before = list(sinc_before[maskk])

    bins = np.logspace(-1, 5.5, 30)

    ax = fig.add_subplot(3, 3, 6)
    ax.hist(sinc_all, bins = bins, facecolor = '0.75', label = r'$\rm Full \; [%s]$'%(str(int(len(df)))))
    ax.hist(sinc_some, bins = bins, facecolor = 'k', label = r'$\rm Vetted \; [%s]$'%(str(int(len(df2)))))
    ax.hist(sinc_before, bins = bins, color = 'red', histtype = 'step', lw = 2.5, label = r'$\rm Selected \; [%s]$'%(str(int(len(df3)))))
    ax.set_ylabel(r'$\rm F_{p} \; [F_{\oplus}]$', fontsize = label_size)
    plt.xlim(1e5,0.1)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([100000., 10000., 1000., 100., 10., 1.])
    ax.set_xticklabels([r'$10^5$', r'$10^4$', r'$10^3$', r'$10^2$', r'$10^1$', r'$10^0$'])
    ax.legend(fontsize = legend_size, loc = 'center left', bbox_to_anchor = (1, 0.5), markerscale = marker_scale)


    # K/sigma_K
    ksig_all = df.ksig.values.tolist()
    ksig_some = df2.ksig.values.tolist()
    ksig_before = df3.ksig.values.tolist()
    bins = np.logspace(0, 2, 20)

    ax = fig.add_subplot(3, 3, 7)
    ax.hist(ksig_all, bins = bins, facecolor = '0.75')
    ax.hist(ksig_some, bins = bins, facecolor = 'k')
    ax.hist(ksig_before, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.axvline(3., color = 'darkorange', ls = '--', lw = 1.5)
    ax.axvline(5., color = 'green', ls = '-.', lw = 1.5)
    ax.set_ylabel(r'$\rm K/\sigma_{K}$', fontsize = label_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    plt.xlim(1.,120.)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([1., 3., 10., 30., 100.])
    ax.set_xticklabels([r'$1$', r'$3$', r'$10$', r'$30$', r'$100$'])


    # total time (hours)
    time_all = np.array(df.tot_time.values.tolist())
    time_some = np.array(df2.tot_time.values.tolist())
    time_before = np.array(df3.tot_time.values.tolist())
    bins = np.logspace(np.log10(5.), np.log10(35.), 20)

    ax = fig.add_subplot(3, 3, 8)
    ax.hist(time_all, bins = bins, facecolor = '0.75')
    ax.hist(time_some, bins = bins, facecolor = 'k')
    ax.hist(time_before, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$\rm Total \; time \; [hours]$', fontsize = label_size)
    plt.xlim(4.8,35.5)
    ax.set_xscale("log")
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([6., 10., 15., 20., 30.])
    ax.set_xticklabels([r'$6$', r'$10$', r'$15$', r'$20$', r'$30$'])


    # n programs
    df6 = pd.read_csv(path+'program_overlap.csv')
    totals_after = df6.total_programs.values.tolist()
    counts_after = dict((l, totals_after.count(l)) for l in set(totals_after))
    bins = np.arange(1, 10, 1)

    ax = fig.add_subplot(3, 3, 9)
    ax.hist(totals_after, bins = bins, color = 'red', histtype = 'step', lw = 2.5, zorder = 3)
    ax.set_ylabel(r'$\rm N_{programs}$', fontsize = label_size)
    plt.xlim(0.5,9.5)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.yaxis.tick_right()
    ax.set_xticks([1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5])
    ax.set_xticklabels([r'$1$', r'$2$', r'$3$', r'$4$', r'$5$', r'$6$', r'$7$', r'$8$'])
    loc, lab = plt.yticks()
    labels = []
    for l in loc:
        labels.append(r'$%d$'%(int(l)))
    ax.set_yticklabels(labels)

    fig.tight_layout()
    if save:
        plt.savefig('results/plots/summary_hists.png', dpi = 250)
    if show:
        plt.show()
    plt.close()


    # RA distribution
    df = pd.read_csv('results/plots_before/TOIs_perfect_final.csv')
    df2 = df.query("photo_vetting == 'passed' and spec_vetting != 'failed' and spec_vetting != 'do not observe'")
    df3 = pd.read_csv('results/plots_before/observing_priorities.csv')
    filter = df['tic'].isin(df3.tic.values.tolist())
    df3 = df[filter]
    ra_all = np.array(df.ra.values.tolist())*(24./360.)
    ra_some = np.array(df2.ra.values.tolist())*(24./360.)
    ra_before = np.array(df3.ra.values.tolist())*(24./360.)
    bins = np.arange(0, 24, 1.)

    fig = plt.figure(figsize = (14,6))
    ax = fig.add_subplot(1, 2, 1)

    ax.hist(ra_all, bins = bins, facecolor = '0.75', label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(ra_all)))))
    ax.hist(ra_some, bins = bins, facecolor = 'k', label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(ra_some)))))
    ax.hist(ra_before, bins = bins, color = 'blue', histtype = 'step', lw = 2.5, label = r'$\rm Before \; [%s]$'%(str(int(len(ra_before)))))
    ax.set_xlabel(r'$\rm RA \; [^{o}]$', fontsize = label_size)
    ax.legend(fontsize = legend_size, loc = 'upper left', markerscale = marker_scale)
    plt.xlim(-0.5,24.5)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([2., 6., 10., 14., 18., 22.])
    ax.set_xticklabels([r'$2$', r'$6$', r'$10$', r'$14$', r'$18$', r'$22$'])


    df4 = pd.read_csv(path+'TOIs_perfect_final.csv')
    df5 = df4.query("photo_vetting == 'passed' and spec_vetting != 'failed' and spec_vetting != 'do not observe'")
    df6 = pd.read_csv(path+'observing_priorities.csv')
    filter = df4['tic'].isin(df6.tic.values.tolist())
    df6 = df4[filter]
    ra_all = np.array(df4.ra.values.tolist())*(24./360.)
    rem_time_all = np.array(df4.rem_time.values.tolist())
    ra_some = np.array(df5.ra.values.tolist())*(24./360.)
    rem_time_some = np.array(df5.rem_time.values.tolist())
    ra_after = np.array(df6.ra.values.tolist())*(24./360.)
    rem_time = np.array(df6.rem_time.values.tolist())
    ax = fig.add_subplot(1, 2, 2)

    ax.hist(ra_all, bins = bins, facecolor = '0.75', label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(ra_all)))))
    ax.hist(ra_some, bins = bins, facecolor = 'k', label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(ra_some)))))
    ax.hist(ra_after, bins = bins, color = 'red', histtype = 'step', lw = 2.5, label = r'$\rm After \; [%s]$'%(str(int(len(ra_after)))))
    ax.set_xlabel(r'$\rm RA \; [^{o}]$', fontsize = label_size)
    ax.legend(fontsize = legend_size, loc = 'upper left', markerscale = marker_scale)
    plt.xlim(-0.5,24.5)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([2., 6., 10., 14., 18., 22.])
    ax.set_xticklabels([r'$2$', r'$6$', r'$10$', r'$14$', r'$18$', r'$22$'])

    fig.tight_layout()
    if save:
        plt.savefig('results/plots/ra_dist.png', dpi = 250)
    if show:
        plt.show()
    plt.close()

    bins = np.arange(0, 24, 1.)

    plt.figure(figsize = (14,10))
    ax = plt.subplot(1, 1, 1)

    ax.hist(ra_before, bins = bins, density = True, cumulative = True, color = 'blue', histtype = 'step', lw = 2.5, label = r'$\rm Before$')
    ax.hist(ra_after, bins = bins, density = True, cumulative = True, color = 'red', histtype = 'step', lw = 2.5, label = r'$\rm After$')
    ax.set_xlabel(r'$\rm RA \; [^{o}]$', fontsize = 28.)
    ax.legend(fontsize = legend_size, loc = 'upper left', markerscale = marker_scale)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = 22.)
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([2., 6., 10., 14., 18., 22.])
    ax.set_xticklabels([r'$2$', r'$6$', r'$10$', r'$14$', r'$18$', r'$22$'])
    ax.set_xlim([-0.5,24.5])

    plt.tight_layout()
    if save:
        plt.savefig('results/plots/ra_dist_compare_4.png', dpi = 250)
    if show:
        plt.show()
    plt.close()

    x = np.arange(0.5, 24, 1)
    width = 1.

    digitized = np.digitize(ra_after, bins)
    tot_times = [rem_time[digitized == i].sum() for i in range(1, len(bins))]
    tot_times.append(0.)
    avg_times = [rem_time[digitized == i].mean() for i in range(1, len(bins))]
    avg_times.append(0.)

    plt.figure(figsize = (10,8))
    ax = plt.subplot(1, 1, 1)

    ax.bar(x, tot_times, width = width, facecolor = 'dodgerblue', edgecolor = 'k', label = r'$\rm Total$')
    ax.bar(x, avg_times, width = width, facecolor = 'darkorange', edgecolor = 'k', label = r'$\rm Average$')
    ax.set_xlabel(r'$\rm RA \; [^{o}]$', fontsize = 28.)
    ax.set_ylabel(r'$\rm Time \,\, [hours]$', fontsize = 28.)
    ax.set_title(r'$\rm Remaining \,\, time \,\, for \,\, TKS$', fontsize = 30.)
    ax.legend(fontsize = legend_size, loc = 'upper left', markerscale = marker_scale)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 1, direction = 'inout')
    ax.tick_params(labelsize = 22.)
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(15))
    loc, lab = plt.yticks()
    ylabels = []
    for l in loc:
        ylabels.append(r'$%d$'%int(l))
    ax.set_yticklabels(ylabels)
    ax.set_xticks([1., 5., 9., 13., 17., 21.])
    ax.set_xticklabels([r'$1$', r'$5$', r'$9$', r'$13$', r'$17$', r'$21$'])
    ax.set_xlim([0.,24.])
    ax.set_ylim([0.,83.])

    plt.tight_layout()
    if save:
        plt.savefig('results/plots/ra_remaining_times.png', dpi = 250)
    if show:
        plt.show()
    plt.close()

    """
    n_systems = list(set(program.tic.values.tolist()))
    y_upper = len(n_systems)-0.5

    rp = program.rp.values.tolist()
    per = program.period.values.tolist()

    labels = []

    plt.figure(figsize = (12,12))
    ax = plt.subplot(1,1,1)

    for i in range(len(n_systems)):
        query = program.query('tic == %d'%n_systems[i])
        for j in query.index.values.tolist():
            ax.scatter(query.loc[j]['period'], i, color = 'dodgerblue', s = 30.*(query.loc[j]['rp'])**(1.75), lw = 0.5, edgecolor = 'k')
        toi = int(np.floor(query.loc[j]['toi']))
        labels.append(str(toi))
    ax.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)
    ax.set_xscale('log')
    ax.tick_params(labelsize = tick_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.set_yticks(np.arange(len(n_systems)))
    labels = [r'$\rm TOI \, %s$'%label for label in labels]
    ax.set_yticklabels(labels)
    ax.set_xticks([0.3, 1., 3., 10., 30.])
    ax.set_xticklabels([r'$0.3$', r'$1$', r'$3$', r'$10$', r'$30$'])
    ax.set_xlim(0.2, 70)
    ax.set_ylim(-0.5, y_upper)

    ax2 = ax.twiny()
    ax2.set_xscale('log')
    ax2.tick_params(labelsize = tick_size)
    ax2.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax2.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax2.set_xticks([0.3, 1., 3., 10., 30.])
    ax2.set_xticklabels([r'$0.3$', r'$1$', r'$3$', r'$10$', r'$30$'])
    ax2.set_xlim(0.2, 70)
    ax2.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)

    plt.tight_layout()
    if (save and all) or (save and science_case in case):
        plt.savefig('results/plots/%s.png'%science_case)
    if (show and all) or (show and science_case in case):
        plt.show()
    plt.close()
    """

    return


def make_single_plots(path, show, save, all, case, label_size, tick_size, legend_size, marker_size, marker_scale):

    df = pd.read_csv(path+'TOIs_perfect_final.csv')
    df2 = df.query("photo_vetting == 'passed' and spec_vetting != 'failed' and spec_vetting != 'do not observe'")

    # SC1A
    science_case = 'SC1A'
    program = df.query("in_%s == 1"%science_case)
    no = len(program.tic.values.tolist())

    rp_all = df.rp.values.tolist()
    rp_some = df2.rp.values.tolist()
    rp = program.rp.values.tolist()

    bins = np.logspace(np.log10(min(rp_all)), np.log10(max(rp_all)), 50)

    plt.figure(figsize = (14,8))
    ax = plt.subplot(1, 1, 1)

    ax.hist(rp_all, bins = bins, facecolor = '0.75', label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(rp_all)))))
    ax.hist(rp_some, bins = bins, facecolor = 'k', label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(rp_some)))))
    ax.hist(rp, bins = bins, color = 'blue', histtype = 'step', lw = 2.5, label = r'$\rm SC1A \; [%d]$'%no)
    ax.set_xlabel(r'$\rm R_{p} \; [R_{\oplus}]$', fontsize = label_size)
    ax.legend(fontsize = legend_size, loc = 'center left', bbox_to_anchor = (1, 0.5), markerscale = marker_scale)
    plt.xlim(1.,22.5)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([1., 1.3, 1.7, 2.2, 3., 10., 13., 20.])
    ax.set_xticklabels([r'$1$', r'$1.3$', r'$1.7$', r'$2.2$', r'$3$', r'$10$', r'$13$', r'$20$'])
    plt.tight_layout()
    if (save and all) or (save and science_case in case):
        plt.savefig('results/plots/%s.png'%science_case)
    if (show and all) or (show and science_case in case):
        plt.show()
    plt.close()


    # SC1B
    science_case = 'SC1B'
    program = df.query("in_%s == 1"%science_case)
    no = len(program.tic.values.tolist())

    rp_all = df.rp.values.tolist()
    per_all = df.period.values.tolist()
    rp_some = df2.rp.values.tolist()
    per_some = df2.period.values.tolist()
    rp = program.rp.values.tolist()
    per = program.period.values.tolist()

    lines = np.logspace(0,2,5)

    plt.figure(figsize = (14,8))

    ax = plt.subplot(1,1,1)
    ax.scatter(per_all, rp_all, linestyle = 'None', marker = 'o', color = '0.75', s = marker_size, zorder = 1, label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(rp_all)))))
    ax.scatter(per_some, rp_some, linestyle = 'None', marker = 'o', color = 'k', s = marker_size, zorder = 1, label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(rp_some)))))
    ax.scatter(per, rp, linestyle = 'None', marker = 'o', color = 'orange', edgecolor = 'k',  s = marker_size, zorder = 2, label = r'$\rm SC1B \; [%d]$'%no)
    ax.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)
    ax.set_ylabel(r'$\rm R_{p}$', fontsize = label_size)
    for line in lines:
        ax.axvline(line, color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.axhline(3., color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.axhline(2., color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.set_xlim(1, 100)
    ax.set_ylim(1, 4)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')
    ax.tick_params(labelsize = tick_size)
    ax.legend(fontsize = legend_size, loc = 'center left', bbox_to_anchor = (1, 0.5), markerscale = marker_scale)
    ax.set_xscale("log") 
    ax.set_yticks([1., 2., 3., 4.])
    ax.set_yticklabels([r'$1$', r'$2$', r'$3$', r'$4$'])
    ax.set_xticks(lines)
    ax.set_xticklabels([r'$1.00$', r'$3.16$', r'$10.0$', r'$31.6$', r'$100$'])
    plt.tight_layout()
    if (save and all) or (save and science_case in case):
        plt.savefig('results/plots/%s.png'%science_case)
    if (show and all) or (show and science_case in case):
        plt.show()
    plt.close()


    # SC1C
    science_case = 'SC1C'
    program = df.query("in_%s == 1"%science_case)
    no = len(program.tic.values.tolist())

    rp_all = df.rp.values.tolist()
    sinc_all = df.sinc.values.tolist()
    rp_some = df2.rp.values.tolist()
    sinc_some = df2.sinc.values.tolist()
    rp = program.rp.values.tolist()
    sinc = program.sinc.values.tolist()

    plt.figure(figsize = (14,8))

    ax = plt.subplot(1,1,1)
    p1 = (1e6, 2.1)
    p2 = (800, 3.8)
    plt.plot((p1[0], p2[0], p2[0], p1[0]), (p1[1], p1[1], p2[1], p2[1]), 'k--', zorder = 0, label = r'$\rm Super$-$\rm Earth \; Desert$')
    ax.scatter(sinc_all, rp_all, c = '0.75', s = marker_size, zorder = 0, label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(rp_all)))))
    ax.scatter(sinc_some, rp_some, c = 'k', s = marker_size, zorder = 0, label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(rp_some)))))
    ax.scatter(sinc, rp, c = '#ff8c00', s = marker_size, lw = 0.5, edgecolor = 'b', zorder = 2, label = r'$\rm SC1C \; [%d]$'%no)
    ax.set_ylabel(r"$\rm R_{p}\,\, [R_{\oplus}]$", fontsize = label_size)
    ax.set_xlabel(r"$\rm Incident\,\, Flux\,\, [F_{\oplus}]$", fontsize = label_size)
    ax.tick_params(labelsize = tick_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')
    plt.xscale("log")
    ax.legend(fontsize = legend_size, loc = 'center left', bbox_to_anchor = (1, 0.5), markerscale = marker_scale)
    ax.set_xticks([10000, 1000])
    ax.set_xticklabels([r'$10^{4}$', r'$10^{3}$'])
    ax.set_yticks([1, 2, 3, 4, 5, 6])
    ax.set_yticklabels([r'$1$', r'$2$', r'$3$', r'$4$', r'$5$', r'$6$'])
    ax.set_xlim(15000, 500)
    ax.set_ylim(1, 6.5)
    plt.tight_layout()
    if (save and all) or (save and science_case in case):
        plt.savefig('results/plots/%s.png'%science_case)
    if (show and all) or (show and science_case in case):
        plt.show()
    plt.close()


    # SC1D
    science_case = 'SC1D'
#    program = df.query("in_%s == 1"%science_case)
    program = df.query("in_other_programs != 0")
    no = len(program.tic.values.tolist())

    rp_all = df.rp.values.tolist()
    sinc_all = df.sinc.values.tolist()
    rp_some = df2.rp.values.tolist()
    sinc_some = df2.sinc.values.tolist()
    rp = program.rp.values.tolist()
    sinc = program.sinc.values.tolist()

    plt.figure(figsize = (12,8))

    ax = plt.subplot(1,1,1)
    ax.scatter(sinc_all, rp_all, c = '0.75', s = marker_size, zorder = 0, label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(rp_all)))))
    ax.scatter(sinc_some, rp_some, c = 'k', s = marker_size, zorder = 0, label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(rp_some)))))
    ax.scatter(sinc, rp, c = 'none', s = marker_size, lw = 2.5, edgecolor = 'r', zorder = 2, label = r'$\rm TKS \; [%d]$'%no)
    ax.set_ylabel(r"$\rm R_{p}\,\, [R_{\oplus}]$", fontsize = label_size)
    ax.set_xlabel(r"$\rm Incident\,\, Flux\,\, [F_{\oplus}]$", fontsize = label_size)
    ax.tick_params(labelsize = tick_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 10, width = 1.25, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 15, width = 1.25, direction = 'inout')
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')
    plt.yscale("log")
    plt.xscale("log")
    ax.axvspan(0.1, 10., facecolor = 'g', alpha = 0.25, zorder = 0, label = r'$\rm Optimistic \,\, HZ$')
    ax.axvspan(0.1, 1.1, facecolor = 'g', alpha = 0.75, zorder = 0, label = r'$\rm Conservative \,\, HZ$')
    ax.set_xticks([0.1, 1, 10, 100, 1000, 10000, 100000])
    ax.set_xticklabels([r'$10^{-1}$', r'$10^{0}$', r'$10^{1}$', r'$10^{2}$', r'$10^{3}$', r'$10^{4}$', r'$10^{5}$'])
    ax.set_yticks([1, 10])
    ax.set_yticklabels([r'$1$', r'$10$'])
    leg = ax.legend(fontsize=legend_size, framealpha=1.0, columnspacing=0.1, labelspacing=0.3, markerscale=marker_scale, handletextpad=0.25, handlelength=0.75)
    leg.get_frame().set_edgecolor('k')
    plt.tick_params(labelsize = tick_size)
    plt.xlim([15000., 0.1])
    plt.ylim([0.9, 22.])
    plt.tight_layout()
    plt.savefig('/Users/ashleychontos/Desktop/planets.png', dpi = 250)
    plt.savefig('/Users/ashleychontos/Desktop/planets.pdf')
    plt.show()
    plt.close()

    # SC1E
    science_case = 'SC1E'
    program = df.query("in_%s == 1"%science_case)
    program2 = df.query("in_other_programs != 0")
    no = len(list(set(program2.tic.values.tolist())))

    ms_all = df.m_s.values.tolist()
    feh_all = df.feh.values.tolist()
    ms_some = df2.m_s.values.tolist()
    feh_some = df2.feh.values.tolist()
    ms = program.m_s.values.tolist()
    feh = program.feh.values.tolist()
    ms2 = program2.m_s.values.tolist()
    feh2 = program2.feh.values.tolist()

    lines = np.logspace(0,2,5)

    plt.figure(figsize = (14,8))

    ax = plt.subplot(1,1,1)
    ax.scatter(feh_all, ms_all, linestyle = 'None', marker = 'o', color = '0.75', s = marker_size, zorder = 1, label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(ms_all)))))
    ax.scatter(feh_some, ms_some, c = 'k', s = marker_size, zorder = 0, label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(ms_some)))))
    ax.scatter(feh, ms, linestyle = 'None', marker = 'o', color = 'orange', edgecolor = 'k',  s = marker_size, zorder = 3, label = r'$\rm SC1E \; [%d]$'%no)
    ax.scatter(feh2, ms2, linestyle = 'None', marker = 'o', color = 'orange', edgecolor = 'k', s = marker_size, zorder = 2)
    ax.set_xlabel(r'$\rm [Fe/H]$', fontsize = label_size)
    ax.set_ylabel(r'$\rm Mass \; [M_{\odot}]$', fontsize = label_size)
    ax.axhline(0.8, color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.axhline(1.2, color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.axvline(-0.25, color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.axvline(0.25, color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.axvline(0., color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0.4, 1.6)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')
    ax.tick_params(labelsize = tick_size)
    ax.legend(fontsize = legend_size, loc = 'center left', bbox_to_anchor = (1, 0.5), markerscale = marker_scale)
#    ax.set_xscale("log") 
    ax.set_yticks([0.5, 1., 1.5])
    ax.set_yticklabels([r'$0.5$', r'$1.0$', r'$1.5$'])
    ax.set_xticks([-0.5, -0.25, 0., 0.25, 0.5])
    ax.set_xticklabels([r'$-0.50$', r'$-0.25$', r'$0$', r'$0.25$', r'$0.50$'])
    plt.tight_layout()
    if (save and all) or (save and science_case in case):
        plt.savefig('results/plots/%s.png'%science_case)
    if (show and all) or (show and science_case in case):
        plt.show()
    plt.close()


    # SC2A
    science_case = 'SC2A'
    program = df.query("in_%s == 1"%science_case)

    xmax = np.ceil(max(program.period.values.tolist()))+1.

    systems = list(set(program.tic.values.tolist()))
    n = len(systems)
    if n%2 != 0:
        n+=1
    count = n//2
    y_upper = float(count)-0.5

    first = systems[:count]
    second = systems[count:]

    rp = program.rp.values.tolist()
    per = program.period.values.tolist()

    labels = []

    plt.figure(figsize = (16,16))
    ax = plt.subplot(1,2,1)

    for i in range(len(first)):
        query = program.query('tic == %d'%first[i])
        for j in query.index.values.tolist():
            ax.scatter(query.loc[j]['period'], i, color = 'dodgerblue', s = 30.*(query.loc[j]['rp'])**(1.75), lw = 0.5, edgecolor = 'k')
        toi = int(np.floor(query.loc[j]['toi']))
        labels.append(str(toi))
    ax.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)
    ax.set_xscale('log')
    ax.tick_params(labelsize = tick_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.set_yticks(np.arange(len(first)))
    labels = [r'$\rm TOI \, %s$'%label for label in labels]
    ax.set_yticklabels(labels)
    ax.set_xlim(0.4, 50.)
    ax.set_xticks([1., 3., 10., 30.])
    ax.set_xticklabels([r'$1$', r'$3$', r'$10$', r'$30$'])
    ax.set_ylim(-0.5, y_upper)

    ax2 = ax.twiny()
    ax2.tick_params(labelsize = tick_size)
    ax2.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax2.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax2.set_xscale('log')
    ax2.set_xlim(0.4, 50.)
    ax2.set_xticks([1., 3., 10., 30.])
    ax2.set_xticklabels([r'$1$', r'$3$', r'$10$', r'$30$'])
    ax2.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)

    labels = []

    ax3 = plt.subplot(1,2,2)

    for i in range(len(second)):
        query = program.query('tic == %d'%second[i])
        for j in query.index.values.tolist():
            ax3.scatter(query.loc[j]['period'], i, color = 'dodgerblue', s = 30.*(query.loc[j]['rp'])**(1.75), lw = 0.5, edgecolor = 'k')
        toi = int(np.floor(query.loc[j]['toi']))
        labels.append(str(toi))
    ax3.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)
    ax3.set_xscale('log')
    ax3.set_xlim(0.4, 50.)
    ax3.set_xticks([1., 3., 10., 30.])
    ax3.set_xticklabels([r'$1$', r'$3$', r'$10$', r'$30$'])
    ax3.tick_params(labelsize = tick_size)
    ax3.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax3.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax3.set_yticks(np.arange(len(second)))
    labels = [r'$\rm TOI \, %s$'%label for label in labels]
    ax3.set_yticklabels(labels)
    ax3.set_ylim(-0.5, y_upper)

    ax4 = ax3.twiny()
    ax4.tick_params(labelsize = tick_size)
    ax4.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax4.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax4.set_xscale('log')
    ax4.set_xlim(0.4, 50.)
    ax4.set_xticks([1., 3., 10., 30.])
    ax4.set_xticklabels([r'$1$', r'$3$', r'$10$', r'$30$'])
    ax4.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)
    
    plt.tight_layout()
    if (save and all) or (save and science_case in case):
        plt.savefig('results/plots/%s.png'%science_case)
    if (show and all) or (show and science_case in case):
        plt.show()
    plt.close()


    # SC2C
    science_case = 'SC2C'
    program = df.query("in_%s == 1"%science_case)

    n_systems = list(set(program.tic.values.tolist()))
    y_upper = len(n_systems)-0.5

    rp = program.rp.values.tolist()
    per = program.period.values.tolist()

    labels = []

    plt.figure(figsize = (12,12))
    ax = plt.subplot(1,1,1)

    for i in range(len(n_systems)):
        query = program.query('tic == %d'%n_systems[i])
        for j in query.index.values.tolist():
            ax.scatter(query.loc[j]['period'], i, color = 'dodgerblue', s = 30.*(query.loc[j]['rp'])**(1.75), lw = 0.5, edgecolor = 'k')
        toi = int(np.floor(query.loc[j]['toi']))
        labels.append(str(toi))
    ax.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)
    ax.set_xscale('log')
    ax.tick_params(labelsize = tick_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.set_yticks(np.arange(len(n_systems)))
    labels = [r'$\rm TOI \, %s$'%label for label in labels]
    ax.set_yticklabels(labels)
    ax.set_xticks([0.3, 1., 3., 10., 30.])
    ax.set_xticklabels([r'$0.3$', r'$1$', r'$3$', r'$10$', r'$30$'])
    ax.set_xlim(0.2, 70)
    ax.set_ylim(-0.5, y_upper)

    ax2 = ax.twiny()
    ax2.set_xscale('log')
    ax2.tick_params(labelsize = tick_size)
    ax2.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax2.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax2.set_xticks([0.3, 1., 3., 10., 30.])
    ax2.set_xticklabels([r'$0.3$', r'$1$', r'$3$', r'$10$', r'$30$'])
    ax2.set_xlim(0.2, 70)
    ax2.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)

    plt.tight_layout()
    if (save and all) or (save and science_case in case):
        plt.savefig('results/plots/%s.png'%science_case)
    if (show and all) or (show and science_case in case):
        plt.show()
    plt.close()

    # SC4
    science_case = 'SC4'
    program = df.query("in_%s == 1"%science_case)
    no = len(program.tic.values.tolist())

    rp_all = df.rp.values.tolist()
    sinc_all = df.sinc.values.tolist()
    rp_some = df2.rp.values.tolist()
    sinc_some = df2.sinc.values.tolist()
    rp = program.rp.values.tolist()
    sinc = program.sinc.values.tolist()

    plt.figure(figsize = (14,8))

    ax = plt.subplot(1,1,1)
    p1 = (1e6, 2.1)
    p2 = (800, 3.8)
    plt.plot((p1[0], p2[0], p2[0], p1[0]), (p1[1], p1[1], p2[1], p2[1]), 'k--', zorder = 0, label = r'$\rm Super$-$\rm Earth \; Desert$')
    ax.scatter(sinc_all, rp_all, c = '0.75', s = marker_size, zorder = 0, label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(rp_all)))))
    ax.scatter(sinc_some, rp_some, c = 'k', s = marker_size, zorder = 0, label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(rp_some)))))
    ax.scatter(sinc, rp, c = '#ff8c00', s = marker_size, lw = 0.5, edgecolor = 'b', zorder = 2, label = r'$\rm SC4 \; [%d]$'%no)
    ax.set_ylabel(r"$\rm R_{p}\,\, [R_{\oplus}]$", fontsize = label_size)
    ax.set_xlabel(r"$\rm Incident\,\, Flux\,\, [F_{\oplus}]$", fontsize = label_size)
    ax.tick_params(labelsize = tick_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')
    plt.yscale("log")
    plt.xscale("log")
    ax.axvspan(0.25, 10., facecolor = 'g', alpha = 0.25, zorder = 0, label = r'$\rm Optimistic \; HZ$')
    ax.axvspan(0.25, 1.1, facecolor = 'g', alpha = 0.75, zorder = 0, label = r'$\rm Conservative \; HZ$')
    ax.set_xticks([0.1, 1, 10, 100, 1000, 10000, 100000])
    ax.set_xticklabels([r'$10^{-1}$', r'$10^{0}$', r'$10^{1}$', r'$10^{2}$', r'$10^{3}$', r'$10^{4}$', r'$10^{5}$'])
    ax.set_yticks([1, 10])
    ax.set_yticklabels([r'$1$', r'$10$'])
    ax.legend(fontsize = legend_size, loc = 'center left', bbox_to_anchor = (1, 0.5), markerscale = marker_scale)
    plt.tick_params(labelsize = tick_size)
    plt.xlim([15000., 0.25])
    plt.ylim([0.9, 22.])
    plt.tight_layout()
    if (save and all) or (save and science_case in case):
        plt.savefig('results/plots/%s.png'%science_case)
    if (show and all) or (show and science_case in case):
        plt.show()
    plt.close()


    # TOA
    science_case = 'TOA'
    program = df.query("in_other_programs != 0")
    no = len(list(set(program.tic.values.tolist())))

    rs = program.r_s.values.tolist()
    rs_some = df2.r_s.values.tolist()
    rs_all = df.r_s.values.tolist()
    teff = program.t_eff.values.tolist()
    teff_some = df2.t_eff.values.tolist()
    teff_all = df.t_eff.values.tolist()

    plt.figure(figsize = (14,10))
    ax = plt.subplot(1, 1, 1)

    ax.scatter(teff_all, rs_all, c = '0.75', s = marker_size, lw = 0.5, edgecolor = '0.6', zorder = 1, label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(rs_all)))))
    ax.scatter(teff_some, rs_some, c = 'k', s = marker_size, lw = 0.5, edgecolor = '0.6', zorder = 1, label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(rs_some)))))
    ax.scatter(teff, rs, c = 'none', s = marker_size, lw = 2.5, edgecolor = 'r', zorder = 2, label = r'$\rm TKS \; [%d]$'%no)
    ax.set_ylabel(r'$\rm R_{\star} \,\, [R_{\odot}]$', fontsize = label_size)
    ax.set_xlabel(r'$\rm Teff \,\, [K]$', fontsize = label_size)
    plt.yscale("log")
    ax.xaxis.set_major_locator(MultipleLocator(1000))
    ax.xaxis.set_minor_locator(MultipleLocator(250))
    ax.tick_params(axis = 'both', which = 'both', direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 10, width = 1.25, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 15, width = 1.25, direction = 'inout')
    leg = ax.legend(fontsize=legend_size, framealpha=1.0, handletextpad=0.25, loc='upper right', markerscale=marker_scale, handlelength=0.75, labelspacing=0.3, columnspacing=0.1)
    leg.get_frame().set_edgecolor('k')
    ax.set_xticks([7000., 6000., 5000., 4000., 3000.])
    ax.set_xticklabels([r'$7000$', r'$6000$', r'$5000$', r'$4000$', r'$3000$'])
    ax.set_yticks([1., 10.])
    ax.set_yticklabels([r'$10^{0}$', r'$10^{1}$'])
    ax.set_xlim([7100., 2900.])
    ax.set_ylim([0.2, 9.])
    plt.tight_layout()
    plt.savefig('/Users/ashleychontos/Desktop/hosts.png', dpi = 250)
    plt.savefig('/Users/ashleychontos/Desktop/hosts.pdf')
    plt.show()
    plt.close()

    return


##########################################################################################
#                                                                                        #
#                                         INIT                                           #
#                                                                                        #
##########################################################################################


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'This is a script to create plots based on a definitive observing list.')
    parser.add_argument(option_strings=[], dest='case', help='Science case(s)', type=str, default = None, nargs = '*')
    parser.add_argument('-show', '--show', help = 'Show plots', dest = 'show', action = 'store_true')
    parser.add_argument('-save', '--save', help = 'Save plots', dest = 'save', action = 'store_false')
    parser.add_argument('-a', '--a', '-all', '--all', help = 'Show all individual plots', dest = 'all', action = 'store_true')

    args = parser.parse_args()
    show = args.show
    save = args.save
    all = args.all
    if args.case is not None:
        case = []
        for c in args.case:
            if c.startswith('o') or c.startswith('O'):
                case.append('T'+c.upper())
            else:
                case.append('SC'+c.upper())
    else:
        case = args.case

    main(show = show, save = save, all = all, case = case)