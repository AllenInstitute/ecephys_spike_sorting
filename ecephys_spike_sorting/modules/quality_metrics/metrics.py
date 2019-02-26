import numpy as np
import pandas as pd
from collections import OrderedDict

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import cdist
from scipy.stats import chi2
from scipy.ndimage.filters import gaussian_filter1d

from ecephys_spike_sorting.common.spike_template_helpers import find_depth_std
from ecephys_spike_sorting.common.epoch import Epoch


def calculate_metrics(spike_times, spike_clusters, amplitudes, channel_map, pc_features, pc_feature_ind, params, epochs = None):

    """ Calculate metrics for all units on one probe

    Inputs:
    ------
    spike_times : numpy.ndarray (num_spikes x 0)
        Spike times in seconds (same timebase as epochs)
    spike_clusters : numpy.ndarray (num_spikes x 0)
        Cluster IDs for each spike time
    amplitudes : numpy.ndarray (num_spikes x 0)
        Amplitude value for each spike time
    channel_map : numpy.ndarray (num_units x 0)
        Original data channel for pc_feature_ind array
    pc_features : numpy.ndarray (num_spikes x num_pcs x num_channels)
        Pre-computed PCs for blocks of channels around each spike
    pc_feature_ind : numpy.ndarray (num_units x num_channels)
        Channel indices of PCs for each unit
    epochs : list of Epoch objects
        contains information on Epoch start and stop times
    params : dict of parameters
        'isi_threshold' : minimum time for isi violations

    
    Outputs:
    --------
    metrics : pandas.DataFrame
        columns for each metric
        one row per unit per epoch


    """

    metrics = pd.DataFrame()

    if epochs is None:
        epochs = [Epoch('complete_session', 0, np.inf)]

    total_units = len(np.unique(spike_clusters))
    total_epochs = len(epochs)

    for epoch in epochs:

        in_epoch = (spike_times > epoch.start_time) * (spike_times < epoch.end_time)

        print("Calculating isi violations")
        isi_viol = calculate_isi_violations(spike_times[in_epoch], spike_clusters[in_epoch], params['isi_threshold'], params['min_isi'])
    	
        print("Calculating firing rate")
        firing_rate = calculate_firing_rate(spike_times[in_epoch], spike_clusters[in_epoch])
        
        print("Calculating amplitude cutoff")
        amplitude_cutoff = calculate_amplitude_cutoff(spike_clusters[in_epoch], amplitudes[in_epoch])
        
        print("Calculating PC metrics")
        peak_channel, isolation_distance, l_ratio, d_prime, nn_hit_rate, nn_miss_rate = calculate_pc_metrics(spike_clusters[in_epoch], 
                                                                                               channel_map,
                                                                                               pc_features[in_epoch,:,:],
                                                                                               pc_feature_ind,
                                                                                               params['num_channels_to_compare'],
                                                                                               params['max_spikes_for_unit'],
                                                                                               params['max_spikes_for_nn'],
                                                                                               params['n_neighbors'])

        cluster_ids = np.unique(spike_clusters)

        epoch_name = [epoch.name] * total_units

        metrics = pd.concat[metrics, pd.DataFrame(data= OrderedDict((('cluster_id', cluster_ids),
                                ('peak_channel', peak_channel), 
                                ('firing_rate' , firing_rate),
                                ('isi_viol' , isi_viol),
                                ('amplitude_cutoff' , amplitude_cutoff),
                                ('isolation_distance' , isolation_distance),
                                ('l_ratio' , l_ratio),
                                ('d_prime' , d_prime),
                                ('nn_hit_rate' , nn_hit_rate),
                                ('nn_miss_rate' , nn_miss_rate),
                                ('epoch_name' , epoch_name),
                                )))]

    return metrics 

# ===============================================================

# HELPER FUNCTIONS TO LOOP THROUGH CLUSTERS:

# ===============================================================

