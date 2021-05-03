import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import MultipleLocator

import warnings
warnings.filterwarnings('ignore')


plt.rcParams['mathtext.fontset'] = 'stix'


def make_all_plots(all, show, case, label_size = 28., tick_size = 24., legend_size = 18., 
                   marker_scale = 1.25,  marker_size = 100.):

    summary_plots(show, marker_scale = 1.25, marker_size = 100., label_size = 22., tick_size = 18., legend_size = 24.)
    make_stacked(show, label_size, tick_size, legend_size, marker_scale)

    make_single_plots(all, show, case, label_size, tick_size, legend_size, marker_size, marker_scale)

    return


def make_stacked(show, label_size, tick_size, legend_size, marker_scale, parameter = 'rp'):

    df = pd.read_csv('results/TOIs_perfect_final.csv')
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
    plt.ylim(0.,50.)
    plt.xlim(1.,20.)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(2))
    ax.set_xticks(bins)
    ax.set_xticklabels(xlabels)
    ax.set_yticks([10., 20., 30., 40., 50.])
    ax.set_yticklabels([r'$10$', r'$20$', r'$30$', r'$40$', r'$50$'])
    ax.xaxis.grid(True, which = 'major', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.yaxis.grid(True, which = 'major', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.yaxis.grid(True, which = 'minor', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.tick_params(axis = 'x', which = 'minor', bottom = False)
    ax.tick_params(axis = 'x', which = 'major', top = True, zorder = 7)
    ax.tick_params(axis = 'x', which = 'major', length = 8, width = 2, direction = 'inout', zorder = 7)
    ax.tick_params(axis = 'y', which = 'both', right = True)
    ax.tick_params(labelsize = tick_size)
    plt.tight_layout()
    plt.savefig('results/plots/step_hist_summary.png', dpi = 250)
    if show:
        plt.show()
    plt.close()


    plt.figure(figsize = (14,8))
    ax = plt.subplot(1, 1, 1)

    ax.hist(values, bins = bins, histtype = 'stepfilled', stacked = True, lw = 2.5, label = labels, zorder = 3)
    ax.set_xlabel(r'$\rm R_{p} \; [R_{\oplus}]$', fontsize = label_size)
    ax.legend(fontsize = legend_size, facecolor = 'w', framealpha = 1.0, markerscale = marker_scale, loc = 'center left', bbox_to_anchor = (1, 0.5))
    plt.ylim(0.,50.)
    plt.xlim(1.,20.)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(2))
    ax.set_xticks(bins)
    ax.set_xticklabels(xlabels)
    ax.set_yticks([10., 20., 30., 40., 50.])
    ax.set_yticklabels([r'$10$', r'$20$', r'$30$', r'$40$', r'$50$'])
    ax.xaxis.grid(True, which = 'major', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.yaxis.grid(True, which = 'major', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.yaxis.grid(True, which = 'minor', color = '0.75', linestyle = '--', linewidth = 0.25, zorder = 0)
    ax.tick_params(axis = 'x', which = 'minor', bottom = False)
    ax.tick_params(axis = 'x', which = 'major', top = True, zorder = 7)
    ax.tick_params(axis = 'x', which = 'major', length = 8, width = 2, direction = 'inout', zorder = 7)
    ax.tick_params(axis = 'y', which = 'both', right = True)
    ax.tick_params(labelsize = tick_size)
    plt.tight_layout()
    plt.savefig('results/plots/bar_hist_summary.png', dpi = 250)
    if show:
        plt.show()
    plt.close()


    plt.figure(figsize = (14,8))
    ax = plt.subplot(1, 1, 1)

    for i, v in enumerate(values):
        bin = np.logspace(np.log10(min(v)), np.log10(max(v)), 20)
        ax.hist(v, bins = bin, histtype = "stepfilled", alpha = 0.8, density = True, label = labels[i])
    ax.set_xlabel(r'$\rm R_{p} \; [R_{\oplus}]$', fontsize = label_size)
    ax.legend(fontsize = legend_size, facecolor = 'w', framealpha = 1.0, markerscale = marker_scale, loc = 'center left', bbox_to_anchor = (1, 0.5))
    plt.xlim(1.,20.)
    ax.set_xscale("log")
    ax.set_xticks(bins)
    ax.set_xticklabels(xlabels)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    plt.tight_layout()
    plt.savefig('results/plots/dens_hist_summary.png', dpi = 250)
    if show:
        plt.show()
    plt.close()

    return


def summary_plots(show, marker_scale, marker_size, label_size = 22., tick_size = 18., legend_size = 24.):

    df = pd.read_csv('results/TOIs_perfect_final.csv')
    df2 = df.query("photo_vetting == 'passed' and spec_vetting != 'failed' and spec_vetting != 'do not observe'")
    df3 = pd.read_csv('results/observing_priorities.csv')
    filter = df['tic'].isin(df3.tic.values.tolist())
    df3 = df[filter]

    plt.figure(figsize = (18,10))

    # vmag
    vmag_all = df.vmag.values.tolist()
    vmag_some = df2.vmag.values.tolist()
    vmag = df3.vmag.values.tolist()
    bins = np.arange(5.5, 13.5, 0.25)

    ax = plt.subplot(3, 3, 1)
    ax.hist(vmag_all, bins = bins, facecolor = '0.75')
    ax.hist(vmag_some, bins = bins, facecolor = 'k')
    ax.hist(vmag, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$\rm V_{mag}$', fontsize = label_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
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
    teff = df3.t_eff.values.tolist()
    bins = np.arange(3000., 8100., 250.)

    ax = plt.subplot(3, 3, 2)
    ax.hist(teff_all, bins = bins, facecolor = '0.75')
    ax.hist(teff_some, bins = bins, facecolor = 'k')
    ax.hist(teff, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$\rm Teff \; [K]$', fontsize = label_size)
    plt.xlim(2750.,8250.)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
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
    vsini = np.array(df3.vsini.values.tolist())
    mask = np.ma.getmask(np.ma.masked_invalid(vsini))
    vsini = list(vsini[~mask])
    bins = np.logspace(-1., np.log10(20.), 20)

    ax = plt.subplot(3, 3, 3)
    ax.hist(vsini_all, bins = bins, facecolor = '0.75')
    ax.hist(vsini_some, bins = bins, facecolor = 'k')
    ax.hist(vsini, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$v\,\sin\,i \; [\rm{km s}^{-1}]$', fontsize = label_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([0.1, 0.3, 1.0, 3., 10.])
    ax.set_xticklabels([r'$0.1$', r'$0.3$', r'$1$', r'$3$', r'$10$'])


    # Rs
    rs_all = df.r_s.values.tolist()
    rs_some = df2.r_s.values.tolist()
    rs = df3.r_s.values.tolist()
    bins = np.logspace(-1., 1., 30)

    ax = plt.subplot(3, 3, 4)
    ax.hist(rs_all, bins = bins, facecolor = '0.75')
    ax.hist(rs_some, bins = bins, facecolor = 'k')
    ax.hist(rs, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$\rm R_{\star} \; [R_{\odot}]$', fontsize = label_size)
    plt.xlim(0.3,11.)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([0.5, 1.0, 3., 10.])
    ax.set_xticklabels([r'$0.5$', r'$1$', r'$3$', r'$10$'])


    # Rp
    rp_all = df.rp.values.tolist()
    rp_some = df2.rp.values.tolist()
    rp = df3.rp.values.tolist()
    bins = np.logspace(-0.5, 2., 30)

    ax = plt.subplot(3, 3, 5)
    ax.hist(rp_all, bins = bins, facecolor = '0.75')
    ax.hist(rp_some, bins = bins, facecolor = 'k')
    ax.hist(rp, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$\rm R_{p} \; [R_{\oplus}]$', fontsize = label_size)
    plt.xlim(0.7,30.)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([1., 3., 10., 30.])
    ax.set_xticklabels([r'$1$', r'$3$', r'$10$', r'$30$'])


    # Incident flux
    sinc_all = df.sinc.values.tolist()
    sinc_some = df2.sinc.values.tolist()
    sinc = df3.sinc.values.tolist()
    bins = np.logspace(-1, 5.5, 30.)

    ax = plt.subplot(3, 3, 6)
    ax.hist(sinc_all, bins = bins, facecolor = '0.75', label = r'$\rm Full \; [%s]$'%(str(int(len(sinc_all)))))
    ax.hist(sinc_some, bins = bins, facecolor = 'k', label = r'$\rm Vetted \; [%s]$'%(str(int(len(sinc_some)))))
    ax.hist(sinc, bins = bins, color = 'red', histtype = 'step', lw = 2.5, label = r'$\rm Selected \; [%s]$'%(str(int(len(sinc)))))
    ax.set_ylabel(r'$\rm F_{p} \; [F_{\oplus}]$', fontsize = label_size)
    plt.xlim(1e5,0.)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
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
    ksig = df3.ksig.values.tolist()
    bins = np.logspace(0, 2, 20)

    ax = plt.subplot(3, 3, 7)
    ax.hist(ksig_all, bins = bins, facecolor = '0.75')
    ax.hist(ksig_some, bins = bins, facecolor = 'k')
    ax.hist(ksig, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.axvline(3., color = 'dodgerblue', ls = '--', lw = 1.5)
    ax.axvline(5., color = 'green', ls = '-.', lw = 1.5)
    ax.set_ylabel(r'$\rm K/\sigma_{K}$', fontsize = label_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    plt.xlim(1.,120.)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([1., 3., 10., 30., 100.])
    ax.set_xticklabels([r'$1$', r'$3$', r'$10$', r'$30$', r'$100$'])


    # total time (hours)
    time_all = np.array(df.tottime.values.tolist())
    time_some = np.array(df2.tottime.values.tolist())
    time = np.array(df3.tottime.values.tolist())
    bins = np.logspace(np.log10(5.), np.log10(35.), 20)

    ax = plt.subplot(3, 3, 8)
    ax.hist(time_all, bins = bins, facecolor = '0.75')
    ax.hist(time_some, bins = bins, facecolor = 'k')
    ax.hist(time, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$\rm Total \; time \; [hours]$', fontsize = label_size)
    plt.xlim(4.8,35.5)
    ax.set_xscale("log")
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([6., 10., 15., 20., 30.])
    ax.set_xticklabels([r'$6$', r'$10$', r'$15$', r'$20$', r'$30$'])


    # n programs
    n_all = np.array(df.in_other_programs.values.tolist())
    n_some = np.array(df2.in_other_programs.values.tolist())
    n = np.array(df3.in_other_programs.values.tolist())
    bins = np.arange(0, 9, 1)

    ax = plt.subplot(3, 3, 9)
    ax.hist(n_all, bins = bins, facecolor = '0.75')
    ax.hist(n_some, bins = bins, facecolor = 'k')
    ax.hist(n, bins = bins, color = 'red', histtype = 'step', lw = 2.5)
    ax.set_ylabel(r'$\rm N_{programs}$', fontsize = label_size)
    plt.xlim(-0.5,9.)
    plt.ylim(0.,30.)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5])
    ax.set_xticklabels([r'$1$', r'$2$', r'$3$', r'$4$', r'$5$', r'$6$', r'$7$', r'$8$'])

    plt.tight_layout()
    plt.savefig('results/plots/summary_hists.png', dpi = 250)
    if show:
        plt.show()
    plt.close()
    return


def make_single_plots(all, show, case, label_size, tick_size, legend_size, marker_size, marker_scale):

    df = pd.read_csv('results/TOIs_perfect_final.csv')
    df2 = df.query("photo_vetting == 'passed' and spec_vetting != 'failed' and spec_vetting != 'do not observe'")

    # SC1A
    science_case = 'SC1A'
    program = df.query("in_%s == 1"%science_case)

    rp_all = df.rp.values.tolist()
    rp_some = df2.rp.values.tolist()
    rp = program.rp.values.tolist()

    bins = np.logspace(np.log10(min(rp_all)), np.log10(max(rp_all)), 50)

    plt.figure(figsize = (14,8))
    ax = plt.subplot(1, 1, 1)

    ax.hist(rp_all, bins = bins, facecolor = '0.75', label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(rp_all)))))
    ax.hist(rp_some, bins = bins, facecolor = 'k', label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(rp_some)))))
    ax.hist(rp, bins = bins, color = 'red', histtype = 'step', lw = 2.5, label = r'$\rm SC1A \; [%s]$'%(str(int(len(rp)))))
    ax.set_xlabel(r'$\rm R_{p} \; [R_{\oplus}]$', fontsize = label_size)
    ax.legend(fontsize = tick_size, markerscale = marker_scale)
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
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()


    # SC1B
    science_case = 'SC1B'
    program = df.query("in_%s == 1"%science_case)

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
    ax.scatter(per, rp, linestyle = 'None', marker = 'o', color = 'orange', edgecolor = 'k',  s = marker_size, zorder = 2, label = r'$\rm SC1B \; [%s]$'%(str(int(len(rp)))))
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
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()


    # SC1C
    science_case = 'SC1C'
    program = df.query("in_%s == 1"%science_case)

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
    ax.scatter(sinc, rp, c = '#ff8c00', s = marker_size, lw = 0.5, edgecolor = 'b', zorder = 2, label = r'$\rm SC1C \; [%s]$'%(str(int(len(rp)))))
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
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()


    # SC1D
    science_case = 'SC1D'
    program = df.query("in_%s == 1"%science_case)

    rp_all = df.rp.values.tolist()
    sinc_all = df.sinc.values.tolist()
    rp_some = df2.rp.values.tolist()
    sinc_some = df2.sinc.values.tolist()
    rp = program.rp.values.tolist()
    sinc = program.sinc.values.tolist()

    plt.figure(figsize = (14,8))

    ax = plt.subplot(1,1,1)
    ax.scatter(sinc_all, rp_all, c = '0.75', s = marker_size, zorder = 0, label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(rp_all)))))
    ax.scatter(sinc_some, rp_some, c = 'k', s = marker_size, zorder = 0, label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(rp_some)))))
    ax.scatter(sinc, rp, c = '#ff8c00', s = marker_size, lw = 0.5, edgecolor = 'b', zorder = 2, label = r'$\rm SC1D \; [%s]$'%(str(int(len(rp)))))
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
    plt.xlim([15000., 1.])
    plt.ylim([0.9, 22.])
    plt.tight_layout()
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()

    # SC1E
    science_case = 'SC1E'
    program = df.query("in_%s == 1"%science_case)

    ms_all = df.m_s.values.tolist()
    feh_all = df.feh.values.tolist()
    ms_some = df2.m_s.values.tolist()
    feh_some = df2.feh.values.tolist()
    ms = program.m_s.values.tolist()
    feh = program.feh.values.tolist()

    lines = np.logspace(0,2,5)

    plt.figure(figsize = (14,8))

    ax = plt.subplot(1,1,1)
    ax.scatter(feh_all, ms_all, linestyle = 'None', marker = 'o', color = '0.75', s = marker_size, zorder = 1, label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(ms_all)))))
    ax.scatter(feh_some, ms_some, c = 'k', s = marker_size, zorder = 0, label = r'$\rm Vetted \; Sample \; [%s]$'%(str(int(len(ms_some)))))
    ax.scatter(feh, ms, linestyle = 'None', marker = 'o', color = 'orange', edgecolor = 'k',  s = marker_size, zorder = 2, label = r'$\rm SC1B \; [%s]$'%(str(int(len(ms)))))
    ax.set_xlabel(r'$\rm [Fe/H]$', fontsize = label_size)
    ax.set_ylabel(r'$\rm Mass \; [M_{\odot}]$', fontsize = label_size)
    ax.axhline(0.8, color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.axhline(1.2, color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.axvline(-0.25, color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.axvline(0.25, color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.axvline(0., color = 'k', linestyle = '--', linewidth = 0.75, zorder = 0)
    ax.set_xlim(-0.6, 0.6)
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
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
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
    ax.tick_params(labelsize = tick_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.set_yticks(np.arange(len(first)))
    labels = [r'$\rm TOI \, %s$'%label for label in labels]
    ax.set_yticklabels(labels)
    ax.set_xticks([0., 40., 80., 120., 160.])
    ax.set_xticklabels([r'$0$', r'$40$', r'$80$', r'$120$', r'$160$'])
    ax.xaxis.set_minor_locator(MultipleLocator(10))
    ax.set_xlim(-0.5, 165)
    ax.set_ylim(-0.5, y_upper)
    locs, labs = plt.xticks()
    for i in range(len(locs)):
        labs[i] = r"$%s$"%(str(int(locs[i])))
    ax.set_xticks(locs)
    ax.set_xticklabels(labs)

    ax2 = ax.twiny()
    ax2.tick_params(labelsize = tick_size)
    ax2.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax2.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax2.set_xticks([0., 40., 80., 120., 160.])
    ax2.set_xticklabels([r'$0$', r'$40$', r'$80$', r'$120$', r'$160$'])
    ax2.xaxis.set_minor_locator(MultipleLocator(10))
    ax2.set_xlim(-0.5, 165.)
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
    ax3.tick_params(labelsize = tick_size)
    ax3.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax3.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax3.set_yticks(np.arange(len(second)))
    labels = [r'$\rm TOI \, %s$'%label for label in labels]
    ax3.set_xticks([0., 40., 80., 120., 160.])
    ax3.set_xticklabels([r'$0$', r'$40$', r'$80$', r'$120$', r'$160$'])
    ax3.xaxis.set_minor_locator(MultipleLocator(10))
    ax3.set_yticklabels(labels)
    ax3.set_xlim(-0.5, 165.)
    ax3.set_ylim(-0.5, y_upper)

    ax4 = ax3.twiny()
    ax4.tick_params(labelsize = tick_size)
    ax4.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax4.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax4.set_xticks([0., 40., 80., 120., 160.])
    ax4.set_xticklabels([r'$0$', r'$40$', r'$80$', r'$120$', r'$160$'])
    ax4.xaxis.set_minor_locator(MultipleLocator(10))
    ax4.set_xlim(-0.5, 165.)
    ax4.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)
    
    plt.tight_layout()
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()

    """
    # SC2Bi
    science_case = 'SC2Bi'

    df = pd.read_csv('../data/program_overlap.csv')
    program = df.query("in_%s == 'X'"%science_case)

    science_filter = ''
    for tic in program.tic.values.tolist():
        science_filter += 'tic == %d or '%tic
    science_filter = science_filter[:-4]

    results = candidates.query(science_filter)

    rp = results.rp.values.tolist()
    sinc = results.sinc.values.tolist()

    plt.figure(figsize = (14,8))

    ax = plt.subplot(1,1,1)

    plt.tight_layout()
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()


    # SC2Bii
    science_case = 'SC2Bi'

    df = pd.read_csv('../data/program_overlap.csv')
    program = df.query("in_%s == 'X'"%science_case)

    science_filter = ''
    for tic in program.tic.values.tolist():
        science_filter += 'tic == %d or '%tic
    science_filter = science_filter[:-4]

    results = candidates.query(science_filter)

    rp = results.rp.values.tolist()
    sinc = results.sinc.values.tolist()

    plt.figure(figsize = (14,8))

    ax = plt.subplot(1,1,1)

    plt.tight_layout()
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()
    """


    # SC2C
    science_case = 'SC2C'
    program = df.query("in_%s == 1"%science_case)

    n_systems = list(set(program.tic.values.tolist()))
    y_upper = len(n_systems)-0.5

    rp = program.rp.values.tolist()
    per = program.period.values.tolist()

    labels = []

    plt.figure(figsize = (12,16))
    ax = plt.subplot(1,1,1)

    for i in range(len(n_systems)):
        query = program.query('tic == %d'%n_systems[i])
        for j in query.index.values.tolist():
            ax.scatter(query.loc[j]['period'], i, color = 'dodgerblue', s = 30.*(query.loc[j]['rp'])**(1.75), lw = 0.5, edgecolor = 'k')
        toi = int(np.floor(query.loc[j]['toi']))
        labels.append(str(toi))
    ax.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)
    ax.tick_params(labelsize = tick_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.set_yticks(np.arange(len(n_systems)))
    labels = [r'$\rm TOI \, %s$'%label for label in labels]
    ax.set_yticklabels(labels)
    ax.set_xticks([0., 10., 20., 30.])
    ax.set_xticklabels([r'$0$', r'$10$', r'$20$', r'$30$'])
    ax.set_xlim(-0.5, 39)
    ax.set_ylim(-0.5, y_upper)

    ax2 = ax.twiny()
    ax2.tick_params(labelsize = tick_size)
    ax2.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax2.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax2.set_xticks([0., 10., 20., 30.])
    ax2.set_xticklabels([r'$0$', r'$10$', r'$20$', r'$30$'])
    ax2.xaxis.set_minor_locator(MultipleLocator(5))
    ax2.set_xlim(-0.5, 39)
    ax2.set_xlabel(r'$\rm Period \; [days]$', fontsize = label_size)

    plt.tight_layout()
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()


    """
    # SC3
    science_case = 'SC3'

    df = pd.read_csv('../data/program_overlap.csv')
    program = df.query("in_%s == 'X'"%science_case)

    science_filter = ''
    for tic in program.tic.values.tolist():
        science_filter += 'tic == %d or '%tic
    science_filter = science_filter[:-4]

    results = candidates.query(science_filter)

    rp = results.rp.values.tolist()
    sinc = results.sinc.values.tolist()

    plt.figure(figsize = (14,8))

    ax = plt.subplot(1,1,1)


    plt.tight_layout()
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()
    """


    # SC4
    science_case = 'SC4'
    program = df.query("in_%s == 1"%science_case)

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
    ax.scatter(sinc, rp, c = '#ff8c00', s = marker_size, lw = 0.5, edgecolor = 'b', zorder = 2, label = r'$\rm SC4 \; [%s]$'%(str(int(len(rp)))))
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
    plt.xlim([15000., 1.])
    plt.ylim([0.9, 22.])
    plt.tight_layout()
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()


    # TOA
    science_case = 'TOA'
    program = df.query("in_other_programs != 0")

    rs = program.r_s.values.tolist()
    rs_some = df2.r_s.values.tolist()
    rs_all = df.r_s.values.tolist()
    teff = program.t_eff.values.tolist()
    teff_some = df2.t_eff.values.tolist()
    teff_all = df.t_eff.values.tolist()

    plt.figure(figsize = (14,10))
    ax = plt.subplot(1, 1, 1)

    ax.scatter(teff_all, rs_all, c = '0.75', s = marker_size, lw = 0.5, edgecolor = '0.6', zorder = 1, label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(rs_all)))))
    ax.scatter(teff_some, rs_some, c = 'k', s = marker_size, lw = 0.5, edgecolor = '0.6', zorder = 1, label = r'$\rm Full \; Sample \; [%s]$'%(str(int(len(rs_some)))))
    ax.scatter(teff, rs, c = '#ff8c00', s = marker_size, lw = 0.5, edgecolor = 'b', zorder = 2, label = r'$\rm TOA \; [%s]$'%(str(int(len(rs)))))
    ax.set_ylabel(r'$\rm R_{\star} \,\, [R_{\odot}]$', fontsize = label_size)
    ax.set_xlabel(r'$\rm Teff \,\, [K]$', fontsize = label_size)
    plt.yscale("log")
    ax.xaxis.set_major_locator(MultipleLocator(1000))
    ax.xaxis.set_minor_locator(MultipleLocator(250))
    ax.tick_params(axis = 'both', which = 'both', direction = 'inout')
    ax.tick_params(labelsize = tick_size)
    ax.tick_params(axis = 'both', which = 'minor', length = 5, width = 1, direction = 'inout')
    ax.tick_params(axis = 'both', which = 'major', length = 8, width = 2, direction = 'inout')
    ax.legend(fontsize = tick_size, loc = 'upper right', markerscale = marker_scale)
    ax.set_xticks([10000., 8000., 6000., 4000.])
    ax.set_xticklabels([r'$10000$', r'$8000$', r'$6000$', r'$4000$'])
    ax.set_yticks([1., 10.])
    ax.set_yticklabels([r'$10^{0}$', r'$10^{1}$'])
    ax.set_xlim([11500., 2900.])
    ax.set_ylim([0.2, 75.])
    plt.tight_layout()
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()

    """
    # TOB
    science_case = 'TOB'

    df = pd.read_csv('../data/program_overlap.csv')
    program = df.query("in_%s == 'X'"%science_case)

    science_filter = ''
    for tic in program.tic.values.tolist():
        science_filter += 'tic == %d or '%tic
    science_filter = science_filter[:-4]

    results = candidates.query(science_filter)

    rp = results.rp.values.tolist()
    sinc = results.sinc.values.tolist()

    plt.figure(figsize = (14,8))

    ax = plt.subplot(1,1,1)

    plt.tight_layout()
    if all:
        plt.savefig('results/plots/%s.png'%science_case)
        plt.show()
    else:
        if case is not None and science_case in case and show:
            plt.savefig('results/plots/%s.png'%science_case)
            plt.show()
    plt.close()
    """

    return

