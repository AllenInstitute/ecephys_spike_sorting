import numpy as np 
import matplotlib.pyplot as plt 

from .utils import (get_spike_depths, 
                    get_spike_amplitudes,
                    load_kilosort_data)

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

    good_units = clusterIDs[cluster_quality != 'noise']

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