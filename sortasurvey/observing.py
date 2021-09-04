import numpy as np
import pandas as pd
from scipy.optimize import brentq
pd.set_option('mode.chained_assignment', None)




class Instrument:

    def __init__(self, survey):
        # General survey information
        self.name = survey.instrument
        # General survey observing/instrument information
        self.archival, self.overhead = survey.params['archival'], survey.params['overhead']
        self.time_lower, self.time_upper = survey.params['time_lower'], survey.params['time_upper']

    def __call__(self, teff, vmag, method, template=False, nobs=0):
        self.teff = teff
        self.vmag = vmag
        self.template = template
        self.nobs = nobs
        # Specific observing method (which can vary depending on science case)
        self.counts = method.split('=')[-1]
        self.nobs_goal = int(float((method.split('-')[1]).split('=')[-1]))
        if self.counts == 'ramp':
            self.counts = self.exp_ramp()
        else:
            self.counts = float(self.counts)
        # Initialize specific instrument (+ cost function)
        # Available instruments
        instruments={'hires':HIRES,'apf':APF,'kpf',KPF}
        inst = instruments[self.name]
        inst.cost_function()
        return inst.rem_time

    def cost_function(self):
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
        # estimate how much time a target would take, given a program's observing method
        self.exposure_time()
        # make a cut at a survey's maximum allowable exposure time per observation
#        exp = np.clip(exp, self.time_lower, self.time_upper)
        # include archival data in total time estimates
        if self.archival:
            self.rem_nobs = int(self.nobs_goal-self.nobs)
            if self.rem_nobs < 0:
                self.rem_nobs = 0
                self.rem_time = 0.
        else:
            self.rem_nobs = self.nobs_goal
        self.rem_time = self.exp_time*self.rem_nobs+self.overhead*self.rem_nobs
        # if a template has not been acquired for a target yet
        if not self.template:
            self.counts = 250.
            self.exposure_time(iodine=False)
            exp = np.clip(exp, self.time_lower, self.time_upper)
            self.rem_time += (self.exp_time+self.overhead)


class HIRES(Instrument):

    def __init__(self):
        # General instrument information

    def exposure_time(self, iodine=False, vmag_0=8., time_0=110., counts_0=250., iodine_factor=0.7):
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
        fluxfactor = 10.0**(-0.4*(self.vmag-vmag_0)) 
        self.exp_time = time_0/fluxfactor 
        self.exp_time *= self.counts/counts_0
        if not iodine:
            self.exp_time *= iodine_factor


    def exp_ramp(self, vmag_1=10.5, vmag_2=12.0, counts_1=250., counts_2=60.):
        """
        Calculates exposure counts based on a minimum (v1) and maximum (v2)
        magnitude limits, with a linear ramp between the two magnitude limits.

        Parameters
        ----------
        vmag : float 
            target magnitude
        vmag_1 : float 
            below this mag targets get full counts (c1)
        vmag_2 : float
            fainter than this mag targets get c2
        counts_1 : float
            expcounts (k) for bright targets
        counts_2 : float
            expcounts (k) for the faint limit

        Returns
        -------
        counts : float
            expected number of photon counts (x1000)

        """
        if self.vmag <= vmag_1:
            return counts_1
        if self.vmag >= vmag_2:
            return counts_2
        exp_level = np.interp(vmag, xp=[vmag_1, vmag_2], fp=[np.log10(counts_1), np.log10(counts_2)])
        self.counts = 10.**exp_level


    def counts_to_err_hires(self):
        '''
        Compute the expected RV error for an iodine-in observation, scaling from 2.5 m/s at 250k counts

        '''
        self.err = 2.0/np.sqrt(self.counts/60.0)



