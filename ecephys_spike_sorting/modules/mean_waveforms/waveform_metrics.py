# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 16:50:21 2018

@author: Xiaoxuan Jia
"""
# Corresponds to notebook probe_analysis_waveform_2D


# extract waveform features
import numpy as np
import random
import pandas as pd
import h5py
import os
import sys
import glob
import copy

from scipy.stats import linregress
from scipy.signal import argrelextrema, resample
from scipy.cluster.vq import kmeans2


def calculate_waveform_metrics(waveforms, cluster_id, peak_channel, sample_rate, upsampling_factor, epoch_name):
    """Calculate metrics for an array of waveforms

    Inputs:
    -------
    waveforms : numpy.ndarray (num_spikes x num_channels x num_samples)
        Can include NaN values for missing spikes
    cluster_id : Int
        ID for cluster
    peak_channel : Int
        Location of waveform peak
    sample_rate : float
        Sample rate in Hz
    upsampling_factor : float
        Relative rate at which to upsample the spike waveform
    epoch_name : str
        Name of epoch for which these waveforms originated

    Outputs:
    -------
    metrics : pandas.DataFrame
        Single-row table containing all metrics

    """

    snr = calculate_snr(waveforms[:, peak_channel, :])

    mean_2D_waveform = np.nanmean(waveforms, 0)

    num_samples = mean_2D_waveform.shape[1]
    new_sample_count = int(num_samples * upsampling_factor)

    mean_1D_waveform = resample(
        mean_2D_waveform[peak_channel, :], new_sample_count)
    timestamps = np.linspace(0, len(mean_1D_waveform) /
                             sampling_rate, new_sample_count)

    duration = calculate_waveform_duration(mean_1D_waveform, timestamps)
    halfwidth = calculate_waveform_halfwidth(mean_1D_waveform, timestamps)
    PT_ratio = calculate_waveform_PT_ratio(mean_1D_waveform)
    repolarization_slope = calculate_waveform_repolarization_slope(
        mean_1D_waveform, timestamps)
    recovery_slope = calculate_waveform_recovery_slope(
        mean_1D_waveform, timestamps)

    amplitude, spread, velocity_above, velocity_below = calculate_2D_features(
        mean_2D_waveform)

    data = [[cluster_id, epoch_name, peak_channel, snr, duration, halfwidth, PT_ratio, repolarization_slope,
              recovery_slope, amplitude, spread, velocity_above, velocity_below]]

    metrics = pd.DataFrame(data,
                           columns=['cluster_id', 'epoch_name', 'peak_channel', 'snr', 'duration', 'halfwidth',
                                     'PT_ratio', 'repolarization_slope', 'recovery_slope', 'amplitude',
                                     'spread', 'velocity_above', 'velocity_below'])

    return metrics


# ==========================================================

# EXTRACTING 1D FEATURES

# ==========================================================


def calculate_snr(W):
    """Calculate SNR of spike waveforms.

    Converted from Matlab by Xiaoxuan Jia

    ref: (Nordhausen et al., 1996; Suner et al., 2005)

    Input:
    -------
    W : array of N waveforms (N x samples)

    Output:
    snr : signal-to-noise ratio for unit (scalar)

    """

    W_bar = np.nanmean(W, axis=0)
    A = np.max(W_bar) - np.min(W_bar)
    e = W - np.tile(W_bar, (np.shape(W)[0], 1))
    snr = A/(2*np.nanstd(e.flatten()))

    return snr


def calculate_waveform_duration(waveform, timestamps):
    """ Duration (in seconds) between peak and trough

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)
    timestamps : numpy.ndarray (N samples)

    Outputs:
    --------
    duration : waveform duration in seconds

    """

    trough_idx = np.argmin(waveform)
    peak_idx = np.argmax(waveform)

    duration = np.abs(timestamps[peak_idx] - timestamps[trough_idx])

    return duration


def calculate_waveform_halfwidth(waveform, timestamps):
    """ Spike width (in seconds) at half max amplitude

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)
    timestamps : numpy.ndarray (N samples)

    Outputs:
    --------
    halfwidth : waveform halfwidth in seconds

    """

    trough_idx = np.argmin(waveform)
    peak_idx = np.argmax(waveform)

    if waveform[peak_idx] > np.abs(waveform[trough_idx]):
        threshold = waveform[peak_idx] * 0.5
        thresh_crossing_1 = np.min(
            np.where(waveform[:peak_idx] > threshold)[0])
        thresh_crossing_2 = np.min(
            np.where(waveform[peak_idx:] < threshold)[0]) + peak_idx
    else:
        threshold = waveform[trough_idx] * 0.5
        thresh_crossing_1 = np.min(
            np.where(waveform[:trough_idx] < threshold)[0])
        thresh_crossing_2 = np.min(
            np.where(waveform[trough_idx:] > threshold)[0]) + trough_idx

    halfwidth = timestamps[thresh_crossing_2] - timestamps[thresh_crossing_1]

    return halfwidth


def calculate_waveform_PT_ratio(waveform):

    """ Peak-to-trough ratio of 1D waveform

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)

    Outputs:
    --------
    PT_ratio : waveform peak-to-trough ratio

    """

    trough_idx = np.argmin(waveform)

    peak_idx = np.argmax(waveform)

    PT_ratio = np.abs(waveform[peak_idx] / waveform[trough_idx])

    return PT_ratio


def calculate_waveform_repolarization_slope(waveform, timestamps, window=20):
    
    """ Spike repolarization slope (after maximum deflection point)

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)
    timestamps : numpy.ndarray (N samples)
    window : int
        Window (in samples) for linear regression

    Outputs:
    --------
    repolarization_slope : slope of return to baseline

    """

    max_point = np.argmax(np.abs(waveform))

    waveform = - waveform * (np.sign(waveform[max_point])) # invert if we're using the peak

    repolarization_slope = linregress(timestamps[max_point:max_point+window], waveform[max_point:max_point+window])[0]

    return repolarization_slope



def calculate_waveform_recovery_slope(waveform, sampling_rate=30000., window=20):

    """ Spike recovery slope (after repolarization)

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)
    timestamps : numpy.ndarray (N samples)
    window : int
        Window (in samples) for linear regression

    Outputs:
    --------
    recovery_slope : slope of recovery period

    """

    max_point = np.argmax(np.abs(waveform))

    waveform = - waveform * (np.sign(waveform[max_point])) # invert if we're using the peak

    peak_idx = np.argmax(waveform[max_point:]) + max_point

    recovery_slope = linregress(time[peak_idx:peak_idx+window],w[peak_idx:peak_idx+window])[0]

    return recovery_slope


# ==========================================================

# EXTRACTING 2D FEATURES

# ==========================================================


def calculate_2d_features(waveform, timestamps, peak_channel, spread_threshold = 0.12, site_range=16):
    
    """ Compute features of 2D waveform (channels x samples)

    Inputs:
    ------
    waveform : numpy.ndarray (N samples)
    timestamps : numpy.ndarray (N samples)
    peak_channel : int
    site_range: int

    Outputs:
    --------
    amplitude : 
    spread : 
    velocity_above : 
    velocity_below : 

    """

    """
    waveform_all_40: neuron*time*space
    Calculate features from 2D waveform plot:
    Amplitude: Amplitude of waveform
    Spread: Number of channels has more than 10% amplitude of maximum amplitude.
    Velo: list of two dimentional arrays:
            x: distance (micon) 
            y: time (microseconds)
    """

    assert site_range % 2 == 0 # must be even

    sites_to_sample = np.arange(np.arange(-site_range, site_range+1, 2)) + peak_channel

    wv = waveform[sites_to_sample, :]

    trough_idx = np.argmin(wv,1)
    trough_amplitude = np.min(wv,1)

    peak_idx = np.argmax(wv,1)
    peak_ampliutde = np.max(wv,1)

    duration = np.abs(timestamps[peak_idx] - timestamps[trough_idx])
        
    # find local minima, interpolate waveform for noisy cases
    idx_minima_tmp = np.array(argrelextrema(trough_amplitude, np.less)[0])
    idx_minima=idx_minima_tmp[np.where(trough_amplitude[idx_minima_tmp]<-200)[0]]

    if len(idx_minima)>1:
        # more than 1 local minima, noisy 2D plots, smooth by averaging two columns
        # print(i, idx_minima)
        del ttemp, time_to_peak, time_to_trough, amplitude_peak, amplitude_trough, dur, peak_idx, trough_idx
        temp = waveform_all_40[i,:,:]
        for i in range(site_range-2):
            temp[:,i+1]=interpolation_matrix(temp[:,i:i+2])
        ttemp = temp# same side as peak unit, largest waveform at unit_idx=10
        time_to_peak=np.zeros(site_range)
        time_to_trough=np.zeros(site_range)
        amplitude_peak=np.zeros(site_range)
        amplitude_trough=np.zeros(site_range)
        dur=np.zeros(site_range)
        peak_idx=np.zeros(site_range)
        trough_idx=np.zeros(site_range)
        for j in range(site_range):
            w = ttemp[:,j]
            time = range(temp.shape[0])
            trough = np.where(w==np.min(w))[0][0]
            peak = np.where(w==np.max(w))[0][0]

            # normal
            time_to_peak[j]=time[peak]
            time_to_trough[j]=time[trough]
            amplitude_peak[j]=w[peak]
            amplitude_trough[j]=w[trough]
            peak_idx[j]=peak
            trough_idx[j]=trough
            dur[j]=time[trough:][np.where(w[trough:]==np.max(w[trough:]))[0][0]] - time[trough]

    
    amplitude = amplitude_peak-amplitude_trough
    spread_tmp = np.where(amplitude>(max(amplitude)*threshold))[0]
    
    if len(spread_tmp)>1:
        # remove outlier for noisy maps
        spread_idx = spread_tmp[isnot_outlier(spread_tmp)]
    else:
        spread_idx = spread_tmp
    
    Spread.append(len(spread_idx))
    Amplitude.append(amplitude)
    peak_ch = int(site_range/2)
    waveform=ttemp[:,peak_ch]
    
    Velo.append([((np.arange(site_range)-peak_ch)*site_range)[spread_idx], ((time_to_trough-time_to_trough[peak_ch])*1/30.*1000.)[spread_idx]])
    
 
    return amplitude, spread, velocity_above, velocity_below


def get_velocity(Velo, plot=False):
    """Calculate slope above and below soma."""
    slope = np.zeros(np.shape(Velo))
    for idx, v in enumerate(Velo):
        if len(v)>0: # when v is not empty
            regress = linregress(v[0][v[0]>=0], v[1][v[0]>=0])
            slope[idx, 1]=regress[0]

            if len(v[0][v[0]<=0])>1:
                regress = linregress(v[0][v[0]<=0], v[1][v[0]<=0])
                slope[idx, 0]=regress[0]
            else:
                slope[idx, 0]=np.NaN
        else:
            slope[idx, 1]=np.NaN
            slope[idx, 0]=np.NaN
    return slope

# ==========================================================

# HELPER FUNCTIONS:

# ==========================================================

def interpolation_array(a1, a2):

    """Interpolate between two arrays by taking the mean of the two arrays."""

    return (a1+a2)/2.


def interpolation_matrix(m):

    """Interpolate between two arrays by taking the mean of the two arrays."""

    return np.nanmean(m,axis=1)


def isnot_outlier(points, thresh=1.5):

    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """

    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score <= thresh
