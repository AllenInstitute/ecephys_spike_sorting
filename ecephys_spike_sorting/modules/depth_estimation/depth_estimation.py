import glob    
import json
import os

import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import welch
from scipy.ndimage.filters import gaussian_filter1d

from ...common.utils import find_range, rms, printProgressBar
from ...common.OEFileInfo import get_lfp_channel_order
from ...common.SGLXMetaToCoords import MetaToCoords

def compute_channel_offsets(ap_data, ephys_params, params, xCoord, yCoord):

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

    offsets = np.zeros((numChannels, numIterations), dtype = 'int16')
    rms_noise = np.zeros((numChannels, numIterations), dtype='float')

    for i in range(numIterations):

        start_sample = int((params['start_time'] + params['skip_s_per_pass'] * i)* ephys_params['sample_rate'])
        end_sample = start_sample + int(params['time_interval'] * ephys_params['sample_rate'])

        for ch in range(numChannels):

            printProgressBar(i * numChannels + ch +1, numChannels * numIterations)

            data = ap_data[start_sample:end_sample, ch]
            offsets[ch,i] = np.median(data)
            median_subtr = data - offsets[ch,i]
            rms_noise[ch,i] = rms(median_subtr) * ephys_params['bit_volts']
        
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



def find_surface_channel(lfp_data, ephys_params, params, xCoord, yCoord, shankInd):

    """
    Computes surface channel from LFP band data
    Updated to use the site positions and estimate surface y (from tip) for shank 0

    Inputs:
    ------
    lfp_data : numpy.ndarray (N samples x M channels)
    ephys_params : dict
    params : dict

    Outputs:
    -------
    output_dict : dict
        - surface_y : channel at brain surface
        - air_y : channel at agar / air surface (approximate)
        
    """
    
    nchannels = ephys_params['num_channels']
    sample_frequency = ephys_params['lfp_sample_rate']
    
    lfp_samples, lfp_channels = lfp_data.shape
    

    smoothing_amount = params['smoothing_amount']
    power_thresh = params['power_thresh']
    diff_thresh = params['diff_thresh']
    freq_range = params['freq_range']
    saline_range = params['saline_range_um']
    nfft = params['nfft']
    n_passes = params['n_passes']

    save_figure = params['save_figure']

    candidates = np.zeros((n_passes,))
    
    samples_per_pass = int(sample_frequency*(params['skip_s_per_pass'] + 1))
    max_passes = int(np.floor(lfp_samples/samples_per_pass))
    passes_used = min(n_passes, max_passes)

    # use channels only on shank0, to yield a single estimate for the surace z
    channels = np.squeeze(np.asarray(np.where(shankInd == 0)))
    # remove reference channels
    channels = np.delete(channels, ephys_params['reference_channels'])
    nchannels_used = channels.size
    
    chan_y = np.squeeze(yCoord[channels])
    in_saline_range = np.squeeze((chan_y > saline_range[0]) & (chan_y < saline_range[1]))
    saline_chan = np.where(in_saline_range)
    
    max_y = np.max(chan_y)
    
    
    for p in range(passes_used):
        
        startPt = int(sample_frequency*params['skip_s_per_pass']*p)
        endPt = startPt + int(sample_frequency)
    
        chunk = np.copy(lfp_data[startPt:endPt,channels])
#        print('chunk shape: ')
#        print(chunk.shape)
        
        # subtract dc offset for all channels
        for ch in np.arange(nchannels_used):
            chunk[:,ch] = chunk[:,ch] - np.median(chunk[:,ch])
        
        # reduce noise by correcting each timepoint with the signal in saline
        for ch in np.arange(nchannels_used):
            saline_chunk = np.squeeze(chunk[:,saline_chan])
            saline_median = np.median(saline_chunk,1)
            chunk[:,ch] = chunk[:,ch] - saline_median
        
        power = np.zeros((int(nfft/2+1), nchannels_used))
    
        for ch in np.arange(nchannels_used):

            printProgressBar(p * nchannels_used + ch + 1, nchannels_used * n_passes)

            sample_frequencies, Pxx_den = welch(chunk[:,ch], fs=sample_frequency, nfft=nfft)
            power[:,ch] = Pxx_den
        
        in_range = find_range(sample_frequencies, 0, params['max_freq'])
        
        in_range_gamma = find_range(sample_frequencies, freq_range[0],freq_range[1])
        
        values = np.log10(np.mean(power[in_range_gamma,:],0))

        values = gaussian_filter1d(values,smoothing_amount)

        surface_channels = np.where((np.diff(values) < diff_thresh) * (values[:-1] < power_thresh) )[0]
        surface_y = chan_y[surface_channels]

        if len(surface_y > 0):
            candidates[p] = np.max(surface_y)
        else:
            candidates[p] = max_y
      
    surface_y = np.median(candidates)
    air_y = np.min([surface_y + params['air_gap_um'], max_y])

    output_dict = {
        'surface_y' : surface_y,
        'air_y' : air_y
    }

    if save_figure:
        plot_results(chunk, 
                     power, 
                     in_range, 
                     values, 
                     nchannels_used,
                     chan_y,
                     surface_y, 
                     power_thresh, 
                     diff_thresh, 
                     params['figure_location'])

    return output_dict



def plot_results(chunk, 
                 power, 
                 in_range, 
                 values, 
                 nchannels,
                 chan_y,
                 surface_y, 
                 power_thresh, 
                 diff_thresh, 
                 figure_location):

    plt.figure(figsize=(5,10))
    plt.subplot(4,1,1)
    # plt.imshow(np.flipud((chunk).T), aspect='auto',vmin=-1000,vmax=1000)
    # sort chanks by y position
    chunk_order = np.argsort(chan_y)
    chunk[:,:] = chunk[:,chunk_order]
    plt.imshow((chunk).T, aspect='auto',vmin=-1000,vmax=1000)

    plt.subplot(4,1,2)
    # plt.imshow(np.flipud(np.log10(power[in_range,:]).T), aspect='auto')
    power[:,:] = power[:,chunk_order]
    plt.imshow(np.log10(power[in_range,:]).T, aspect='auto')

    y_sorted = chan_y[chunk_order]
    plt.subplot(4,1,3)
    plt.plot(y_sorted, values[chunk_order]) 
    plt.plot([chan_y[0],chan_y[nchannels-1]],[power_thresh,power_thresh],'--k')
    
    surface_index = np.min(np.where(y_sorted > surface_y))
    plt.plot([surface_index, surface_index],[-2, 2],'--r')
    
    plt.subplot(4,1,4)
    plt.plot(y_sorted[0:nchannels-1], np.diff(values[chunk_order]))
    plt.plot([chan_y[0],chan_y[nchannels-2]],[diff_thresh,diff_thresh],'--k')
    
    plt.plot([surface_y, surface_y],[-0.2, diff_thresh],'--r')
    plt.title(surface_y)
    plt.savefig(figure_location)