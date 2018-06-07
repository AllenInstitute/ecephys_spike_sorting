#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 14:51:18 2017

@author: joshs
"""

import glob    
import json
import os
from scipy.optimize import minimize
from scipy import signal
from scipy.ndimage.filters import gaussian_filter1d
import numpy as np
import matplotlib.pyplot as plt

dataFolder = r'E:\\704514354_380485_20180601_probeF_sorted\\'

f1 = dataFolder + os.path.join('continuous','Neuropix*.0')
f2 = dataFolder + os.path.join('continuous','Neuropix*.1')


ap_directory = glob.glob(f1)[0]
lfp_directory = glob.glob(f2)[0]

print(ap_directory)
print(lfp_directory)

hi_noise_thresh = 26
lo_noise_thresh = 3
lfp_noise_thresh = -1.0
surface_ch_thresh = -0.05

# %%



def rms(data):
    return np.power(np.mean(np.power(data,2)),0.5)

def func(x, channel, M):
    
    corrected = channel - M * x
    error = rms(corrected)
    
    return error


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


# %%
  
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

start_time = 30000*20
recording_time = 90000
median_subtr = np.zeros((recording_time,numChannels))

offsets = np.zeros((numChannels,))

# 1. cycle through to find median offset
plt.figure(200)
plt.clf()

for ch in range(0,numChannels,1): #
    
    channel = dataAp[start_time:start_time+recording_time,ch].astype('float32')
    #a
    offsets[ch] = np.nanmedian(channel).astype('int16')

    median_subtr[:,ch] = channel - offsets[ch]
    if ch % 10 == 0:
        plt.plot(median_subtr[:,ch] + ch*10,linewidth=0.5)

    f,Pxx = signal.welch(median_subtr[:2500,ch],fs=30000,nfft=2048)
    
    rms_noise[ch] = rms(median_subtr[:,ch]).astype('int16')
    lfp_power[ch] = np.log10(Pxx[7])
    
plt.show()
    
# %%
    
excluded_chans1 = np.where(rms_noise > hi_noise_thresh)[0]
excluded_chans2 = np.where(rms_noise < lo_noise_thresh)[0]
    
mask_chans2 = np.concatenate((mask_chans, excluded_chans1, excluded_chans2))


# %%

rawDataLfp = np.memmap(lfp_file, dtype='int16', mode='r')
dataLfp = np.reshape(rawDataLfp, (int(rawDataLfp.size/numChannels), numChannels))

mask_chans = np.array([37, 76, 113, 152, 189, 228, 265, 304, 341, 380]) - 1

start_time = 2500*20
recording_time = 2500*3
median_subtr = np.zeros((recording_time,numChannels))

# 1. cycle through to find median 
plt.figure(199)
plt.clf()

for ch in range(0,numChannels,1): #
    
    channel = dataLfp[start_time:start_time+recording_time,ch].astype('float32')
    #a
    offset = np.nanmedian(channel)

    median_subtr = channel - offset
    if ch % 10 == 0:
        plt.plot(median_subtr + ch*10,linewidth=0.5)
    
    f,Pxx = signal.welch(median_subtr,fs=2500,nfft=2048)
    lfp_power[ch] = np.log10(np.mean(Pxx[80]))

plt.show()

lfp_power[mask_chans2] = lfp_power[mask_chans2-1]    
lfp_power = signal.detrend(lfp_power)
low_power = np.where(lfp_power < lfp_noise_thresh)[0]
lfp_power[low_power] = lfp_power[low_power-1]
#lfp_power = gaussian_filter1d(lfp_power,5)

plt.figure(191211)
plt.clf()
    
plt.subplot(1,3,1)
plt.plot(offsets)

plt.subplot(1,3,2)
plt.plot(rms_noise)

plt.plot([0,numChannels],[hi_noise_thresh,hi_noise_thresh],'--r')
plt.plot([0,numChannels],[lo_noise_thresh,lo_noise_thresh],'--b')

plt.subplot(1,3,3)
plt.plot(lfp_power)
plt.plot([0,numChannels],[surface_ch_thresh,surface_ch_thresh],'--k')

plt.show()

if False:
    surface_chan = np.max(np.where(np.diff(lfp_power) < surface_ch_thresh)[0])

    print(surface_chan)

    channels = np.arange(0,numChannels)
    mask = np.ones((channels.shape))
    mask = mask > 0
    mask[mask_chans3] = False
    scaling = np.ones((numChannels,))

    offset = offsets.astype('int')

    # %%

