# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 15:43:18 2017

@author: joshs

Added bootstrap and signaltonoise by Xiaoxuan Jia 

"""

import numpy as np
import os
import glob
import pandas as pd

def signaltonoise(a, axis=0, ddof=0):
    """
    The signal-to-noise ratio of the input data.
    Returns the signal-to-noise ratio of `a`, here defined as the mean
    divided by the standard deviation.
    Parameters
    ----------
    a : array_like
        An array_like object containing the sample data.
    axis : int or None, optional
        Axis along which to operate. Default is 0. If None, compute over
        the whole array `a`.
    ddof : int, optional
        Degrees of freedom correction for standard deviation. Default is 0.
    Returns
    -------
    s2n : ndarray
        The mean to standard deviation ratio(s) along `axis`, or 0 where the
        standard deviation is 0.
    """
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m/sd)

def bootstrap_resample(X, n=None):
    """ Bootstrap resample an array.
    Sample with replacement.
    From analysis/sampling.py.
    Parameters
    ----------
    X : array_like
      data to resample
    n : int, optional
      length of resampled array, equal to len(X) if n==None
    Results
    -------
    returns X_resamples
    """
    if n == None:
        n = len(X)
        
    resample_i = np.floor(np.random.rand(n)*len(X)).astype(int)
    X_resample = X[resample_i]
    return X_resample
    
def snr(W):
    """Calculate snr of sorted units based on Xiaoxuan's matlab code. 
    W: (waveforms from all spike times), first dim is rep
    ref: (Nordhausen et al., 1996; Suner et al., 2005)
    """
    W_bar = np.nanmean(W,axis=0)
    A = max(W_bar) - min(W_bar)
    e = W - np.tile(W_bar,(np.shape(W)[0],1))
    snr = A/(2*np.nanstd(e.flatten()))
    return snr   
    
def get_peak_ch(mean_waveforms):
    """Calculate peak channel based on mean waveforms."""
    delta = np.max(mean_waveforms, axis=0)-np.min(mean_waveforms, axis=0)                     
    ch_peak = np.where(delta==max(delta))[0][0]
    return ch_peak

    
def extract_waveforms(rawDataFile, kilosort_path, numChannels, nBoots =100):
    """Re-calculate waveforms for sorted clusters from raw data.
    Bootstrap for units with more than 100 spikes.
    n=100
    boots=100
    """

    clustersFile = os.path.join(kilosort_path,'spike_clusters.npy')
    spikeTimesFile = os.path.join(kilosort_path,'spike_times.npy')
    clusterGroupsFile =     os.path.join(kilosort_path,'cluster_group.tsv')
    
    waveformsFile = os.path.join(kilosort_path, 'mean_waveforms.npy')
    SNRFile = os.path.join(kilosort_path, 'SNR.npy')
    templatesFile = os.path.join(kilosort_path, 'templates.npy')

    samplesPerSpike = 82
    preSamples = 20
    total_waveforms = 100

    numBytes = os.path.getsize(rawDataFile)
    numRecords = numBytes/numChannels/2

    rawData = np.memmap(rawDataFile, dtype='int16', mode='r')
    data = np.reshape(rawData, (rawData.size/numChannels, numChannels))

    clusters = np.load(clustersFile)
    spike_times = np.load(spikeTimesFile)
    templates = np.load(templatesFile)
    cluster_nums = np.unique(clusters)
    cluster_groups = pd.read_csv(clusterGroupsFile, sep='\t')
    
    new_clusters = np.zeros(clusters.size, dtype = np.int16)
    
    # 1. relabel clusters as consecutive integers
    for cluster_idx, cluster_num in enumerate(cluster_nums):
        
        in_cluster = np.where(clusters == cluster_num)[0]
        new_clusters[in_cluster] = int(cluster_idx)
        cluster_groups.ix[cluster_idx, 0] = int(cluster_idx)

    del clusters, cluster_nums
    clusters = new_clusters
    cluster_nums = np.unique(clusters)
    print(cluster_nums)
        
    mean_waveforms = np.zeros((np.max(clusters)+1,samplesPerSpike,numChannels))
    SNR = np.zeros((np.max(clusters)+1,2)) # 0: snr; 1: peak_channel

    # 2. extract mean waveforms and save
    for cluster_idx, cluster_num in enumerate(cluster_nums):
        print(cluster_num)
        in_cluster = np.where(clusters == cluster_num)[0]
        times_for_cluster = spike_times[in_cluster]
        
        if times_for_cluster.size > total_waveforms:
            TW = total_waveforms
        else:
            TW = times_for_cluster.size
            
        boots = nBoots

        if times_for_cluster.size > total_waveforms:
            waveform_boots = np.zeros((boots,samplesPerSpike, numChannels))
            SNR_boots=np.zeros((boots,samplesPerSpike, numChannels))
            for i in range(boots):
                times_boot = bootstrap_resample(times_for_cluster,n=total_waveforms)
                waveforms = np.zeros((samplesPerSpike, numChannels, TW))
                for wv_idx in range(0, TW):
                    peak_time = times_boot[wv_idx][0]
                    rawWaveform = data[int(peak_time-preSamples):int(peak_time+samplesPerSpike-preSamples),:]
                    try:
                        normWaveform = rawWaveform - np.tile(rawWaveform[0,:],(samplesPerSpike,1))
                        waveforms[:, :, wv_idx] = normWaveform
                    except ValueError:
                        waveforms[:, :, wv_idx] = np.nan
                SNR_boots[i,:,:]=signaltonoise(waveforms, axis=2)
                waveform_boots[i,:,:]=np.nanmean(waveforms,2)
            tmp = np.squeeze(np.mean(waveform_boots,0))
            mean_waveforms[cluster_num, :, :] = tmp
            ch_peak = get_peak_ch(tmp)
            SNR[cluster_num, 0]=ch_peak
            SNR[cluster_num, 1]=snr(waveforms[:,ch_peak,:].T) 
        else:
            waveforms = np.zeros((samplesPerSpike, numChannels, TW))
            for wv_idx in range(0, TW):
                peak_time = times_for_cluster[wv_idx][0]
                rawWaveform = data[int(peak_time-preSamples):int(peak_time+samplesPerSpike-preSamples),:]
                try:
                    normWaveform = rawWaveform - np.tile(rawWaveform[0,:],(samplesPerSpike,1))
                    waveforms[:, :, wv_idx] = normWaveform
                except ValueError:
                    waveforms[:, :, wv_idx] = np.nan
            tmp = np.nanmean(waveforms,2)  
            mean_waveforms[cluster_num, :, :] = tmp
            ch_peak = get_peak_ch(tmp)
            SNR[cluster_num, 0]=ch_peak
            SNR[cluster_num, 1]=snr(waveforms[:,ch_peak,:].T)         
            
    np.save(waveformsFile, mean_waveforms)
    np.save(SNRFile, SNR)
    np.save(clustersFile, clusters)
    cluster_groups.to_csv(clusterGroupsFile, sep='\t', index=False)
    

