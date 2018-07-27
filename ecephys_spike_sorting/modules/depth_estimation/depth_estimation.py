import glob    
import json
import os

import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import welch
from scipy.ndimage.filters import gaussian_filter1d

from ecephys_spike_sorting.common.utils import find_range, rms

def find_surface_channel(data, params, reference_channels, nchannels=384, sample_frequency=2500):
    
    smoothing_amount = params['smoothing_amount']
    power_thresh = params['power_thresh']
    diff_thresh = params['diff_thresh']
    freq_range = params['freq_range']
    channel_range = params['channel_range']
    nfft = params['nfft']
    n_passes = params['n_passes']

    save_figure = params['save_figure']
    if save_figure:
        figure_location = params['figure_location']
    
    candidates = np.zeros((n_passes,))
    
    for p in range(n_passes):
        
        startPt = int(sample_frequency*params['skip_s_per_pass']*p)
        endPt = startPt + int(sample_frequency)
    
        channels = np.arange(nchannels).astype('int')
        chunk = np.copy(data[startPt:endPt,channels])
        
        for channel in channels:
            chunk[:,channel] = chunk[:,channel] - np.median(chunk[:,channel])
            
        for channel in channels:
            chunk[:,channel] = chunk[:,channel] - np.median(chunk[:,channel_range[0]:channel_range[1]],1)
        
        power = np.zeros((int(nfft/2+1), channels.size))
    
        for channel in channels:
            sample_frequencies, Pxx_den = welch(chunk[:,channel], fs=sample_frequency, nfft=nfft)
            power[:,channel] = Pxx_den
        
        in_range = find_range(sample_frequencies, 0, params['max_freq'])
        
        mask_chans = reference_channels

        in_range_gamma = find_range(sample_frequencies, freq_range[0],freq_range[1])
        
        values = np.log10(np.mean(power[in_range_gamma,:],0))
        values[mask_chans] = values[mask_chans-1]
        values = gaussian_filter1d(values,smoothing_amount)
                        
        try:
           #print(np.where(np.diff(values) < diff_thresh))
           #print(np.where(values < power_thresh))
           surface_chan = np.max(np.where((np.diff(values) < diff_thresh) * (values[:-1] < power_thresh) )[0])
        except ValueError:
           surface_chan = ephys_params['num_channels']
            
        candidates[p] = surface_chan
        
        if save_figure:
            plot_results(chunk, power, in_range, values, nchannels, surface_chan, power_thresh, diff_thresh, figure_location)
      
    surface_channel = np.median(candidates)
    air_channel = np.min([surface_channel + params['air_gap'], nchannels])
        
    return surface_channel, air_channel


def plot_results(chunk, power, in_range, values, nchannels, surface_chan, power_thresh, diff_thresh, figure_location):

    plt.figure(figsize=(5,10))
    plt.subplot(4,1,1)
    plt.imshow(np.flipud((chunk).T), aspect='auto',vmin=-1000,vmax=1000)
    
    plt.subplot(4,1,2)
    plt.imshow(np.flipud(np.log10(power[in_range,:]).T), aspect='auto')
    
    plt.subplot(4,1,3)
    plt.plot(values) 
    plt.plot([0,nchannels],[power_thresh,power_thresh],'--k')

    plt.plot([surface_chan, surface_chan],[-2, 2],'--r')
    
    plt.subplot(4,1,4)
    plt.plot(np.diff(values))
    plt.plot([0,nchannels],[diff_thresh,diff_thresh],'--k')
    
    plt.plot([surface_chan, surface_chan],[-0.2, diff_thresh],'--r')
    plt.title(surface_chan)
    plt.savefig(os.path.join(figure_location, 'probe_depth.png'))


def compute_offset_and_surface_channel(ap_data, lfp_data, ephys_params, params):

    hi_noise_thresh = params['hi_noise_thresh']
    lo_noise_thresh = params['lo_noise_thresh']

    numChannels = ephys_params['num_channels']

    offsets = np.zeros((numChannels,), dtype = 'int16')
    rms_noise = np.zeros((numChannels,), dtype='int16')
    lfp_power = np.zeros((numChannels,), dtype = 'float32')

    # %%

    mask_chans = ephys_params['reference_channels']

    start_time = params['start_sample']
    recording_time = int(ephys_params['sample_rate'])
    median_subtr = np.zeros((recording_time,numChannels))

    # 1. cycle through to find median offset

    for ch in range(0,numChannels,1): #
        
        channel = ap_data[start_time:start_time+recording_time,ch]
        offsets[ch] = np.median(channel).astype('int16')
        median_subtr[:,ch] = channel - offsets[ch]
        rms_noise[ch] = rms(median_subtr[:,ch])*ephys_params['bit_volts']
        
    excluded_chans1 = np.where(rms_noise > hi_noise_thresh)[0]
    excluded_chans2 = np.where(rms_noise < lo_noise_thresh)[0]
        
    mask_chans2 = np.concatenate((mask_chans, excluded_chans1, excluded_chans2))

    surface, air = find_surface_channel(lfp_data, params, ephys_params['reference_channels'], ephys_params['num_channels'], ephys_params['lfp_sample_rate'])

    print("Surface channel: " + str(surface))

    channels = np.arange(0,numChannels)
    mask = np.ones((channels.shape), dtype=bool)
    mask[mask_chans2] = False
    scaling = np.ones((numChannels,))
    vertical_pos = 20*(np.floor(np.arange(0.384)/2)+1).astype('int')
    horizontal_pos = np.array([43,11,59,27]*96)

    output_dict = {}
    output_dict['channels'] = channels
    output_dict['mask'] = mask
    output_dict['scaling'] = scaling
    output_dict['offsets'] = offsets
    output_dict['surface_channel'] = surface
    output_dict['air_channel'] = air
    output_dict['vertical_pos'] = vertical_pos
    output_dict['horizontal_pos'] = horizontal_pos

    return output_dict