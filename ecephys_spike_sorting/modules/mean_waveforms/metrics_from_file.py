import numpy as np
import os
import glob

import xarray as xr
import pandas as pd

import warnings

from .waveform_metrics import calculate_waveform_metrics_from_avg
from ...common.epoch import Epoch
from ...common.utils import printProgressBar

def metrics_from_file(mean_waveform_fullpath,
                      snr_fullpath,
                      spike_times, 
                      spike_clusters, 
                      templates, 
                      channel_map, 
                      bit_volts, 
                      sample_rate, 
                      site_spacing, 
                      w_inv,
                      params):
                     
    
    """
    Load C_waves output and call waveform_metrics for each cluster
    Does not support epochs, since waveforms are already averaged
    
    Inputs:
    -------
    mean_wavefrom_fullpath: path to the mean waveforms npy file
    snr_fullpath: path to snr npy file
    spike_times : spike times (in samples)
    spike_clusters : cluster IDs for each spike time []
    clusterIDs : all unique cluster ids
    cluster_quality : 'noise' or 'good'
    sample_rate : Hz
    site_spacing : m

    Outputs:
    -------
    mean_waveforms : numpy array with dims :
     - 1 : clusterID
     - 2 : epochs
     - 3 : mean (0) or std (1)
     - 4 : channels
     - 5 : samples
    spike_count : numpy array with dims :
     - 1 : clusterID
     - 2 : epoch (last is entire dataset)
    dimCoords : list of coordinates for each dimension
    dimLabels : list of labels for each dimension
    metrics : DataFrame with waveform metrics

    Parameters:
    ----------
    samples_per_spike : number of samples in extracted spikes
    pre_samples : number of samples prior to peak
    num_epochs : number of epochs to calculate mean waveforms
    spikes_per_epoch : max number of spikes to generate average for epoch

    """

    # #############################################

    samples_per_spike = params['samples_per_spike']
    pre_samples = params['pre_samples']
    spikes_per_epoch = params['spikes_per_epoch']
    upsampling_factor = params['upsampling_factor']
    spread_threshold = params['spread_threshold']
    site_range = params['site_range']

    # #############################################

    metrics = pd.DataFrame()

    cluster_ids = np.arange(np.max(spike_clusters) + 1)
    total_units = len(cluster_ids)
    
    mean_waveforms = np.load(mean_waveform_fullpath)
    snr_array = np.load(snr_fullpath)

    channel_map = np.squeeze(channel_map)
    
    nTemplate = templates.shape[0]
    
    # initialize peak_channels array
    peak_channels = np.zeros([nTemplate,],'uint32')
    # for each template (nt x nchan), multiply the the transpose (nchan x nt) by inverse of 
    # the whitening matrix (nchan x nchan); get max and min along tthe time axis (1)
    # to find the peak channel
    for i in np.arange(0,nTemplate):
        currT = templates[i,:].T
        curr_unwh = np.matmul(w_inv, currT)
        currdiff = np.max(curr_unwh,1) - np.min(curr_unwh,1)
        peak_channels[i] = channel_map[np.argmax(currdiff)]
    
    for cluster_idx, cluster_id in enumerate(cluster_ids):

        printProgressBar(cluster_idx+1, total_units)

        snr = snr_array[cluster_idx,0]
        nSpike = snr_array[cluster_idx,1]
        # if at least one spike, calculate metrics and concatenate to existing dataframe
        if nSpike > 0:
            metrics = pd.concat([metrics, calculate_waveform_metrics_from_avg(mean_waveforms[cluster_idx,:],
                                                                     snr,
                                                                     cluster_id, 
                                                                     peak_channels[cluster_idx], 
                                                                     channel_map,
                                                                     sample_rate, 
                                                                     upsampling_factor,
                                                                     spread_threshold,
                                                                     site_range,
                                                                     site_spacing,                                                                     
                                                                     )])



    return metrics


def generateDimLabels(good_clusters, num_epochs, pre_samples, total_samples, num_channels, sample_rate):
    """ Generate dimension labels and coordinates for the xarray """

    dimCoords = []
    dimLabels = []

    dimCoords.append(good_clusters)
    dimLabels.append('clusterID')

    dim1Coords = [str(i) for i in range(0, num_epochs)]
    dim1Coords.append('all')
    dimCoords.append(dim1Coords)
    dimLabels.append('epoch')

    dimCoords.append(['mean', 'std'])
    dimLabels.append('mean or std')

    dimCoords.append(range(0, num_channels))
    dimLabels.append('channel')

    dimCoords.append(np.linspace(-pre_samples, total_samples -
                                 pre_samples, total_samples) / sample_rate)
    dimLabels.append('time')

    return dimCoords, dimLabels


def writeDataAsXarray(mean_waveforms, spike_count, dimCoords, dimLabels, output_file):
    """ Saves mean waveforms as xarray """

    waveform_array = xr.DataArray(mean_waveforms,
                                  coords=dimCoords,
                                  dims=dimLabels)

    spike_count_array = xr.DataArray(spike_count,
                                     coords=dimCoords[:2],
                                     dims=dimLabels[:2])

    ds = xr.Dataset({'waveforms': waveform_array,
                     'spike_count': spike_count_array})

    ds.to_netcdf(output_file)


def writeDataAsNpy(waveforms, output_file):
    """ Saves mean waveforms as xarray """

    mean_waveforms = waveforms[:, -1, 0, :, :]  # extract overall mean

    np.save(output_file, mean_waveforms)
