import numpy as np 
import matplotlib.pyplot as plt 

from scipy.signal import butter, filtfilt, medfilt

from .utils import (get_spike_depths, 
                    get_spike_amplitudes,
                    load_kilosort_data,
                    rms)


def plotKsTemplates(ks_directory, raw_data_file, sample_rate = 30000, bit_volts = 0.195, time_range = [10, 11], exclude_noise=True, fig=None, output_path=None):

    """
    Compares the template-based model to the raw data

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

    for i in range(D.shape[1]):
        D[:,i] = filtfilt(b, a, D[:,i])

    D = D / np.max(np.abs(D))

    if exclude_noise:
        good_units = clusterIDs[cluster_quality != 'noise']
    else:
        good_units = clusterIDs

    spikes_in_time_range = np.where((spike_times > start_index) * (spike_times < end_index))[0]
    spikes_from_good_units = np.where(np.in1d(spike_templates, good_units))[0]
    spikes_to_use = np.intersect1d(spikes_in_time_range, spikes_from_good_units)

    Z = np.zeros(D.shape)

    for idx, time in enumerate(spike_times[spikes_to_use] - start_index):
        if (time < Z.shape[0] - 42 and time > 40):
            template = np.squeeze(templates[spike_templates[spikes_to_use[idx]],:,:])
            Z[int(time-40):int(time-40+61),:] += template * amplitudes[spikes_to_use[idx]]
    
    ax = plt.subplot(211)

    ax.imshow(D[:,1::2].T,
               vmin=-0.25,
               vmax=0.25,
               aspect='auto',
               origin='lower',
               cmap='RdGy')

    ax.axis('off')

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
        plt.close('all')


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

    if exclude_noise:
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
        plt.close('all')



def plotContinuousFile(raw_data_file, sample_rate = 30000, bit_volts = 0.195, noise_threshold = 20, time_range = [1000, 1002], fig=None, output_path=None):

    """
    Compares the template-based model to the raw data

    Inputs:
    ------
    raw_data_file : str
        Path to raw .dat or .bin file
    sample_rate : float
        Sample rate of original data (Hz)
    bit_volts : float
        Conversion factor for raw data to microvolts
    noise_threshold : float
        Distance above median to classify as noise channel
    time_range : [float, float]
        Min/max of time range for plot
    fig : matplotlib.pyplot.figure
        Figure handle to use for plotting
    output_path : str
        Path for saving the image

    Outputs:
    --------
    Saves image to output_path (optional)

    """

    raw_data = np.memmap(raw_data_file, dtype='int16')
    data = np.reshape(raw_data, (int(raw_data.size / 384), 384))

    if fig is None:
        fig = plt.figure(figsize=(15,12))

    plt.clf()

    start_index = time_range[0] * sample_rate
    end_index = time_range[1] * sample_rate

    b, a = butter(3, [10/(sample_rate/2), 10000/(sample_rate/2)], btype='band')

    D = data[start_index:end_index, :] * bit_volts
    D_filt = np.zeros(D.shape)

    for i in range(D.shape[1]):
        D_filt[:,i] = filtfilt(b, a, D[:,i])

    offset_values = np.apply_along_axis(np.median, axis=0, arr=D)
    rms_values = np.apply_along_axis(rms, axis=0, arr=D_filt)
     
    ax = plt.subplot(325)
    ax.hist(offset_values, bins=np.linspace(-1000,100,50))
    ax.set_xlabel('Channel offset')

    ax = plt.subplot(326)
    ax.hist(rms_values, bins=np.linspace(0,100,50))
    ax.set_xlabel('RMS value')

    above_median = rms_values - medfilt(rms_values,11)
    noise_channels = np.where(above_median > noise_threshold)[0]

    rms_values[rms_values > 100] = 100

    ax = plt.subplot(321)

    t = np.linspace(0,D.shape[0]/sample_rate,D.shape[0])

    spacing = 500

    for i in range(D.shape[1]):
        if i in noise_channels:
            color = 'r'
        else:
            color = 'k'
        ax.plot(t,D[:,i]+i*spacing,color,alpha=rms_values[i]/100)

    ax.axis('off')
        
    ax = plt.subplot(322)

    for i in range(D.shape[1]):
        if i in noise_channels:
            color = 'r'
        else:
            color = 'k'
        ax.plot(t,D_filt[:,i]+i*spacing,color,alpha=rms_values[i]/100)
        
    ax.axis('off')

    ax = plt.subplot(323)

    t = np.linspace(0,D.shape[0]/sample_rate,D.shape[0])

    spacing = 300

    for i in range(10):
        if i in noise_channels:
            color = 'r'
        else:
            color = 'k'
        ax.plot(t, np.ones(t.shape)+i*spacing,color='teal',linewidth=1.)
        ax.plot(t,D[:,i]+i*spacing,color,alpha=0.8,linewidth=0.5)
        
    ax.axis('off')
        
    ax = plt.subplot(324)

    for i in range(10):
        if i in noise_channels:
            color = 'r'
        else:
            color = 'k'
        ax.plot(t, np.ones(t.shape)+i*spacing,color='teal',linewidth=1.)
        ax.plot(t,D_filt[:,i]+i*spacing,color,alpha=0.8,linewidth=0.5)
           
    ax.axis('off')

    if output_path is not None:
        plt.savefig(output_path)
        plt.close('all')
        

def plotFullProbeTSNE(ks_directory, total_spikes=150000, exclude_noise = True, fig=None, output_path = None):

    """
    Plots t-SNE embedding of spikes across the entire probe

    Requires the fast_tsne module

    https://github.com/KlugerLab/FIt-SNE

    This is a useful way to assess overall data quality for an experiment, as it makes probe
    motion very easy to see.

    This implementation is based on Matlab code from github.com/cortex-lab/spikes

    Inputs:
    ------
    ks_directory : str
        Path to Kilosort outputs
    total_spikes : int
        number of spikes to use
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
    from os.path import dirname
    import sys
    sys.path.append('/home/joshs/GitHub/FIt-SNE')

    try:
        from fast_tsne import fast_tsne
    except ModuleNotFoundError:
        print('fast_tsne not available; please download from https://github.com/KlugerLab/FIt-SNE')
        return

    from matplotlib.cm import get_cmap

    spike_times, spike_clusters, spike_templates, amplitudes, templates, channel_map, clusterIDs, cluster_quality, pc_features, pc_feature_ind = \
                load_kilosort_data(ks_directory, 
                    30000., 
                    convert_to_seconds = False,
                    use_master_clock = False,
                    include_pcs = True)

    if exclude_noise:
        good_units = clusterIDs[cluster_quality != 'noise']
    else:
        good_units = clusterIDs

    spikes_from_good_units = np.where(np.in1d(spike_clusters, good_units))[0]

    print("creating PC matrix...")

    random_spike_inds = np.random.permutation(spikes_from_good_units.size)
    random_spike_inds = random_spike_inds[:total_spikes]
    num_pc_features = pc_features.shape[1]

    good_spike_clusters = spike_clusters[spikes_from_good_units]

    all_pcs = np.zeros((total_spikes, np.max(pc_feature_ind) * num_pc_features + 1))

    for idx, i in enumerate(random_spike_inds):
        
        unit_id = good_spike_clusters[i]
        channels = pc_feature_ind[unit_id,:]
        
        for j in range(0,num_pc_features):
            all_pcs[idx, channels + np.max(pc_feature_ind) * j] = pc_features[i,j,:]

    print("Computing T-SNE")
    Z = fast_tsne(all_pcs, perplexity=50, seed=42)

    cmap = get_cmap('Spectral')
    color_assignment = np.random.rand(np.max(good_spike_clusters)+1)
    colors = np.squeeze(cmap(color_assignment[good_spike_clusters[random_spike_inds]]))

    print("Plotting...")

    if fig is None:
        fig = plt.figure(figsize=(10,10))

    ax = plt.subplot(111)
    ax.scatter(Z[:,0], Z[:,1], c=colors, s=0.5)
    ax.axis('off')
    
    if output_path is not None:
       plt.savefig(output_path)
       plt.close('all')