def calculate_isi_violations(spike_times, spike_clusters, isi_threshold, min_isi):

	cluster_ids = np.unique(spike_clusters)

	viol_rates = np.zeros(cluster_ids.shape)

	for idx, cluster_id in enumerate(cluster_ids):
		for_this_cluster = (spike_clusters == cluster_id)
		viol_rates[idx], num_violations = isi_violations(spike_times[for_this_cluster], 
                                                       min_time = np.min(spike_times), 
                                                       max_time = np.max(spike_times), 
                                                       isi_threshold=isi_threshold, 
                                                       min_isi = min_isi)

	return viol_rates


def calculate_firing_rate(spike_times, spike_clusters):

	cluster_ids = np.unique(spike_clusters)

	firing_rates = np.zeros(cluster_ids.shape)

	for idx, cluster_id in enumerate(cluster_ids):
		for_this_cluster = (spike_clusters == cluster_id)
		firing_rates[idx] = firing_rate(spike_times[for_this_cluster], 
                                        min_time = np.min(spike_times),
                                        max_time = np.max(spike_times))

	return firing_rates


def calculate_amplitude_cutoff(spike_clusters, amplitudes):

    cluster_ids = np.unique(spike_clusters)

    amplitude_cutoffs = np.zeros(cluster_ids.shape)

    for idx, cluster_id in enumerate(cluster_ids):
        for_this_cluster = (spike_clusters == cluster_id)
        amplitude_cutoffs[idx] = amplitude_cutoff(amplitudes[for_this_cluster])

    return amplitude_cutoffs

def calculate_pc_metrics(spike_clusters, channel_map, pc_features, pc_feature_ind, num_channels_to_compare, max_spikes_for_cluster, max_spikes_for_nn, n_neighbors):


    assert(num_channels_to_compare % 2 == 1)
    half_spread = int((num_channels_to_compare - 1) / 2)

    cluster_ids = np.unique(spike_clusters)
    peak_channels = np.zeros(cluster_ids.shape)
    actual_channels = np.zeros(cluster_ids.shape)
    isolation_distances = np.zeros(cluster_ids.shape)
    l_ratios = np.zeros(cluster_ids.shape)
    d_primes = np.zeros(cluster_ids.shape)
    nn_hit_rates = np.zeros(cluster_ids.shape)
    nn_miss_rates = np.zeros(cluster_ids.shape)

    for idx, cluster_id in enumerate(cluster_ids):

        feature_inds = pc_feature_ind[idx,:]
        for_unit = np.squeeze(spike_clusters == cluster_id)
        
        pc_max = np.argmax(np.mean(pc_features[for_unit, 0, :],0))
        
        peak_channels[idx] = feature_inds[pc_max]
        actual_channels[idx] = channel_map[peak_channels[idx]]


    for idx, cluster_id in enumerate(cluster_ids):

        print(cluster_id)

        peak_channel = peak_channels[idx]

        if peak_channel < half_spread:
            half_spread_down = int(peak_channel)
        else:
            half_spread_down = half_spread

        if peak_channel + half_spread > np.max(pc_feature_ind):
            half_spread_up = int(np.max(pc_feature_ind) - peak_channel)
        else:
            half_spread_up = half_spread
            
        total_channels = half_spread_up + half_spread_down + 1

        units_for_channel, channel_index = np.unravel_index(np.where(pc_feature_ind.flatten() == peak_channel)[0], pc_feature_ind.shape)

        channels_in_range = (channel_index >= half_spread_down) * (channel_index < 32 - half_spread_up)

        units_for_channel = units_for_channel[channels_in_range]

        channel_index = channel_index[channels_in_range]

        spike_counts = np.zeros(units_for_channel.shape)

        for idx2, cluster_id2 in enumerate(units_for_channel):
            
            spike_counts[idx2] = np.sum(spike_clusters == cluster_id2)
            
        this_unit_idx = np.where(units_for_channel == cluster_id)[0]

        if spike_counts[this_unit_idx] > max_spikes_for_cluster:
            relative_counts = spike_counts / spike_counts[this_unit_idx] * max_spikes_for_cluster
        else:
            relative_counts = spike_counts
            
        all_pcs = np.zeros((0, pc_features.shape[1], total_channels))
        all_labels = np.zeros((0,))
            
        for idx2, cluster_id2 in enumerate(units_for_channel):
            
            subsample = int(relative_counts[idx2])

            index_mask = make_index_mask(spike_clusters, cluster_id2, min_num = 0, max_num = subsample)

            channel_mask = make_channel_mask(cluster_id2, units_for_channel, channel_index, pc_features.shape[2], half_spread_down, half_spread_up)
            pcs = get_unit_pcs(pc_features, index_mask, channel_mask)
            labels = np.ones((pcs.shape[0],)) * cluster_id2
            
            all_pcs = np.concatenate((all_pcs, pcs),0)
            all_labels = np.concatenate((all_labels, labels),0)
            
        all_pcs = np.reshape(all_pcs, (all_pcs.shape[0], pc_features.shape[1]*total_channels))

        isolation_distances[idx], l_ratios[idx] = mahalanobis_metrics(all_pcs, all_labels, cluster_id)

        d_primes[idx] = lda_metrics(all_pcs, all_labels, cluster_id)

        nn_hit_rates[idx], nn_miss_rates[idx] = nearest_neighbors_metrics(all_pcs, all_labels, cluster_id, max_spikes_for_nn, n_neighbors)


    return actual_channels, isolation_distances, l_ratios, d_primes, nn_hit_rates, nn_miss_rates 

