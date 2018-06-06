#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 14:51:18 2017

@author: joshs
"""

import glob    
import json
import os

dataFolder = '/mnt/md0/data/mouse380483/probeE'

ap_directory = glob.glob(dataFolder + '/continuous/Neuropix*.0')[0]
lfp_directory = glob.glob(dataFolder + '/continuous/Neuropix*.1')[0]

# %%

from scipy.optimize import minimize

def rms(data):
    return np.power(np.mean(np.power(data,2)),0.5)

def func(x, channel, M):
    
    corrected = channel - M * x
    error = rms(corrected)
    
    return error

# %%
  
output_file = os.path.join(dataFolder, 'probe_info.json')

numChannels = 384

offsets = np.zeros((numChannels,), dtype = 'int16)
rms_noise = np.zeros((numChannels,), dtype='int16')
lfp_power = np.zeros((numChannels,), dtype = 'float32')

spikes_file = os.path.join(ap_directory, 'continuous.dat')
lfp_file = os.path.join(lfp_directory, 'continuous.dat')

# %%

from scipy import signal

rawDataAp = np.memmap(spikes_file, dtype='int16', mode='r')
dataAp = np.reshape(rawDataAp, (int(rawDataAp.size/numChannels), numChannels))

mask_chans = np.array([37, 76, 113, 152, 189, 228, 265, 304, 341, 380]) - 1

start_time = 30000*10
recording_time = 30000
median_subtr = np.zeros((recording_time,numChannels))

offsets = np.zeros((numChannels,))

# 1. cycle through to find median offset
for ch in range(0,numChannels,1): #
    
    channel = dataAp[start_time:start_time+recording_time,ch].astype('float32')
    #a
    offsets[ch] = np.nanmedian(channel).astype('int16')

    median_subtr[:,ch] = channel - offsets[ch]
    
    f,Pxx = signal.welch(median_subtr[:2500,ch],fs=30000,nfft=2048)
    
    rms_noise[ch] = rms(median_subtr[:,ch]).astype('int16')
    lfp_power[ch] = np.log10(Pxx[7])
    
    
# %%
    
excluded_chans1 = np.where(rms_noise > 300)[0]
excluded_chans2 = np.where(rms_noise < 45)[0]
    
mask_chans2 = np.concatenate((mask_chans, excluded_chans1, excluded_chans2))


# %%

from scipy.ndimage.filters import gaussian_filter1d

rawDataLfp = np.memmap(lfp_file, dtype='int16', mode='r')
dataLfp = np.reshape(rawDataLfp, (int(rawDataLfp.size/numChannels), numChannels))

mask_chans = np.array([37, 76, 113, 152, 189, 228, 265, 304, 341, 380]) - 1

start_time = 2500*10
recording_time = 2500
median_subtr = np.zeros((recording_time,numChannels))

# 1. cycle through to find median offset
for ch in range(0,numChannels,1): #
    
    channel = dataLfp[start_time:start_time+recording_time,ch].astype('float32')
    #a
    offset = np.nanmedian(channel)

    median_subtr = channel - offset
    
    f,Pxx = signal.welch(median_subtr,fs=2500,nfft=2048)
    lfp_power[ch] = np.log10(Pxx[20])
    
lfp_power[mask_chans2] = lfp_power[mask_chans2-1]    
low_power = np.where(lfp_power < 1.0)[0]
lfp_power[low_power] = lfp_power[low_power-1]
lfp_power = gaussian_filter1d(lfp_power,2)

plt.figure(191211)
plt.clf()
    
plt.subplot(1,3,1)
plt.plot(offsets)

plt.subplot(1,3,2)
plt.plot(rms_noise)

plt.plot([0,numChannels],[300,300],'--r')
plt.plot([0,numChannels],[45,45],'--b')

plt.subplot(1,3,3)
plt.plot(np.diff(lfp_power))
plt.plot([0,numChannels],[-0.075,-0.075],'--k')

surface_chan = np.max(np.where(np.diff(lfp_power) < -0.075)[0])

mask_chans3 = np.concatenate(mask_chans2, low_power)

mask = np.ones((ch.shape))
mask = mask > 0
mask[mask_chans3] = False
scaling = np.ones((numChannels,))
channels = np.arange(0,numChannels)

offset = offsets.astype('int')

# %%

def write_probe_json(output_file, channels, offset, scaling, mask, surface_channel):

    with open(output_file, 'w') as outfile:
        json.dump( \
                  {  \
                        'channel' : channels.tolist(), \
                        'offset' : offset.tolist(), \
                        'scaling' : gain_factors.tolist(), \
                        'mask' : mask.tolist(), \
                        'surface_channel' : surface_chan
                   },
                 
                  outfile, \
                  indent = 4, separators = (',', ': ') \
                 ) 

# %%

def read_probe_json(input_file):
    
    with open(input_file) as data_file:
        data = json.load(data_file)
    
    full_mask = np.zeros((totalChans,totalChans))
    full_mask = full_mask > 1
    
    scaling = np.array(data['scaling'])
    mask = np.array(data['mask'])
    offset = np.array(data['offset'])
    surface_channel = data['surface_channel']

    period = 24
        
    for ch in range(0,totalChans):
        
        neighbors = np.arange(ch%period, maxChan, period).astype('int') # 1 neighbor is better than 2
        ok_chans = np.setdiff1d(neighbors, np.where(mask == False)[0])
        
        full_mask[ok_chans,ch] = True 

    return full_mask, offset, scaling, surface_channel

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

