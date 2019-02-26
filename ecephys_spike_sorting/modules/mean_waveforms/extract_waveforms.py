import numpy as np
import os
import glob

import xarray as xr

import warnings

from .waveform_metrics import calculate_waveform_metrics

def extract_waveforms(raw_data, spike_times, spike_clusters, bit_volts, sample_rate, params, epochs=None):
    
    """Calculate mean waveforms for sorted units.

    Inputs:
    -------
    raw_data : continuous data as numpy array (samples x channels)
    spike_times : spike times (in samples)
    spike_clusters : cluster IDs for each spike time []
    clusterIDs : all unique cluster ids
    cluster_quality : 'noise' or 'good'
    sample_rate : Hz

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
    num_epochs = params['num_epochs']
    spikes_per_epoch = params['spikes_per_epoch']
    
    # #############################################

    metrics = pd.DataFrame()

    if epochs is None:
        epochs = [Epoch('complete_session', 0, np.inf)]
        epochs[0].convert_to_index(np.zeros((raw_data.shape[0],)))

    cluster_ids = np.unique(spike_clusters)
    total_units = len(cluster_ids)
    total_epochs = len(epochs)

    mean_waveforms = np.zeros((total_units, total_epochs, 2, raw_data.shape[1], samples_per_spike))
    spike_count = np.zeros((total_units, total_epochs + 1))

    for epoch_idx, epoch in enumerate(epochs):

        in_epoch = (spike_times > epoch.start_index) * (spike_times < epoch.start_index)
        spike_times_in_epoch = spike_times[in_epoch]

        for cluster_idx, cluster_id in enumerate(cluster_ids):

            print(cluster_id)

            in_cluster = (spike_clusters[in_epoch] == cluster_id)
            times_for_cluster = spike_times_in_epoch[in_cluster]

            waveforms = np.empty((spikes_per_epoch, raw_data.shape[1], samples_per_spike))
            waveforms[:] = np.nan

            np.random.shuffle(times_for_cluster)

            total_waveforms = np.min([times_for_cluster.size, spikes_per_epoch])
                
            for wv_idx, peak_time in enumerate(times_for_cluster[:total_waveforms]):
                start = int(peak_time-pre_samples)
                end = start + samples_per_spike
                rawWaveform = raw_data[start:end,:].T
                
                if rawWaveform.shape[1] == samples_per_spike: # in case spike was at start or end of dataset
                    waveforms[wv_idx, :, :] = rawWaveform * bit_volts

            # concatenate to existing dataframe
            metrics = pd.concat([metrics, calculate_waveform_metrics(waveforms[:total_waveforms,:,:], cluster_id, epoch.name)])

            with warnings.catch_warnings():
                
                warnings.simplefilter("ignore", category=RuntimeWarning)
                mean_waveforms[cluster_idx, epoch_idx, 0, :, :] = np.nanmean(waveforms, 0)
                mean_waveforms[cluster_idx, epoch_idx, 1, :, :] = np.nanstd(waveforms, 0)

                # remove offset
                for channel in range(0, mean_waveforms.shape[3]):
                    mean_waveforms[cluster_idx, epoch, 0, channel, :] = \
                    mean_waveforms[cluster_idx, epoch, 0, channel, :] - mean_waveforms[cluster_idx, epoch, 0, channel, 0]
                
            spike_count[cluster_idx, epoch_idx] = total_waveforms


    dimCoords, dimLabels = generateDimLabels(cluster_ids, total_epochs, pre_samples, samples_per_spike, raw_data.shape[1], sample_rate)

    return mean_waveforms, spike_count, dimCoords, dimLabels, metrics



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

    dimCoords.append(range(0,num_channels))
    dimLabels.append('channel')

    dimCoords.append(np.linspace(-pre_samples, total_samples-pre_samples, total_samples) / sample_rate)
    dimLabels.append('time')

    return dimCoords, dimLabels



def writeDataAsXarray(mean_waveforms, spike_count, dimCoords, dimLabels, output_file):

    """ Saves mean waveforms as xarray """

    waveform_array = xr.DataArray(mean_waveforms, \
        coords=dimCoords, \
        dims=dimLabels)

    spike_count_array = xr.DataArray(spike_count, \
        coords=dimCoords[:2], \
        dims=dimLabels[:2])

    ds = xr.Dataset({'waveforms' : waveform_array, 'spike_count' : spike_count_array})

    ds.to_netcdf(output_file)


def writeDataAsNpy(waveforms, output_file):

    """ Saves mean waveforms as xarray """

    mean_waveforms = waveforms[:,-1,0,:,:] # extract overall mean

    np.save(output_file, mean_waveforms)
    
    