class APF(Instrument):

    def __init__(self):
        # General instrument information

    def exposure_time(self, vmag_0=22.9, time_0=1e9, iodine_factor=0.7, decker='M',
                      scale={'M':1.0,'W':1.0,'N':3.0,'B':0.5,'S':2.0,'L':0.5},):
        """
        Calculate expected exposure time for an APF observation

        Parameters
        ----------
        vmag : float
            V-band magnitude 
        counts : float
            Desired exposure meter counts (i.e. 1.0 = 1.0G, SNR~155/pix)
        decker : str, Optional 
            The decker for observation, default is `M`.

        Returns
        -------
        exp_time : float
            exposure time in seconds

        """
        fluxfactor = 10.0**(-0.4*(self.vmag-vmag_0))
        self.exp_time = (self.counts*time_0)/fluxfactor
        if decker in scale:
            self.exp_time *= scale[decker]
        if not iodine:
            self.exp_time *= iodine_factor


    def counts_to_err_apf(self):
        """
        Compute the expected RV error for an iodine-in observation, scaling from 2.5 m/s at 250k counts

        """
        self.err = 3.0/np.sqrt(self.counts/0.3)


class KPF(Instrument):

    def __init__(self):
        # General instrument information

    def exposure_time(self, wavelength=550.0, ind=2, minout=0.):
        """
        Estimates the exposure time required to reach a specified signal-to-noise
        value (snr) at a specified wavelength for a given stellar target. The
        target is defined by the stellar effective temperature (teff) and V
        magnitude (vmag)

        This function interpolates over a pre-computed grid of RV uncertainty values
        to estimate the optimum exposure length. This is done by looping through
        'trial' exposure time guesses to see which yields sigma_rv closest to the
        desired value.

        Parameters
        ----------
        teff : :obj:`float`
            Target effective temperature
        vmag : :obj:`float`
            Target V magnitude
        snr : :obj:`float`
            Desired spectral SNR
        wavelength : :obj:'float'
            Wavelength of desired SNR

        Returns
        -------
        exptime : :obj:`float`
            Estimated exposure time for reaching specified snr

        """
        # Grid files for teff, vmag, exp_time
        teff_grid_file = os.path.join(os.path.abspath(os.getcwd()), 'info', 'photon_grid_teff.fits')
        vmag_grid_file = os.path.join(os.path.abspath(os.getcwd()), 'info', 'photon_grid_vmag.fits')
        exp_time_grid_file = os.path.join(os.path.abspath(os.getcwd()), 'info', 'photon_grid_exptime.fits')
        wvl_ord_file = os.path.join(os.path.abspath(os.getcwd()), 'info', 'order_wvl_centers.fits')
        # Master grid files for interpolation
        snr_grid_file = os.path.join(os.path.abspath(os.getcwd()), 'info', 'snr_master_order.fits')
        snr_grid_all = fits.getdata(snr_grid_file)    
        # find closest order to specified wavelength
        wvl_ords = np.array(fits.getdata(wvl_ord_file)[1])
        idx = (np.abs(wvl_ords - wavelength)).argmin()
        snr_grid = snr_grid_all[idx]
        # read in data cubes and arrays
        teff_grid = fits.getdata(teff_grid_file)
        vmag_grid = fits.getdata(vmag_grid_file)
        exptime_grid = fits.getdata(exp_time_grid_file)
        logexp = np.log10(exptime_grid)
        # Get fractional indices for relevant input parameters
        teff_index_spline = InterpolatedUnivariateSpline(teff_grid,np.arange(len(teff_grid),dtype=np.double))
        vmag_index_spline = InterpolatedUnivariateSpline(vmag_grid,np.arange(len(vmag_grid),dtype=np.double))
        teff_location = teff_index_spline(self.teff)
        vmag_location = vmag_index_spline(self.vmag)
        # while trial exposure time yields worse precision, keep increasing until
        # you reach specified sigma_rv
        while minout < self.snr:
            # dummy guess trial exposure
            trial_exp = min(exptime_grid)+ind
            # fractional index for trial exposure time in exptime_grid
            exptime_index = InterpolatedUnivariateSpline(logexp, np.arange(len(exptime_grid),dtype=np.double))(np.log10(trial_exp))
            # recompute expected SNR based on trial exposure time
            snr_interpolator = RegularGridInterpolator((np.arange(len(exptime_grid)),np.arange(len(vmag_grid)),np.arange(len(teff_grid))),snr_grid)
            inputs = [exptime_index, vmag_location, teff_location]
            # store as new maximum
            minout = snr_interpolator(inputs)[0]
            # increase exposure time by 1 second
            ind += 1
        # last 'trial' exposure time is correct answer
        self.exp_time = trial_exp