# ==========================================================

# IMPLEMENTATION OF ACTUAL METRICS:

# ==========================================================


def isi_violations(spike_train, min_time, max_time, isi_threshold, min_isi=0):
	"""Calculate ISI violations for a spike train.

    Based on metric described in Hill et al. (2011) J Neurosci 31: 8699-8705

    modified by Dan Denman from cortex-lab/sortingQuality GitHub by Nick Steinmetz

    Inputs:
    -------
	spike_train : array of spike times
    min_time : minimum time for potential spikes
    max_time : maximum time for potential spikes
	isi_threshold : threshold for isi violation
	min_isi :

	Outputs:
	--------
	fpRate : rate of contaminating spikes as a fraction of overall rate
        A perfect unit has a fpRate = 0
        A unit with some contamination has a fpRate < 0.05
        A unit with lots of contamination has a fpRate > 0.1
	num_violations : total number of violations

	"""

	isis = np.diff(spike_train)
	num_spikes = len(spike_train)
	num_violations = sum(isis < isi_threshold) 
	violation_time = 2*num_spikes*(isi_threshold - min_isi)
	total_rate = firing_rate(spike_train, min_time, max_time)
	violation_rate = num_violations/violation_time
	fpRate = violation_rate/total_rate

	return fpRate, num_violations


def firing_rate(spike_train, min_time = None, max_time = None):
    """Calculate firing rate for a spike train.

    If no temporal bounds are specified, the first and last spike time are used.

    Inputs:
    -------
    spike_train : numpy.ndarray
        Array of spike times in seconds
    min_time : float
        Time of first possible spike (optional)
    max_time : float
        Time of last possible spike (optional)

    Outputs:
    --------
    fr : float
        Firing rate in Hz

    """

    if min_time is not None and max_time is not None:
        duration = max_time - min_time
    else:
        duration = np.max(spike_train) - np.min(spike_train)

    fr = spike_train.size / duration

    return fr


def amplitude_cutoff(amplitudes, num_histogram_bins = 500, histogram_smoothing_value = 3):

    """ Calculate approximate fraction of spikes missing from a distribution of amplitudes

    Assumes the amplitude histogram is symmetric (not valid in the presence of drift)

    Inspired by metric described in Hill et al. (2011) J Neurosci 31: 8699-8705

    Input:
    ------
    amplitudes : numpy.ndarray
        Array of amplitudes (don't need to be in physical units)

    Output:
    -------
    fraction_missing : float
        Fraction of missing spikes (0-0.5)
        If more than 50% of spikes are missing, an accurate estimate isn't possible 

    """


    h,b = np.histogram(amplitudes, num_histogram_bins, normed=True)
    
    pdf = gaussian_filter1d(h,histogram_smoothing_value)
    support = b[:-1]

    peak_index = np.argmax(pdf)
    G = np.argmin(np.abs(pdf[peak_index:] - pdf[0])) + peak_index

    bin_size = np.mean(np.diff(support))
    fraction_missing = np.sum(pdf[G:])*bin_size

    fraction_missing = np.min([fraction_missing, 0.5])

    return fraction_missing


