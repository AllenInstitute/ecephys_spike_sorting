import numpy as np
import os
import glob

import xarray as xr

import warnings

def extract_waveforms(raw_data, spike_times, spike_clusters, clusterIDs, cluster_quality, bit_volts, sample_rate, params):
    
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
     - 2 : epoch (last is entire dataset)
     - 3 : mean (0) or std (1)
     - 4 : channels
     - 5 : samples
    spike_count : numpy array with dims :
     - 1 : clusterID
     - 2 : epoch (last is entire dataset)
    dimCoords : list of coordinates for each dimension
    dimLabels : list of labels for each dimension

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

    good_clusters = clusterIDs

    mean_waveforms = np.zeros((good_clusters.size, num_epochs + 1, 2, raw_data.shape[1], samples_per_spike))
    spike_count = np.zeros((good_clusters.size, num_epochs + 1))

    epoch_start_times = np.linspace(np.min(spike_times), np.max(spike_times), num_epochs + 1)

    for cluster_idx, clusterID in enumerate(good_clusters):

        #print(clusterID)

        in_cluster = (spike_clusters == clusterID)
        times_for_cluster = spike_times[in_cluster]

        waveforms = np.empty((spikes_per_epoch * num_epochs, raw_data.shape[1], samples_per_spike))
        waveforms[:] = np.nan

        for epoch, start_time in enumerate(epoch_start_times[:-1]):

            end_time = epoch_start_times[epoch+1]
            times_for_epoch = times_for_cluster[(times_for_cluster > start_time) * (times_for_cluster <= end_time)]

            np.random.shuffle(times_for_epoch)

            total_waveforms = np.min([times_for_epoch.size, spikes_per_epoch])
            
            if total_waveforms > 1: # iterate over spike timess

                for wv_idx, peak_time in enumerate(times_for_epoch[:total_waveforms]):
                    start = int(peak_time-pre_samples)
                    end = start + samples_per_spike
                    rawWaveform = raw_data[start:end,:].T
                    
                    if rawWaveform.shape[1] == samples_per_spike: # in case spike was at start or end of dataset
                        waveforms[wv_idx + epoch * spikes_per_epoch, :, :] = rawWaveform * bit_volts
                    
            elif total_waveforms == 1: # don't iterate

                start = int(times_for_epoch[0] - pre_samples)
                end = start + samples_per_spike
                rawWaveform = raw_data[start:end,:].T
                if rawWaveform.shape[1] == samples_per_spike: # in case spike was at start or end of dataset
                    waveforms[epoch * spikes_per_epoch, :, :] = rawWaveform * bit_volts
            else:
                pass # leave as nan if there are no spikes

            start = epoch * spikes_per_epoch
            end = start + spikes_per_epoch

            assert(end <= spikes_per_epoch * num_epochs)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                mean_waveforms[cluster_idx, epoch, 0, :, :] = np.nanmean(waveforms[start:end, :,:], 0)
                mean_waveforms[cluster_idx, epoch, 1, :, :] = np.nanstd(waveforms[start:end, :, :], 0)
                
            spike_count[cluster_idx, epoch] = total_waveforms

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            mean_waveforms[cluster_idx, num_epochs, 0, :, :] = np.nanmean(waveforms, 0)
            mean_waveforms[cluster_idx, num_epochs, 1, :, :] = np.nanstd(waveforms, 0)
            
        spike_count[cluster_idx, num_epochs] = np.sum(spike_count[cluster_idx, :])

    dimCoords, dimLabels = generateDimLabels(good_clusters, num_epochs, pre_samples, samples_per_spike, raw_data.shape[1], sample_rate)

    return mean_waveforms, spike_count, dimCoords, dimLabels



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
    

