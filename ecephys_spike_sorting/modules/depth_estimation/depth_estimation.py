import glob    
import json
import os

import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import welch
from scipy.ndimage.filters import gaussian_filter1d

from ...common.utils import find_range, rms, printProgressBar
from ...common.OEFileInfo import get_lfp_channel_order

def compute_channel_offsets(ap_data, ephys_params, params):

    """
    Computes DC offset for AP band data

    Also identifies channels with very high or low rms noise.

    Inputs:
    ------
    ap_data : numpy.ndarray (N samples x M channels)
    ephys_params : dict
    params : dict

    Outputs:
    -------
    output_dict : dict
        - channels : array of channel numbers
        - mask : True if channel is good, False otherwise
        - scaling : array of ones (not computed)
        - offsets : array of DC offset values
        - vertical_pos : distance of each channel from the probe tip
        - horizontal_pos : distance of each channel from the probe edge

    """

    numChannels = ephys_params['num_channels']
    numIterations = params['n_passes']

    

    

    def iterate_depth_info(numIterations):
        try:
            offsets = np.zeros((numChannels, numIterations), dtype = 'int16')
            rms_noise = np.zeros((numChannels, numIterations), dtype='float')
            for i in range(numIterations):
                start_sample = int((params['start_time'] + params['skip_s_per_pass'] * i)* ephys_params['sample_rate'])
                end_sample = start_sample + int(params['time_interval'] * ephys_params['sample_rate'])

                for ch in range(numChannels):
                    try:
                            printProgressBar(i * numChannels + ch +1, numChannels * numIterations)
                    except Exception as E:
                        pass
                    data = ap_data[start_sample:end_sample, ch]
                    offsets[ch,i] = np.nanmedian(data).astype('int')
                    median_subtr = data - offsets[ch,i]
                    rms_noise[ch,i] = rms(median_subtr) * ephys_params['bit_volts']
        except Exception as E:
            numIterations = numIterations - 1
            if numIterations >0:
                rms_noise, offsets = iterate_depth_info(numIterations)
            else:
                print('Unable to estimate offsets or RMS noise. Returning empty arrays')
        return rms_noise, offsets
        

    rms_noise, offsets = iterate_depth_info(numIterations)
    print(offsets)

    mask = np.ones((numChannels,), dtype=bool)
    mask[ephys_params['reference_channels']] = False
    mask[np.median(rms_noise,1) > params['hi_noise_thresh']] = False
    mask[np.median(rms_noise,1) < params['lo_noise_thresh']] = False

    output_dict = {
        'channels' : np.arange(numChannels),
        'mask' : mask,
        'scaling' : np.ones((numChannels,)),
        'offsets' : np.median(offsets,1).astype('int16'),
        'vertical_pos' : 20*(np.floor(np.arange(0,numChannels)/2)+1).astype('int'),
        'horizontal_pos' : np.array([43,11,59,27] * int(numChannels / 4))

    }

    return output_dict



def find_surface_channel(lfp_data, ephys_params, params):

    """
    Computes surface channel from LFP band data

    Inputs:
    ------
    lfp_data : numpy.ndarray (N samples x M channels)
    ephys_params : dict
    params : dict

    Outputs:
    -------
    output_dict : dict
        - surface_channel : channel at brain surface
        - air_channel : channel at agar / air surface (approximate)
        
    """
    print('using this script')
    nchannels = ephys_params['num_channels']
    sample_frequency = ephys_params['lfp_sample_rate']

    smoothing_amount = params['smoothing_amount']
    power_thresh = params['power_thresh']
    diff_thresh = params['diff_thresh']
    freq_range = params['freq_range']
    channel_range = params['channel_range']
    nfft = params['nfft']
    n_passes = params['n_passes']

    save_figure = params['save_figure']


    def iterate_surface_chan(n_passes):
        candidates = np.zeros((n_passes,))
        try:
            for p in range(n_passes):
                
                startPt = int(sample_frequency*params['skip_s_per_pass']*p)
                endPt = startPt + int(sample_frequency)
            
                if ephys_params['reorder_lfp_channels']:
                    channels = get_lfp_channel_order()
                else:
                    channels = np.arange(nchannels).astype('int')

                chunk = np.copy(lfp_data[startPt:endPt,channels])
                
                for ch in np.arange(nchannels):
                    chunk[:,ch] = chunk[:,ch] - np.median(chunk[:,ch])
                    
                for ch in np.arange(nchannels):
                    chunk[:,ch] = chunk[:,ch] - np.median(chunk[:,channel_range[0]:channel_range[1]],1)
                
                power = np.zeros((int(nfft/2+1), nchannels))
            
                for ch in np.arange(nchannels):
                    try:
                        printProgressBar(p * nchannels + ch + 1, nchannels * n_passes)
                    except Exception as E:
                        pass
                    sample_frequencies, Pxx_den = welch(chunk[:,ch], fs=sample_frequency, nfft=nfft)
                    power[:,ch] = Pxx_den
                
                in_range = find_range(sample_frequencies, 0, params['max_freq'])
                
                mask_chans = ephys_params['reference_channels']

                in_range_gamma = find_range(sample_frequencies, freq_range[0],freq_range[1])
                
                values = np.log10(np.mean(power[in_range_gamma,:],0))
                values[mask_chans] = values[mask_chans-1]
                values = gaussian_filter1d(values,smoothing_amount)

                surface_channels = np.where((np.diff(values) < diff_thresh) * (values[:-1] < power_thresh) )[0]

                if len(surface_channels > 0):
                    candidates[p] = np.max(surface_channels)
                else:
                    candidates[p] = nchannels
        except Exception as E:
            n_passes = n_passes - 1
            if n_passes >0:
                candidates, chunk, power, in_range, values = iterate_surface_chan(n_passes)
            else:
                print('Unable to estimate surface channel. Returning empty arrays')
        return candidates, chunk, power, in_range, values

    candidates, chunk, power, in_range, values = iterate_surface_chan(n_passes)
    surface_channel = np.median(candidates)
    air_channel = np.min([surface_channel + params['air_gap'], nchannels])

    output_dict = {
        'surface_channel' : surface_channel,
        'air_channel' : air_channel
    }

    if save_figure:
        plot_results(chunk, 
                     power, 
                     in_range, 
                     values, 
                     nchannels, 
                     surface_channel, 
                     power_thresh, 
                     diff_thresh, 
                     params['figure_location'])

    return output_dict



def plot_results(chunk, 
                 power, 
                 in_range, 
                 values, 
                 nchannels, 
                 surface_chan, 
                 power_thresh, 
                 diff_thresh, 
                 figure_location):

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
    plt.savefig(figure_location)