def mahalanobis_metrics(all_pcs, all_labels, this_unit_id):

    """ Calculates isolation distance and L-ratio (metrics computed from Mahalanobis distance)

    Based on metrics described in Schmitzer-Torbert et al. (2005) Neurosci 131: 1-11

    Inputs:
    -------
    all_pcs : numpy.ndarray (num_spikes x PCs)
        2D array of PCs for all spikes
    all_labels : numpy.ndarray (num_spikes x 0)
        1D array of cluster labels for all spikes
    this_unit_id : Int
        number corresponding to unit for which these metrics will be calculated

    Outputs:
    --------
    isolation_distance : float
        Isolation distance of this unit
    l_ratio : float
        L-ratio for this unit

    """
    
    pcs_for_this_unit = all_pcs[all_labels == this_unit_id,:]
    pcs_for_other_units = all_pcs[all_labels != this_unit_id, :]
    
    mean_value = np.expand_dims(np.mean(pcs_for_this_unit,0),0)
    
    VI = np.linalg.inv(np.cov(pcs_for_this_unit.T))

    mahalanobis_other = np.sort(cdist(mean_value,
                       pcs_for_other_units,
                       'mahalanobis', VI = VI)[0])
    
    mahalanobis_self = np.sort(cdist(mean_value,
                             pcs_for_this_unit,
                             'mahalanobis', VI = VI)[0])
    
    n = np.min([pcs_for_this_unit.shape[0], pcs_for_other_units.shape[0]]) # number of spikes
    dof = pcs_for_this_unit.shape[1] # number of features
    
    l_ratio = np.sum(1 - chi2.cdf(pow(mahalanobis_other,2), dof)) / mahalanobis_other.shape[0]
    isolation_distance = pow(mahalanobis_other[n-1],2)
    
    return isolation_distance, l_ratio




def lda_metrics(all_pcs, all_labels, this_unit_id):

    """ Calculates d-prime based on Linear Discriminant Analysis

    Based on metric described in Hill et al. (2011) J Neurosci 31: 8699-8705

    Inputs:
    -------
    all_pcs : numpy.ndarray (num_spikes x PCs)
        2D array of PCs for all spikes
    all_labels : numpy.ndarray (num_spikes x 0)
        1D array of cluster labels for all spikes
    this_unit_id : Int
        number corresponding to unit for which these metrics will be calculated

    Outputs:
    --------
    d_prime : float
        Isolation distance of this unit
    l_ratio : float
        L-ratio for this unit

    """
    
    X = all_pcs
    
    y = np.zeros((X.shape[0],),dtype='bool')
    y[all_labels == this_unit_id] = True
    
    lda = LDA(n_components=1)
    
    X_flda = lda.fit_transform(X, y)
      
    flda_this_cluster  = X_flda[np.where(y)[0]]
    flda_other_cluster = X_flda[np.where(np.invert(y))[0]]
        
    d_prime = (np.mean(flda_this_cluster) - np.mean(flda_other_cluster))/np.sqrt(0.5*(np.std(flda_this_cluster)**2+np.std(flda_other_cluster)**2))
        
    return d_prime



