import numpy as np 
import matplotlib.pyplot as plt 
from scipy.signal import butter, filtfilt

from .utils import (get_spike_depths, 
                    get_spike_amplitudes,
                    load_kilosort_data)


def plotKsTemplates(ks_directory, raw_data_file, sample_rate = 30000, bit_volts = 0.195, time_range = [10, 11], exclude_noise=True, fig=None, output_path=None):

    """
    Compares the template times and locations to the raw data

    Inputs:
    ------
    ks_directory : str
        Path to Kilosort outputs
    raw_data_file : str
        Path to raw .dat or .bin file
    sample_rate : float
        Sample rate of original data (Hz)
    bit_volts : float
        Conversion factor for raw data to microvolts
    time_range : [float, float]
        Min/max of time range for plot
    exclude_noise : bool
        True if noise units should be ignored, False otherwise
    fig : matplotlib.pyplot.figure
        Figure handle to use for plotting
    output_path : str
        Path for saving the image

    Outputs:
    --------
    Saves image to output_path (optional)

    """

    spike_times, spike_clusters, spike_templates, amplitudes, templates, channel_map, clusterIDs, cluster_quality, pc_features, pc_feature_ind = \
                load_kilosort_data(ks_directory, 
                    sample_rate, 
                    convert_to_seconds = False,
                    use_master_clock = False,
                    include_pcs = True)

    raw_data = np.memmap(raw_data_file, dtype='int16')
    data = np.reshape(raw_data, (int(raw_data.size / 384), 384))

    if fig is None:
        fig = plt.figure(figsize=(16,10))

    start_index = time_range[0] * sample_rate
    end_index = time_range[1] * sample_rate

    b, a = butter(3, [300/(sample_rate/2), 2000/(sample_rate/2)], btype='band')

    D = data[start_index:end_index, np.squeeze(channel_map)] * bit_volts

    print(D.shape)

    for i in range(D.shape[1]):
        D[:,i] = filtfilt(b, a, D[:,i])

    D = D / np.max(np.abs(D))

    ax = plt.subplot(211)

    ax.imshow(D[:,1::2].T,
               vmin=-0.25,
               vmax=0.25,
               aspect='auto',
               origin='lower',
               cmap='RdGy')

    ax.axis('off')

    if exclude_noise:
        good_units = clusterIDs[cluster_quality != 'noise']
    else:
        good_units = clusterIDs

    spikes_in_time_range = np.where((spike_times > start_index) * (spike_times < end_index))[0]
    spikes_from_good_units = np.where(np.in1d(spike_templates, good_units))[0]
    spikes_to_use = np.intersect1d(spikes_in_time_range, spikes_from_good_units)

    times_in_range = spike_times[spikes_to_use]
    ids_in_range = spike_templates[spikes_to_use]
    amps_in_range = amplitudes[spikes_to_use]

    Z = np.zeros(D.shape)

    for idx, time in enumerate(times_in_range - start_index):
        if (time < Z.shape[0] - 42 and time > 40):
            template = np.squeeze(templates[ids_in_range[idx],:,:])
            Z[int(time-40):int(time-40+61),:] += template * amps_in_range[idx]
        
    ax = plt.subplot(212)

    ax.imshow(Z[:,1::2].T,
               vmin=-400,
               vmax=400,
               aspect='auto',
               origin='lower',
               cmap='RdGy')

    ax.axis('off')

    if output_path is not None:
        plt.savefig(output_path)


def plotDriftmap(ks_directory, sample_rate = 30000, time_range = [0, np.inf], exclude_noise=True, subselection = 50, fig=None, output_path=None):

    """
    Plots a "driftmap" of spike depths over time.

    This is a useful way to assess overall data quality for an experiment, as it makes probe
    motion very easy to see.

    This implementation is based on Matlab code from github.com/cortex-lab/spikes

    Inputs:
    ------
    ks_directory : str
        Path to Kilosort outputs
    sample_rate : float
        Sample rate of original data (Hz)
    time_range : [float, float]
        Min/max of time range for plot
    exclude_noise : bool
        True if noise units should be ignored, False otherwise
    subselection : int
        Number of spikes to skip (helpful for large datasets)
    fig : matplotlib.pyplot.figure
        Figure handle to use for plotting
    output_path : str
        Path for saving the image

    Outputs:
    --------
    Saves image to output_path (optional)

    """

    spike_times, spike_clusters, spike_templates, amplitudes, templates, channel_map, clusterIDs, cluster_quality, pc_features, pc_feature_ind = \
                load_kilosort_data(ks_directory, 
                    sample_rate, 
                    use_master_clock = False,
                    include_pcs = True)

    spike_depths = get_spike_depths(spike_clusters, pc_features, pc_feature_ind)
    spike_amplitudes = get_spike_amplitudes(spike_templates, templates, amplitudes)

    if excluse_noise:
        good_units = clusterIDs[cluster_quality != 'noise']
    else:
        good_units = clusterIDs

    spikes_in_time_range = np.where((spike_times > time_range[0]) * (spike_times < time_range[1]))[0]
    spikes_from_good_units = np.where(np.in1d(spike_clusters, good_units))[0]
    spikes_to_use = np.intersect1d(spikes_in_time_range, spikes_from_good_units)

    if fig is None:
        fig = plt.figure(figsize=(16,6))

    ax = plt.subplot(111)

    selection = np.arange(0, spikes_to_use.size, subselection)

    ax.scatter(spike_times[spikes_to_use[selection]] / (60*60), 
                spike_depths[spikes_to_use[selection]], 
                c = spike_amplitudes[spikes_to_use[selection]], 
                s = np.ones(selection.shape), 
                vmin=0,
                vmax=3000, 
                alpha=0.25,
                cmap='Greys')

    ax.set_ylim([0,3840])

    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Distance from tip (um)')

    if output_path is not None:
        plt.savefig(output_path)