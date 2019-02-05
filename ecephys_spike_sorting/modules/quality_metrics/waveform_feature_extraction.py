# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 16:50:21 2018

@author: Xiaoxuan Jia
"""
### Corresponds to notebook probe_analysis_waveform_2D


# extract waveform features
import numpy as np
import random
import cPickle as pkl
import pandas as pd
import h5py
import os, sys, glob, copy
import os.path
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import linregress
from scipy.signal import argrelextrema, resample
from scipy.cluster.vq import kmeans2


# general functions used by class
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

#--------------functions to extract 1D waveform features -------------
def get_waveform_duration(waveform, sampling_rate=30000.):
    w = resample(waveform,200)#upsample to smooth the data
    time = np.linspace(0,len(waveform)/sampling_rate,200)
    trough = np.where(w==np.min(w))[0][0]
    peak = np.where(w==np.max(w))[0][0]
    #print(peak, trough)
    #print(w[peak], w[trough])
    
    #dur =   time[trough:][np.where(w[trough:]==np.max(w[trough:]))[0][0]] - time[trough]
    if w[peak] > np.abs(w[trough]):
        dur =   time[peak:][np.where(w[peak:]==np.min(w[peak:]))[0][0]] - time[peak] 
    else:
        dur =   time[trough:][np.where(w[trough:]==np.max(w[trough:]))[0][0]] - time[trough] 
    return dur

def get_waveform_halfwidth(waveform, sampling_rate=30000.):
    """spike width at half amplitude <0.8ms FS; >0.8ms RS"""
    w = resample(waveform,200)#upsample to smooth the data
    time = np.linspace(0,len(waveform)/sampling_rate,200)
    trough = np.where(w==np.min(w))[0][0]
    peak = np.where(w==np.max(w))[0][0]
    
    #dur =   time[trough:][np.where(w[trough:]==np.max(w[trough:]))[0][0]] - time[trough]
    if w[peak] > np.abs(w[trough]):
        dur =   time[peak:][np.where(w[peak:]>=0.5*np.min(w[peak:]))[0][0]] - time[peak] 
    else:
        dur =  time[trough:][np.where(w[trough:]<=0.5*np.max(w[trough:]))[0][0]] - time[trough] 
    if peak<trough:
        dur=-dur
    return dur

def get_waveform_PTratio(waveform, sampling_rate=30000.):
    w = resample(waveform,200)#upsample to smooth the data
    time = np.linspace(0,len(waveform)/sampling_rate,200)
    peak = np.where(w==np.max(w))[0][0]
    trough = np.where(w==np.min(w))[0][0]
    ratio = w[peak]/abs(w[trough])
    if ratio > 1.:
        return 1.
    else:
        return w[peak]/abs(w[trough])

def get_waveform_repolarizationslope(waveform, sampling_rate=30000.,window=20):
    # accurate unit for time (second), upsample to avoid NaN
    w = resample(waveform,200)#upsample to smooth the data
    time = np.linspace(0,len(waveform)/sampling_rate,200)
    trough = np.where(w==np.min(w))[0][0]
    peak = np.where(w==np.max(w))[0][0]
    
    if w[peak] > np.abs(w[trough]):
        w = -w
        trough = np.where(w==np.min(w))[0][0]
    return linregress(time[trough:trough+window],w[trough:trough+window])[0]

def get_waveform_recoveryslope(waveform, sampling_rate=30000., window=20):
    w = resample(waveform,200)#upsample to smooth the data
    time = np.linspace(0,len(waveform)/sampling_rate,200)
    trough = np.where(w==np.min(w))[0][0]
    peak = np.where(w==np.max(w))[0][0]
    
    if w[peak] > np.abs(w[trough]):
        w = -w
        peak = np.where(w==np.max(w))[0][0]
    return linregress(time[peak:],w[peak:])[0]

def cluster_rsfs(durations, PTratio):
    """Use duration and PTratio to cluster into RS and FS neurons"""
    iter=1000
    # cluster for FS and RS neurons according to duration of spike and PTratio
    waveform_k = kmeans2(np.vstack((durations/np.max(durations),PTratio/np.max(PTratio))).T, 
        2, iter=iter, thresh=5e-6,minit='random')
    labels = waveform_k[1]
    return labels 

def plot_rsfs_waveforms(peak_waveform, durations, labels):
    """Plot example traces for rs and fs. Plot mean waveform.
    RS: 0; FS: 1
    """
    if np.mean(durations[np.where(labels==0)[0]]) < np.mean(durations[np.where(labels==1)[0]]):
        fs_k = 0;rs_k = 1
        waveform_class_ids = [1,0]
    else:
        rs_k = 0;fs_k = 1
        waveform_class_ids = [0,1]
    waveform_class = [waveform_class_ids[k] for k in labels]
    waveform_class = np.array(waveform_class)


    plt.figure(figsize=(6,4))
    for i in range(len(peak_waveform)):
        waveform = peak_waveform[i]
        if waveform_class[i]==np.unique(waveform_class)[0]:
            plt.plot(waveform/np.max(np.abs(waveform)),'#b3b3ff',alpha=0.7)
        if waveform_class[i]==np.unique(waveform_class)[1]:
            plt.plot(waveform/np.max(np.abs(waveform)),'#c6ecc6',alpha=0.7)


    # plot means, normalized
    for waveform_class_id in np.unique(waveform_class):
        plt.plot(np.mean(peak_waveform[waveform_class==waveform_class_id],axis=0)/
                 (np.max(np.abs(np.mean(peak_waveform[waveform_class==waveform_class_id],axis=0)))),lw=3,label=waveform_class_id)
    plt.title('Raw: RS:'+str(len(np.where(waveform_class==0)[0]))+', FS: '+str(len(np.where(waveform_class==1)[0])))
    return waveform_class


#---------------------------------------

def get_1d_features(waveforms):
    """Calculate duration, PTration, repolarization slope."""
    durations = []
    PTratio= []
    repolarizationslope= []
    recoveryslope = []
    for i in range(len(waveforms)): 
        waveform=waveforms[i,:] 
        durations.append(get_waveform_duration(waveform))
        PTratio.append(get_waveform_PTratio(waveform))
        repolarizationslope.append(get_waveform_repolarizationslope(waveform))
        recoveryslope.append(get_waveform_recoveryslope(waveform))
    return np.array(durations), np.array(PTratio), np.array(repolarizationslope), np.array(recoveryslope)


def get_2d_features(waveform_all_40, site_range=15, plot=False):
    """
    waveform_all_40: neuron*time*space
    Calculate features from 2D waveform plot:
    Amplitude: Amplitude of waveform
    Spread: Number of channels has more than 10% amplitude of maximum amplitude.
    Velo: list of two dimentional arrays:
            x: distance (micon) 
            y: time (microseconds)
    """
    sampling_rate=30. 
    threshold=0.12
    Amplitude=[]
    Spread=[]
    Velo= []
    for i in range(np.shape(waveform_all_40)[0]):
        temp = waveform_all_40[i,:,:]
        ttemp = temp[:,np.arange(0,site_range*2,2)]# same side as peak unit, largest waveform at unit_idx=10
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

            #normal
            time_to_peak[j]=time[peak]
            time_to_trough[j]=time[trough]
            amplitude_peak[j]=w[peak]
            amplitude_trough[j]=w[trough]
            peak_idx[j]=peak
            trough_idx[j]=trough
            dur[j]=time[trough:][np.where(w[trough:]==np.max(w[trough:]))[0][0]] - time[trough]
            
        # find local minima, interpolate waveform for noisy cases
        idx_minima_tmp = np.array(argrelextrema(amplitude_trough, np.less)[0])
        idx_minima=idx_minima_tmp[np.where(amplitude_trough[idx_minima_tmp]<-200)[0]]

        if len(idx_minima)>1:
            # more than 1 local minima, noisy 2D plots, smooth by averaging two columns
            #print(i, idx_minima)
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

                #normal
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
        
        if plot==True:
	        plt.figure(figsize=(16,8))
	        plt.subplot(231)
	        plt.imshow(ttemp.T, aspect=4)
	        plt.scatter(peak_idx, range(site_range))
	        plt.scatter(trough_idx, range(site_range))
	        plt.grid(False)
	        plt.plot([0,81],[spread_idx[0],spread_idx[0]],':r')
	        plt.plot([0,81],[spread_idx[-1],spread_idx[-1]],':r')
	        plt.title('0 is deep into cortex', fontsize=16)

	        plt.subplot(232)
	        tttemp=ttemp[:, spread_idx]
	        for i in range(len(spread_idx)):
	            plt.plot(tttemp[:,i]+400*i)
	        plt.yticks([])

	        plt.subplot(233)
	        peak_ch = int(site_range/2)
	        waveform=ttemp[:,peak_ch]
	        plt.plot(waveform)
	        plt.scatter(peak_idx[peak_ch], amplitude_peak[peak_ch])
	        plt.scatter(trough_idx[peak_ch], amplitude_trough[peak_ch])
	        plt.grid(False)
	        plt.title('Peak waveform', fontsize=16)

	        plt.subplot(234)
	        plt.plot(((np.arange(site_range)-peak_ch)*site_range),amplitude_peak)
	        plt.plot(((np.arange(site_range)-peak_ch)*site_range),amplitude_trough)
	        #plt.scatter(((np.arange(20)-10)*20)[idx_minima], amplitude_trough[idx_minima], c = 'b') #before smoothing
	        plt.grid(False)

	        plt.subplot(235)
	        plt.plot((np.arange(site_range)-peak_ch)*site_range, amplitude/max(amplitude))
	        plt.plot((np.arange(site_range)-peak_ch)*site_range,np.ones(site_range)*threshold,'k:')
	        plt.title('Amplitude', fontsize=16)
	        plt.xlabel('Distance from soma',fontsize=14)
	        plt.grid(False)

	        plt.subplot(236)
	        plt.plot(((np.arange(site_range)-peak_ch)*site_range)[spread_idx], ((time_to_trough-time_to_trough[peak_ch])*1/30.*1000.)[spread_idx])
	        plt.title('Velocity', fontsize=16)
	        plt.xlabel('Distance',fontsize=14)
	        plt.ylabel('Time',fontsize=12)
	        plt.grid(False)


    Spread = np.array(Spread)
    Amplitude = np.array(Amplitude)
    Velo = Velo
    return Spread, Amplitude, Velo


def get_velocity(Velo, plot=False):
    """Calculate slope above and below soma."""
    slope = np.zeros(np.shape(Velo))
    for idx, v in enumerate(Velo):
        if len(v)>0: # when v is not empty
            regress = linregress(v[0][v[0]>=0], v[1][v[0]>=0])
            slope[idx, 1]=regress[0]
            if plot==True:
	            plt.figure()
	            plt.plot(v[0][v[0]>=0], v[1][v[0]>=0])
	            plt.plot([0,v[0][-1]],[0,v[0][-1]*regress[0]])

            if len(v[0][v[0]<=0])>1:
                regress = linregress(v[0][v[0]<=0], v[1][v[0]<=0])
                slope[idx, 0]=regress[0]
                if plot==True:
	                plt.plot(v[0][v[0]<=0], v[1][v[0]<=0])
	                plt.plot([0,v[0][0]],[0,v[0][0]*regress[0]])
            else:
                slope[idx, 0]=np.NaN
        else:
            slope[idx, 1]=np.NaN
            slope[idx, 0]=np.NaN
    return slope


#def get_waveform_class(durations, PTratio, peak_waveform):
#	"""Label FS and RS for kmeans classification according to duration. """
#    if len(durations)>1:
#    	labels = cluster_rsfs(durations, PTratio)
    	#labels = plot_rsfs_waveforms(peak_waveform, durations, labels_tmp)
#    else:
#        labels = 0

#    return labels


"""
def save_to_file(filename):
    f = file(filename, 'wb')
    pkl.dump([waveform_all_40, self.ch_id_all_40, self.Spread, self.Velo, self.slope, self.labels, self.durations[self.index_40], 
        self.PTratio[self.index_40], self.repolarizationslope[self.index_40], self.recoveryslope[self.index_40]], f)
    f.close()

def save_to_file_unit(self, filename):
    
    f = file(filename, 'wb')
    pkl.dump([self.waveform_all_40, self.ch_id_all_40, self.Spread, self.Velo, self.slope, self.labels, self.durations[self.index_40], 
        self.PTratio[self.index_40], self.repolarizationslope[self.index_40], self.recoveryslope[self.index_40], self.unit_list_40], f)
    f.close()
"""


