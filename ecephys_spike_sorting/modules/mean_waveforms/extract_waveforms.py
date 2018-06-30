import numpy as np
import os
import glob

import xarray as xr

def extract_waveforms(raw_data, spike_times, spike_clusters, clusterIDs, cluster_quality, sample_rate, output_file, params):
    
    """Calculate mean waveforms for sorted units.

    Inputs:
    -------
    raw_data : continuous data as numpy array (samples x channels)
    spike_times : spike times (in samples)
    spike_clusters : cluster IDs for each spike time []
    clusterIDs : all unique cluster ids
    cluster_quality : 'noise' or 'good'
    sample_rate : Hz
    output_file : path to output file

    Outputs:
    -------
    mean_waveforms : xarray (in NetCDF format) with dims :
     - 1 : clusterID
     - 2 : epoch (last is entire dataset)
     - 3 : mean (0) or std (1)
     - 4 : channels
     - 5 : samples

    Parameters:
    ----------
    samples_per_spike : number of samples in extracted spikes
    pre_samples : number of samples prior to peak
    num_epochs : number of epochs to calculate mean waveforms
    spikes_per_epoch : max number of spikes to generate average for epoch

    """

    waveformsFile = os.path.join(kilosort_path, 'mean_waveforms.npy')
    SNRFile = os.path.join(kilosort_path, 'SNR.npy')

    samples_per_spike = params['samples_per_spike']
    pre_samples = params['pre_samples']
    num_epochs = params['num_epochs']
    spikes_per_epoch = params['spikes_per_epoch']

    good_clusters = clusterIDs[cluster_quality == 'good']

    mean_waveforms = np.zeros((good_clusters.size, num_epochs + 1, 2, raw_data.shape[1], samples_per_spike))

    epoch_start_times = np.linspace(np.min(spike_times), np.max(spike_times), num_epochs + 1)

    for cluster_idx, clusterID in enumerate(good_clusters):

        in_cluster = (clusters == clusterID)
        times_for_cluster = spike_times[in_cluster]

        waveforms = np.empty((spikes_per_epoch * num_epochs, raw_data.shape[1], samples_per_spike))
        waveforms[:] = np.nan

        for epoch, start_time in epoch_start_times[:-1]:

            end_time = epoch_start_times[epoch+1]
            times_for_epoch = times_for_cluster[(times_for_cluster > start_time) * (times_for_cluster < start_time)]

            rand_times = np.shuffle(times_for_epoch)

            total_waveforms = np.min([rand_times.size, spikes_per_epoch])

            for wv_idx, peak_time in rand_times[:total_waveforms]:
                rawWaveform = raw_data[int(peak_time-preSamples):int(peak_time+samplesPerSpike-preSamples),:].T
                waveforms[wv_idx + epoch * spikes_per_epoch, :, :] = rawWaveform

            start = epoch*spikes_per_epoch
            end = start + spikes_per_epoch
            mean_waveforms[cluster_idx, epoch, 0, :, :] = np.nanmean(waveforms[start:end, :,:], 0)
            mean_waveforms[cluster_idx, epoch, 1, :, :] = np.nanstd(waveforms[start:end, :, :], 0)

        mean_waveforms[cluster_idx, num_epochs, 0, :, :] = np.nanmean(waveforms, 0)
        mean_waveforms[cluster_idx, num_epochs, 1, :, :] = np.nanstd(waveforms, 0)

    dimCoords, dimLabels = generateDimLabels(good_clusters, num_epochs, pre_samples, samples_per_spike, raw_data.shape[1], sample_rate)

    writeDataAsXarray(mean_waveforms, dimCoords, dimLabels, output_file)


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

    dimCoords.append(np.linspace(-pre_samples, total_samples-pre_samples) / sample_rate)
    dimLabels.append('time')

    return dimCoords, dimLabels



def writeDataAsXarray(mean_waveforms, dimCoords, dimLabels, output_file):

    """ Saves mean waveform as xarray """

    waveform_array = xr.DataArray(mean_waveforms, \
        coords=dimCoords, \
        dims=dimLabels)

    waveform_array.to_netcdf(output_file)
    