def nearest_neighbors_metrics(all_pcs, all_labels, this_unit_id, max_spikes_for_nn, n_neighbors):

    """ Calculates unit contamination based on NearestNeighbors search in PCA space

    Based on metrics described in Chung, Magland et al. (2017) Neuron 95: 1381-1394

    Inputs:
    -------
    all_pcs : numpy.ndarray (num_spikes x PCs)
        2D array of PCs for all spikes
    all_labels : numpy.ndarray (num_spikes x 0)
        1D array of cluster labels for all spikes
    this_unit_id : Int
        number corresponding to unit for which these metrics will be calculated
    max_spikes_for_nn : Int
        number of spikes to use (calculation can be very slow when this number is >20000)
    n_neighbors : Int
        number of neighbors to use

    Outputs:
    --------
    hit_rate : float
        Fraction of neighbors for target cluster that are also in target cluster
    miss_rate : float
        Fraction of neighbors outside target cluster that are in target cluster

    """

    total_spikes = all_pcs.shape[0]
    ratio = max_spikes_for_nn / total_spikes
    this_unit = all_labels == this_unit_id
    
    X = np.concatenate((all_pcs[this_unit,:], all_pcs[np.invert(this_unit),:]),0)

    n = np.sum(this_unit)
    
    if ratio < 1:
        inds = np.arange(0,X.shape[0]-1,1/ratio).astype('int')
        X = X[inds,:]
        n = int(n * ratio)
        

    nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(X)
    distances, indices = nbrs.kneighbors(X)   
    
    this_cluster_inds = np.arange(n)
    
    this_cluster_nearest = indices[:n,1:].flatten()
    other_cluster_nearest = indices[n:,1:].flatten()
    
    hit_rate = np.mean(this_cluster_nearest < n)
    miss_rate = np.mean(other_cluster_nearest < n)
    
    return hit_rate, miss_rate

# ==========================================================

# HELPER FUNCTIONS:

# ==========================================================

def make_index_mask(spike_clusters, unit_id, min_num, max_num):

    """ Create a mask for the spike index dimensions of the pc_features array  

    Inputs:
    -------
    spike_clusters : numpy.ndarray (num_spikes x 0)
        Contains cluster IDs for all spikes in pc_features array
    unit_id : Int
        ID for this unit
    min_num : Int
        Minimum number of spikes to return; if there are not enough spikes for this unit, return all False
    max_num : Int
        Maximum number of spikes to return; if too many spikes for this unit, return a random subsample

    Output:
    -------
    index_mask : numpy.ndarray (boolean)
        Mask of spike indices for pc_features array

    """
    
    index_mask = spike_clusters == unit_id
        
    inds = np.where(index_mask)[0]
    
    if len(inds) < min_num:
        index_mask = np.zeros((spike_clusters.size,), dtype='bool')
    else:
        index_mask = np.zeros((spike_clusters.size,), dtype='bool')
        order = np.random.permutation(inds.size)
        index_mask[inds[order[:max_num]]] = True
        
    return index_mask


def make_channel_mask(unit_id, units_for_channel, channel_index, total_pc_channels, half_spread_down, half_spread_up):

    """ Create a mask for the channel dimension of the pc_features array  

    Inputs:
    -------
    unit_id : Int
        ID for this unit
    units_for_channel : numpy.ndarray
        List of units with overlapping PC channels
    channel_index : numpy.ndarray
        List of channel indices for these units
    total_pc_channels : Int
        Max number of PCs available
    half_spread_down : Int
        Number of channels below peak to keep
    half_spread_up : Int
        Number of channels above peak to keep

    Output:
    -------
    channel_mask : numpy.ndarray (boolean)
        Mask of channel indices for pc_features array

    """
    
    channel_mask = np.zeros((total_pc_channels,), dtype='bool')
    ch = channel_index[units_for_channel == unit_id][0]
    channel_mask[ch-half_spread_down:ch+half_spread_up+1] = True
    
    return channel_mask


def get_unit_pcs(these_pc_features, index_mask, channel_mask):

    """ Use the index_mask and channel_mask to return PC features for one unit 

    Inputs:
    -------
    these_pc_features : numpy.ndarray (float)
        Array of pre-computed PC features (num_spikes x num_PCs x num_channels)
    index_mask : numpy.ndarray (boolean)
        Mask for spike index dimension of pc_features array
    channel_mask : numpy.ndarray (boolean)
        Mask for channel index dimension of pc_features array

    Output:
    -------
    unit_PCs : numpy.ndarray (float)
        PCs for one unit (num_spikes x num_PCs x num_channels)

    """

    unit_PCs = these_pc_features[index_mask,:,:]

    unit_PCs = unit_PCs[:,:,channel_mask]
    
    return unit_PCs