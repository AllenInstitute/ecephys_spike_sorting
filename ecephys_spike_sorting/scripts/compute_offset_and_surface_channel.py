#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 14:51:18 2017

@author: joshs
"""

import glob    
import json
import os

import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import welch
from scipy.ndimage.filters import gaussian_filter1d

dataFolder = r'C:\\data\\706875901_388187_20180607_probeF_sorted\\'



# %%

def find_range(x,a,b,option='within'):
    """Find data within range [a,b]"""
    if option=='within':
        return np.where(np.logical_and(x>=a, x<=b))[0]
    elif option=='outside':
        return np.where(np.logical_or(x < a, x > b))[0]
    else:
        raise ValueError('unrecognized option paramter: {}'.format(option))


def rms(data):
    return np.power(np.mean(np.power(data.astype('float32'),2)),0.5)

def write_probe_json(output_file, channels, offset, scaling, mask, surface_chan, air_chan):

    with open(output_file, 'w') as outfile:
        json.dump( \
                  {  \
                        'channel' : channels.tolist(), \
                        'offset' : offset.tolist(), \
                        'scaling' : scaling.tolist(), \
                        'mask' : mask.tolist(), \
                        'surface_channel' : surface_chan, \
                        'air_channel' : air_chan
                   },
                 
                  outfile, \
                  indent = 4, separators = (',', ': ') \
                 ) 

# %%

def read_probe_json(input_file):
    
    with open(input_file) as data_file:
        data = json.load(data_file)

    totalChans = 384
    maxChan = 384
    
    full_mask = np.zeros((totalChans,totalChans))
    full_mask = full_mask > 1
    
    scaling = np.array(data['scaling'])
    mask = np.array(data['mask'])
    offset = np.array(data['offset'])
    surface_channel = data['surface_channel']
    air_channel = data['air_channel']

    period = 24
        
    for ch in range(0,totalChans):
        
        neighbors = np.arange(ch%period, maxChan, period).astype('int') # 1 neighbor is better than 2
        ok_chans = np.setdiff1d(neighbors, np.where(mask == False)[0])
        
        full_mask[ok_chans,ch] = True 

    return full_mask, offset, scaling, surface_channel, air_channel

# %%
    
def median_subtraction(spikes_file, full_mask, offset, scaling, totalChans):
    
    rawData = np.memmap(spikes_file, dtype='int16', mode='r+')
    
    for sample in range(0,100): #rawData.size/numChannels):
        
        start = sample*totalChans
        end = sample*totalChans + totalChans
        this_sample = np.copy(rawData[start:end])
        this_sample = this_sample - offset
        
        for ch in range(0,numChannels):
            
            m = np.where(full_mask[:,ch])[0]
            this_sample[ch] = int(float(this_sample[ch]) - float(np.median(this_sample[m]))*scaling[ch])
        
        rawData[start:end] = this_sample
        
    del rawData

def find_surface_channel(lfp_data, show_figure = False):
    
    # HARD-CODED PARAMETERS:
    nchannels = 384
    sample_frequency = 2500
    smoothing_amount = 5
    power_thresh = 2.0
    diff_thresh = -0.07
    freq_range = [0,10]
    channel_range = [370,380]
    n_passes = 1
    # END HARD-CODED PARAMETERS
    
    candidates = np.zeros((n_passes,))
    
    for p in range(n_passes):
        
        startPt = sample_frequency*100*p
        endPt = startPt + sample_frequency
    
        rawData = np.memmap(lfp_data, dtype='int16', mode='r')
        data = np.reshape(rawData, (int(rawData.size/nchannels), nchannels))
        
        channels = np.arange(nchannels)
        chunk = np.copy(data[startPt:endPt,channels])
        
        for channel in channels:
            chunk[:,channel] = chunk[:,channel] - np.median(chunk[:,channel])
            
        for channel in channels:
            chunk[:,channel] = chunk[:,channel] - np.median(chunk[:,channel_range[0]:channel_range[1]],1)
        
        nfft = 4096
        power = np.zeros((2049, channels.size))
    
        for channel in channels:
            sample_frequencies, Pxx_den = welch(chunk[:,channel], fs=sample_frequency, nfft=nfft)
            power[:,channel] = Pxx_den
        
        in_range = find_range(sample_frequencies, 0, 150)
        
        mask_chans = np.array([37, 76, 113, 152, 189, 228, 265, 304, 341, 380]) - 1
        
        in_range_gamma = find_range(sample_frequencies, freq_range[0],freq_range[1])
        
        values = np.log10(np.mean(power[in_range_gamma,:],0))
        values[mask_chans] = values[mask_chans-1]
        values = gaussian_filter1d(values,smoothing_amount)
                        
        try:
            surface_chan = np.max(np.where((np.diff(values) < diff_thresh) * (values[:-1] < power_thresh) )[0])
        except ValueError:
            surface_chan = 384
            
        candidates[p] = surface_chan
        
        if show_figure:
            plt.figure(figsize=(5,10))
            plt.subplot(4,1,1)
            plt.imshow(np.flipud((chunk).T), aspect='auto',vmin=-1000,vmax=1000)
            
            plt.subplot(4,1,2)
            plt.imshow(np.flipud(np.log10(power[in_range,:]).T), aspect='auto')
            
            plt.subplot(4,1,3)
            plt.plot(values) 
            plt.plot([0,384],[power_thresh,power_thresh],'--k')
  
            plt.plot([surface_chan, surface_chan],[-2, 2],'--r')
            
            plt.subplot(4,1,4)
            plt.plot(np.diff(values))
            plt.plot([0,384],[diff_thresh,diff_thresh],'--k')
            
            plt.plot([surface_chan, surface_chan],[-0.2, 0.07],'--r')
            plt.title(surface_chan)
            plt.show()
            
    surface_channel = np.median(candidates)
    air_channel = np.min([surface_channel + 100, 384])
        
    return surface_channel, air_channel

# %%

def compute_offset_and_surface_channel(dataFolder):

    f1 = os.path.join(dataFolder, os.path.join('continuous','Neuropix*.0'))
    f2 = os.path.join(dataFolder, os.path.join('continuous','Neuropix*.1'))

    ap_directory = glob.glob(f1)[0]
    lfp_directory = glob.glob(f2)[0]

    print(ap_directory)
    print(lfp_directory)

    hi_noise_thresh = 50.0
    lo_noise_thresh = 3.0
  
    output_file = os.path.join(dataFolder, 'probe_info.json')

    numChannels = 384

    offsets = np.zeros((numChannels,), dtype = 'int16')
    rms_noise = np.zeros((numChannels,), dtype='int16')
    lfp_power = np.zeros((numChannels,), dtype = 'float32')

    spikes_file = os.path.join(ap_directory, 'continuous.dat')
    lfp_file = os.path.join(lfp_directory, 'continuous.dat')

    # %%

    rawDataAp = np.memmap(spikes_file, dtype='int16', mode='r')
    dataAp = np.reshape(rawDataAp, (int(rawDataAp.size/numChannels), numChannels))

    mask_chans = np.array([37, 76, 113, 152, 189, 228, 265, 304, 341, 380]) - 1

    start_time = 30000*10
    recording_time = 90000
    median_subtr = np.zeros((recording_time,numChannels))

    # 1. cycle through to find median offset

    for ch in range(0,numChannels,1): #
        
        channel = dataAp[start_time:start_time+recording_time,ch]
        offsets[ch] = np.median(channel).astype('int16')
        median_subtr[:,ch] = channel - offsets[ch]
        rms_noise[ch] = rms(median_subtr[:,ch])*0.195

        if False:
            if ch % 1 == 0:
                if rms_noise[ch] > hi_noise_thresh:
                    plt.plot(median_subtr[:10000,ch]*0.195 + ch*200, 'r')
                elif rms_noise[ch] < lo_noise_thresh:
                    plt.plot(median_subtr[:10000,ch]*0.195 + ch*200, 'b')
                else:
                    plt.plot(median_subtr[:10000,ch]*0.195 + ch*200,'k')
            
    # %%
        
    excluded_chans1 = np.where(rms_noise > hi_noise_thresh)[0]
    excluded_chans2 = np.where(rms_noise < lo_noise_thresh)[0]
        
    mask_chans2 = np.concatenate((mask_chans, excluded_chans1, excluded_chans2))

    surface, air = find_surface_channel(lfp_file, False)

    print("Surface channel: " + str(surface))

    channels = np.arange(0,numChannels)
    mask = np.ones((channels.shape), dtype=bool)
    mask[mask_chans2] = False
    scaling = np.ones((numChannels,))

    write_probe_json(output_file, channels, offsets, scaling, mask, surface, air)

        # %%

