import numpy as np
import pandas as pd
import psutil
from collections import OrderedDict

import warnings

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score

from scipy.spatial.distance import cdist
from scipy.stats import chi2
from scipy.ndimage.filters import gaussian_filter1d
from scipy import special

from ...common.epoch import Epoch
from ...common.utils import printProgressBar, get_spike_depths


def calculate_metrics(spike_times, spike_clusters, spike_templates, amplitudes, channel_map, channel_pos, templates, pc_features, pc_feature_ind, params, epochs = None):

    """ Calculate metrics for all units on one probe

    Inputs:
    ------
    spike_times : numpy.ndarray (num_spikes x 0)
        Spike times in seconds (same timebase as epochs)
    spike_clusters : numpy.ndarray (num_spikes x 0)
        Cluster IDs for each spike time
    spike_templates : numpy.ndarray (num_spikes x 0)
        template IDs for each spike time
    amplitudes : numpy.ndarray (num_spikes x 0)
        Amplitude value for each spike time
    channel_map : numpy.ndarray (num_channels x 0)
        Original data channel for pc_feature_ind array
    channel_pos : numpy.ndarray (num_channels x 2)
        Original data channel positions in um
    templates : numpy.ndarray (num_units, num_timepoints, num_channels]
        Templates to which the spikes are assigned
    pc_features : numpy.ndarray (num_spikes x num_pcs x num_channels)
        Pre-computed PCs for blocks of channels around each spike
    pc_feature_ind : numpy.ndarray (num_units x num_channels)
        Channel indices of PCs for each unit
    params : dict of parameters
        'isi_threshold' : minimum time for isi violations
        'tbin_sec' : time bin for ccg for contam_rate
    epochs : list of Epoch objects
        contains information on Epoch start and stop times

    
    Outputs:
    --------
    metrics : pandas.DataFrame
        one column for each metric
        one row per unit per epoch

    """

    metrics = pd.DataFrame()

    if epochs is None:
        epochs = [Epoch('complete_session', 0, np.inf)]
    
#   define a short epoch for testing
    # epochs = [Epoch('test',0,10)]
    
    include_pcs = params['include_pcs']
    
    
#   after any curation, the number of templates may not match the number of templates  
#   many of these cluster ID's may have no spikes assigned, 
#   but arrays of metrics need to be sized for the full set
    total_units = np.max(spike_clusters) + 1
    print('total unite: ' + repr(total_units))
    
    template_ids = np.zeros((total_units,), dtype='uint16')
    spike_templates = np.squeeze(spike_templates)
    
    
#    earlier versions assumed num clusters = num templates
#    [total_units, dummy, dummy] = templates.shape
    
    total_epochs = len(epochs)

    for epoch in epochs:

        in_epoch = (spike_times > epoch.start_time) * (spike_times < epoch.end_time)

        print("Calculating isi violations")
        isi_viol, num_viol = calculate_isi_violations(spike_times[in_epoch], spike_clusters[in_epoch], total_units, params['isi_threshold'], params['min_isi'])
        
        print("Calculating contamination rate")
        contam_rate = calculate_contam_rate(spike_times[in_epoch], spike_clusters[in_epoch], total_units, params['tbin_sec'], params['isi_threshold'])

        print("Calculating presence ratio")
        presence_ratio = calculate_presence_ratio(spike_times[in_epoch], spike_clusters[in_epoch], total_units)

        print("Calculating firing rate")
        firing_rate = calculate_firing_rate(spike_times[in_epoch], spike_clusters[in_epoch], total_units)
        
        print("Calculating amplitude cutoff")
        amplitude_cutoff = calculate_amplitude_cutoff(spike_clusters[in_epoch], amplitudes[in_epoch], total_units)
        
        if include_pcs:
            
            # determine template this is the best match for each cluster id
            # initialize template ids
            template_ids = template_ids + total_units + 10  # unassinged template_ids out of range
            curr_spike_clusters = spike_clusters[in_epoch]
            curr_spike_templates = spike_templates[in_epoch]
            curr_cluster_ids = np.unique(curr_spike_clusters)
            for cid in curr_cluster_ids:
                cluster_templates = curr_spike_templates[np.where(curr_spike_clusters==cid)]
                template_ids[cid] = np.argmax(np.bincount(cluster_templates)) 

            print("Calculating PC-based metrics")
            isolation_distance, l_ratio, d_prime, nn_hit_rate, nn_miss_rate = calculate_pc_metrics(spike_clusters[in_epoch],
                                                                                                spike_templates[in_epoch],
                                                                                                total_units,
                                                                                                curr_cluster_ids,
                                                                                                template_ids,
                                                                                                pc_features[in_epoch,:,:],
                                                                                                pc_feature_ind,
                                                                                                channel_pos,
                                                                                                params['max_radius_um'],
                                                                                                params['max_spikes_for_unit'],
                                                                                                params['max_spikes_for_nn'],
                                                                                                params['n_neighbors'])
  
            print("Calculating silhouette score")
            nSpikes = spike_times[in_epoch].size
            the_silhouette_score = calculate_silhouette_score(spike_clusters[in_epoch], 
                                                       spike_templates[in_epoch],
                                                       total_units,                                                      
                                                       pc_features[in_epoch,:,:],
                                                       pc_feature_ind,
                                                       min(nSpikes, params['n_silhouette']))


            print("Calculating drift metrics")
            max_drift, cumulative_drift = calculate_drift_metrics(spike_times[in_epoch],
                                                       spike_clusters[in_epoch], 
                                                       spike_templates,
                                                       template_ids,
                                                       total_units,
                                                       pc_features[in_epoch,:,:],
                                                       pc_feature_ind,
                                                       channel_pos,
                                                       params['drift_metrics_interval_s'],
                                                       params['drift_metrics_min_spikes_per_interval'])
        else:
            # fill in empty arrays for dataframe            
            isolation_distance = np.zeros((total_units,))
            l_ratio = np.zeros((total_units,))
            d_prime = np.zeros((total_units,))
            nn_hit_rate = np.zeros((total_units,))
            nn_miss_rate = np.zeros((total_units,))
            the_silhouette_score = np.zeros((total_units,))
            max_drift = np.zeros((total_units,))
            cumulative_drift = np.zeros((total_units,))
            
            
        cluster_ids = np.arange(total_units)

        epoch_name = [epoch.name] * len(cluster_ids)

        metrics = pd.concat((metrics, pd.DataFrame(data= OrderedDict((('cluster_id', cluster_ids),
                                ('firing_rate' , firing_rate),
                                ('presence_ratio' , presence_ratio),
                                ('isi_viol' , isi_viol),
                                ('num_viol', num_viol),
                                ('amplitude_cutoff' , amplitude_cutoff),
                                ('isolation_distance' , isolation_distance),
                                ('contam_rate', contam_rate),
                                ('l_ratio' , l_ratio),
                                ('d_prime' , d_prime),
                                ('nn_hit_rate' , nn_hit_rate),
                                ('nn_miss_rate' , nn_miss_rate),
                                ('silhouette_score', the_silhouette_score),
                                ('max_drift', max_drift),
                                ('cumulative_drift', cumulative_drift),
                                ('epoch_name' , epoch_name),
                                )))))

    return metrics 

# ===============================================================

# HELPER FUNCTIONS TO LOOP THROUGH CLUSTERS:

# ===============================================================

def calculate_isi_violations(spike_times, spike_clusters, total_units, isi_threshold, min_isi):

    cluster_ids = np.unique(spike_clusters)

    viol_rates = np.zeros((total_units,))
    
    num_viol =np.zeros((total_units,))

    for idx, cluster_id in enumerate(cluster_ids):

        printProgressBar(idx+1, len(cluster_ids))

        for_this_cluster = (spike_clusters == cluster_id)
        viol_rates[cluster_id], num_viol[cluster_id] = isi_violations(spike_times[for_this_cluster], 
                                                               min_time = np.min(spike_times), 
                                                               max_time = np.max(spike_times), 
                                                               isi_threshold=isi_threshold, 
                                                               min_isi = min_isi)

    return viol_rates, num_viol

def calculate_presence_ratio(spike_times, spike_clusters, total_units):

    cluster_ids = np.unique(spike_clusters)

    ratios = np.zeros((total_units,))

    for idx, cluster_id in enumerate(cluster_ids):

        printProgressBar(idx + 1, len(cluster_ids))

        for_this_cluster = (spike_clusters == cluster_id)
        ratios[cluster_id] = presence_ratio(spike_times[for_this_cluster], 
                                                       min_time = np.min(spike_times), 
                                                       max_time = np.max(spike_times))

    return ratios



def calculate_firing_rate(spike_times, spike_clusters, total_units):

    cluster_ids = np.unique(spike_clusters)

    firing_rates = np.zeros((total_units,))

    min_time = np.min(spike_times)
    max_time = np.max(spike_times)

    for idx, cluster_id in enumerate(cluster_ids):

        printProgressBar(idx + 1, len(cluster_ids))

        for_this_cluster = (spike_clusters == cluster_id)
        firing_rates[cluster_id] = firing_rate(spike_times[for_this_cluster], 
                                        min_time = np.min(spike_times),
                                        max_time = np.max(spike_times))

    return firing_rates


def calculate_amplitude_cutoff(spike_clusters, amplitudes, total_units):

    cluster_ids = np.unique(spike_clusters)

    amplitude_cutoffs = np.zeros((total_units,))

    for idx, cluster_id in enumerate(cluster_ids):

        printProgressBar(idx + 1, len(cluster_ids))


        for_this_cluster = (spike_clusters == cluster_id)
        amplitude_cutoffs[cluster_id] = amplitude_cutoff(amplitudes[for_this_cluster])

    return amplitude_cutoffs


def calculate_contam_rate(spike_times, spike_clusters, total_units, tbin_sec, refPer_sec):

    cluster_ids = np.unique(spike_clusters)

    contam_rate = np.ones((total_units,))

    for idx, cluster_id in enumerate(cluster_ids):

        printProgressBar(idx + 1, len(cluster_ids))

        curr_st_sec = spike_times[spike_clusters == cluster_id]
        
        if len(curr_st_sec) > 10: 
            contam_rate[cluster_id] = contamination_rate(curr_st_sec, tbin_sec, refPer_sec)           

    return contam_rate


def calculate_pc_metrics(spike_clusters,
                         spike_templates,
                         total_units,
                         cluster_ids,
                         template_ids,
                         pc_features, 
                         pc_feature_ind, 
                         channel_pos,
                         max_radius_um, 
                         max_spikes_for_cluster, 
                         max_spikes_for_nn, 
                         n_neighbors):

# OLDER calculatioon assuming linear array and using a number of channels instead of max_radius
#    assert(num_channels_to_compare % 2 == 1)
#    half_spread = int((num_channels_to_compare - 1) / 2)


    peak_channels = np.zeros((total_units,), dtype='uint16')
    isolation_distances = np.zeros((total_units,))
    l_ratios = np.zeros((total_units,))
    d_primes = np.zeros((total_units,))
    nn_hit_rates = np.zeros((total_units,))
    nn_miss_rates = np.zeros((total_units,))
    

# pc_feature_ind is NOT updated by phy during manual clustering

    for idx, cluster_id in enumerate(cluster_ids):
            
        # individual pcs are stored for each spike, independent of cluster id
        for_unit = np.squeeze(spike_clusters == cluster_id)
        pc_max = np.argmax(np.mean(pc_features[for_unit, 0, :],0))
        
        # pc_feature_ind are stored according to template, using the 
        # most common template for spikes in this cluster in this epoch
        peak_channels[cluster_id] = pc_feature_ind[template_ids[cluster_id], pc_max]

    for idx, cluster_id in enumerate(cluster_ids):

        
        printProgressBar(idx + 1, len(cluster_ids))

            
        peak_channel = peak_channels[cluster_id]
        
        # calculate distances from all channels to peak channel
        chan_dist = np.sqrt(np.square(channel_pos[:,0] - channel_pos[peak_channel,0]) + \
                            np.square(channel_pos[:,1] - channel_pos[peak_channel,1]) )

# OLDER calculatioon assuming linear array
#        half_spread_down = peak_channel \
#            if peak_channel < half_spread \
#            else half_spread
#
#        half_spread_up = np.max(pc_feature_ind) - peak_channel \
#            if peak_channel + half_spread > np.max(pc_feature_ind) \
#            else half_spread

        # which templates have pcs on the peak channel of the current unit?
        # channel index -- which of the channel swithin the set for a single template -- i snot used
        templates_for_channel, channel_index = np.unravel_index(np.where(pc_feature_ind.flatten() == peak_channel)[0], pc_feature_ind.shape)


        # which units have these templates?       
        units_for_channel = np.zeros((0,),dtype='uint16')
        for j in templates_for_channel:
            units_for_channel = np.append(units_for_channel, np.where(template_ids==j))
                  
               
# OLDER calculatioon assuming linear array        
#        units_in_range = (peak_channels[units_for_channel] >= peak_channel - half_spread_down) * \
#                       (peak_channels[units_for_channel] <= peak_channel + half_spread_up)
                        
        
        # of those units that have pc overlap, which have their peak channel 
        # within range of the current unit?              
        units_in_range = np.where( chan_dist[peak_channels[units_for_channel]] < max_radius_um )[0]
           
            
        # If there is at least one neighbor unit in range, compare pcs across 
        # units for channels that overlap AND lie within maximum radius
        
        if len(units_in_range) > 1 :

            units_for_channel = np.asarray(units_for_channel[units_in_range])
                    
    
# OLDER calculatioon assuming linear array
#           channels_to_use = np.arange(peak_channel - half_spread_down, peak_channel + half_spread_up + 1)
            
            channels_to_use = np.where(chan_dist < max_radius_um)[0]

    
            spike_counts = np.zeros(units_for_channel.shape, dtype = 'int')
    
            for idx2, cluster_id2 in enumerate(units_for_channel):
                spike_counts[idx2] = np.sum(spike_clusters == cluster_id2)
                
            this_unit_idx = np.where(units_for_channel == cluster_id)[0]
    
            # calculate how many spikes from this unit will be used
            if spike_counts[this_unit_idx] > max_spikes_for_cluster:
                relative_counts = spike_counts / spike_counts[this_unit_idx] * max_spikes_for_cluster
            else:
                relative_counts = spike_counts
            
            all_pcs = np.zeros((0, pc_features.shape[1], channels_to_use.size))     #dtype = default, double
            all_labels = np.zeros((0,), dtype = 'int')
                
            for idx2, cluster_id2 in enumerate(units_for_channel):
    
# if any manual curation as been done, the cluster ids are no longer identical to the template ids
# That means we can't use a universal channelmask. Rather, we have to check for each spike what
# channels are there (recorded in pc_feature_ind) and take those that are included in 
# channels to use
#                try:
#                    channel_mask = make_channel_mask(cluster_id2, pc_feature_ind, channels_to_use)
#                except IndexError:
#                    # Occurs when pc_feature_ind does not contain all channels of interest
#                    # In that case, we will exclude this unit for the calculation
#                    pass
#                else:
#                    subsample = int(relative_counts[idx2])
#                    index_mask = make_index_mask(spike_clusters, cluster_id2, min_num = 0, max_num = subsample)
#        
#                    pcs = get_unit_pcs(pc_features, index_mask, channel_mask)
#                    labels = np.ones((pcs.shape[0],), dtype = 'int') * cluster_id2
#                    
#                    all_pcs = np.concatenate((all_pcs, pcs),0)
#                    all_labels = np.concatenate((all_labels, labels),0)
                
                subsample = int(relative_counts[idx2]) # how many spikes to use from this unit
                index_mask = make_index_mask(spike_clusters, cluster_id2, min_num = 0, max_num = subsample)
                
                pcs = get_unit_pcs(pc_features, index_mask, spike_templates, channels_to_use, pc_feature_ind)
                labels = np.ones((pcs.shape[0],), dtype = 'int') * cluster_id2

                all_pcs = np.concatenate((all_pcs, pcs),0)
                all_labels = np.concatenate((all_labels, labels),0) 
                
            all_pcs = np.reshape(all_pcs, (all_pcs.shape[0], pc_features.shape[1]*channels_to_use.size))
            
            num_pcs = all_pcs.shape[0];
#            num_pcs_str = 'cluster_id: ' + repr(cluster_id) + '; num pcs: ' + repr(num_pcs)
#            print(num_pcs_str)
            
            pcs_for_this_unit = all_pcs[all_labels == cluster_id,:].shape[0]   
            pcs_for_other_units = all_pcs[all_labels != cluster_id, :].shape[0]
        
        else:
            # no near neighbor units to compare
            num_pcs = 0
            pcs_for_this_unit = 0
            pcs_for_other_units = 0
        
        
        if num_pcs > 10 and pcs_for_this_unit > 5 and pcs_for_other_units > 5 :

            isolation_distances[cluster_id], l_ratios[cluster_id] = mahalanobis_metrics(all_pcs, all_labels, cluster_id)

            d_primes[cluster_id] = lda_metrics(all_pcs, all_labels, cluster_id)

            nn_hit_rates[cluster_id], nn_miss_rates[cluster_id] = nearest_neighbors_metrics(all_pcs, all_labels, cluster_id, max_spikes_for_nn, n_neighbors)

        else:

            isolation_distances[cluster_id] = np.nan
            d_primes[cluster_id] = np.nan
            nn_hit_rates[cluster_id] = np.nan
            nn_miss_rates[cluster_id] = np.nan


    return isolation_distances, l_ratios, d_primes, nn_hit_rates, nn_miss_rates 


def calculate_silhouette_score(spike_clusters,
                                 spike_templates,
                                 total_units,                                
                                 pc_features, 
                                 pc_feature_ind,
                                 total_spikes):
    
    # total_spikes = number of spikes to sample, given in the metrics params

    random_spike_inds = np.random.permutation(spike_clusters.size)
    random_spike_inds = random_spike_inds[:total_spikes]
    num_pc_features = pc_features.shape[1]

    # initialize array to hold pcs: number of spikes X number of channeles x number of pc features
    all_pcs = np.zeros((total_spikes, np.max(pc_feature_ind) * num_pc_features + 1))

    for idx, i in enumerate(random_spike_inds):
        
        # unit_id = spike_clusters[i]
        
        # look up channel using the template id for this spike
        template_id = spike_templates[i]       
        channels = pc_feature_ind[template_id,:]
        
        # fill pcs into the correct channels for this spike
        for j in range(0,num_pc_features):
            all_pcs[idx, channels + np.max(pc_feature_ind) * j] = pc_features[i,j,:]

    cluster_labels = spike_clusters[random_spike_inds]

    cluster_ids = np.unique(cluster_labels)

    SS = np.empty((total_units, total_units))
    SS[:] = np.nan

    for idx1, i in enumerate(cluster_ids):

        printProgressBar(idx1+1, len(cluster_ids))
        
        for idx2, j in enumerate(cluster_ids):
            
            if j > i:
                # positions of cluster labels = i or j
                inds = np.in1d(cluster_labels, np.array([i,j]))
                X = all_pcs[inds,:]
                labels = cluster_labels[inds]
                
                if len(labels) > 2:
                    SS[i,j] = silhouette_score(X, labels)

    with warnings.catch_warnings():
      warnings.simplefilter("ignore")
      a = np.nanmin(SS, 0)
      b = np.nanmin(SS, 1)

    return np.array([np.nanmin([a,b]) for a, b in zip(a,b)])


def calculate_drift_metrics(spike_times,
                            spike_clusters,
                            spike_templates,
                            unit_template_ids,
                            total_units,
                            pc_features, 
                            pc_feature_ind,
                            channel_pos,
                            interval_length,
                            min_spikes_per_interval):

    max_drift = np.zeros((total_units,))
    cumulative_drift = np.zeros((total_units,))
    
    # need to pick out spikes for each cluster that were extracted using the 
    # the majority template. Make array of the majority template for these clusters
    maj_tid = unit_template_ids[spike_clusters]
    match_maj = spike_templates==maj_tid
    
    # calculate size of the arrays we'll be copying
    # 2*(number of spikes*4) for spike_times and spike_clusters
    # number of spikes*number of template channels*4 for first pc on each site
#    pc_size = pc_features.shape
#    nmatch = match_maj.shape
#    memuse = 2*nmatch[0]*4 + nmatch[0]*pc_size[2]*4

#    print("expected size of new memory: " + repr(memuse))
#    currmem = psutil.Process().memory_info().rss / (1024 * 1024)
#    print("psutil memory info before copies: " + repr(currmem))
    
    
    # make arrays of just those spikes for which the template matches the 
    # majority template for htat cluster. These operations make copies of the
    # arrays.
    m_spike_clusters = spike_clusters[match_maj]
    m_spike_times = spike_times[match_maj]
    
    # same for pc_features, but we only need the first pc for each
    # this operation makes a copy of pc_features so original is not altered
    m_pc_features_sq = np.squeeze(pc_features[match_maj,0,:]);
    # set negative pc_features to zero before taking square
    m_pc_features_sq[m_pc_features_sq < 0] = 0
    # elementwise square
    m_pc_features_sq = pow(m_pc_features_sq, 2) 
    
#    currmem = psutil.Process().memory_info().rss / (1024 * 1024)
#    print("psutil memory info after copies: " + repr(currmem))
    
#    send only
    
    depths = get_spike_depths(m_spike_clusters, unit_template_ids, m_pc_features_sq, pc_feature_ind, channel_pos)
    
    interval_starts = np.arange(np.min(spike_times), np.max(spike_times), interval_length)
    interval_ends = interval_starts + interval_length

    cluster_ids = np.unique(m_spike_clusters)

    for idx, cluster_id in enumerate(cluster_ids):

        printProgressBar(idx+1, len(cluster_ids))

        in_cluster = m_spike_clusters == cluster_id
        times_for_cluster = m_spike_times[in_cluster]
        depths_for_cluster = depths[in_cluster]

        median_depths = []

        for t1, t2 in zip(interval_starts, interval_ends):

            in_range = (times_for_cluster > t1) * (times_for_cluster < t2)
            
            if np.sum(in_range) >= min_spikes_per_interval:
                median_depths.append(np.median(depths_for_cluster[in_range]))
            else:
                median_depths.append(np.nan)
            
        median_depths = np.array(median_depths)
            
        max_drift[cluster_id] = np.around(np.nanmax(median_depths) - np.nanmin(median_depths),2)
        cumulative_drift[cluster_id] = np.around(np.nansum(np.abs(np.diff(median_depths))),2)

    return max_drift, cumulative_drift


# ==========================================================

# IMPLEMENTATION OF ACTUAL METRICS:

# ==========================================================


def isi_violations(spike_train, min_time, max_time, isi_threshold, min_isi=0):
    """Calculate ISI violations for a spike train.

    Based on metric described in Hill et al. (2011) J Neurosci 31: 8699-8705

    modified by Dan Denman from cortex-lab/sortingQuality GitHub by Nick Steinmetz
    
    modified by Jennifer Colonell to correctly solve the quadratic equation

    Inputs:
    -------
    spike_train : array of spike times
    min_time : minimum time for potential spikes
    max_time : maximum time for potential spikes
    isi_threshold : threshold for isi violation
    min_isi : threshold for duplicate spikes

    Outputs:
    --------
    fpRate : rate of contaminating spikes as a fraction of overall rate
        A perfect unit has a fpRate = 0
        A unit with some contamination has a fpRate < 0.5
        A unit with lots of contamination has a fpRate > 1.0
    num_violations : total number of violations

    """

    duplicate_spikes = np.where(np.diff(spike_train) <= min_isi)[0]

    spike_train = np.delete(spike_train, duplicate_spikes + 1)
    isis = np.diff(spike_train)

    num_spikes = len(spike_train)
    num_violations = sum(isis < isi_threshold) 
    violation_time = 2*num_spikes*(isi_threshold - min_isi)
    total_rate = firing_rate(spike_train, min_time, max_time)
    c = num_violations/(violation_time*total_rate)
    if c < 0.25:        # valid solution to quadratic eq. for fpRate:
        fpRate = (1 - np.sqrt(1-4*c))/2
    else:               # no valid solution to eq, call fpRate = 1
        fpRate = 1.0
     
# older estimate that assumes f<<1
#    violation_rate = num_violations/violation_time
#    fpRate = violation_rate/total_rate

    return fpRate, num_violations



def presence_ratio(spike_train, min_time, max_time, num_bins=100):
    """Calculate fraction of time the unit is present within an epoch.

    Inputs:
    -------
    spike_train : array of spike times
    min_time : minimum time for potential spikes
    max_time : maximum time for potential spikes

    Outputs:
    --------
    presence_ratio : fraction of time bins in which this unit is spiking

    """

    h, b = np.histogram(spike_train, np.linspace(min_time, max_time, num_bins))

    return np.sum(h > 0) / num_bins


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


    h,b = np.histogram(amplitudes, num_histogram_bins, density=True)
    
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
    
    try:
        VI = np.linalg.inv(np.cov(pcs_for_this_unit.T))
    except np.linalg.linalg.LinAlgError: # case of singular matrix
        return np.nan, np.nan

    mahalanobis_other = np.sort(cdist(mean_value,
                       pcs_for_other_units,
                       'mahalanobis', VI = VI)[0])
    

    
##    mahalanobis_self = np.sort(cdist(mean_value,
#                             pcs_for_this_unit,
#                             'mahalanobis', VI = VI)[0])
    
    n = np.min([pcs_for_this_unit.shape[0], pcs_for_other_units.shape[0]]) # number of spikes

    if n >= 2:
        
        dof = pcs_for_this_unit.shape[1] # number of features
        
        l_ratio = np.sum(1 - chi2.cdf(pow(mahalanobis_other,2), dof)) / mahalanobis_other.shape[0]
        isolation_distance = pow(mahalanobis_other[n-1],2)

    else:
        l_ratio = np.nan 
        isolation_distance = np.nan 
    
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


def make_channel_mask(unit_id, pc_feature_ind, channels_to_use):

    """ Create a mask for the channel dimension of the pc_features array  

    Inputs:
    -------
    unit_id : Int
        ID for this unit
    pc_feature_ind : np.ndarray
        Channels used for PC calculation for each unit
    channels_to_use : np.ndarray
        Channels to use for calculating metrics

    Output:
    -------
    channel_mask : numpy.ndarray
        Channel indices to extract from pc_features array
    
    """
    
    these_inds = pc_feature_ind[unit_id, :]
    channel_mask = [np.argwhere(these_inds == i)[0][0] for i in channels_to_use]

    return np.array(channel_mask)

# original version, which assumes a fixed channel mask for all spikes in a cluster
# true only if no curation has happened in phy
#def get_unit_pcs(these_pc_features, index_mask, channel_mask):
#
#    """ Use the index_mask and channel_mask to return PC features for one unit 
#
#    Inputs:
#    -------
#    these_pc_features : numpy.ndarray (float)
#        Array of pre-computed PC features (num_spikes x num_PCs x num_channels)
#    index_mask : numpy.ndarray (boolean)
#        Mask for spike index dimension of pc_features array
#    channel_mask : numpy.ndarray (boolean)
#        Mask for channel index dimension of pc_features array
#
#    Output:
#    -------
#    unit_PCs : numpy.ndarray (float)
#        PCs for one unit (num_spikes x num_PCs x num_channels)
#
#    """
#
#    unit_PCs = these_pc_features[index_mask,:,:]
#
#    unit_PCs = unit_PCs[:,:,channel_mask]
#    
#    return unit_PCs
    
def get_unit_pcs(these_pc_features, index_mask, spike_templates, channels_to_use, pc_feature_ind):

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

    # start with an empty 3D array
    [nspike,npcs,nchan] = these_pc_features.shape
    
    nchan_to_use = channels_to_use.shape[0]

    unit_PCs = np.zeros((0,npcs,nchan_to_use))
    
    # get list of templates included in this cluster
    # for data with no curation, there will just be one value   
    template_ids = np.unique(spike_templates[index_mask])
    
    # for each template id, create a channel mask (if possible) and extract templates
    for tid in template_ids:
        curr_idx = index_mask & (spike_templates == tid)
        try:
            channel_mask = make_channel_mask(tid, pc_feature_ind, channels_to_use)            
        except IndexError:
            # Occurs when pc_feature_ind does not contain all channels of interest
            # In that case, we will exclude this unit for the calculation
            pass
        else:
            curr_pcs = these_pc_features[curr_idx,:,:]
            curr_pcs = curr_pcs[:,:,channel_mask]
            unit_PCs = np.append(unit_PCs,curr_pcs,axis=0)
    
    return unit_PCs


def ccg(st1, st2, nbins, tbin, auto):
    
    """ calculate crosscorrelogram between two sets of spike times (st1, st2)
        in seconds, with bin width tbin, time lags = plus/minus nbins.
        Algorithm from Kilosort2, written by Marius Pachitariu
        
    st1 : spike times for set #1 in sec
    st2 : spike times for set #2 in sec
    nbins : ccg will be calculated for 2*nbins + 1, 
    tbin : bin width in seconds
    
    output:
        
    K = ccg histogram
    Qi
    Q00
    Q01
    
    """
    # print('ccg num spikes = ' + repr(len(st1)))
    st1 = np.sort(np.squeeze(st1))
    st2 = np.sort(np.squeeze(st2))
    
    dt = nbins*tbin  # cross correlogram spans -dt-dt
    
    T = max(np.max(st1),np.max(st2)) - min(np.min(st1),np.min(st2))
    
    # traverse both spike trains together, keeping track of the spikes in the first
    # spike train that are within dt of the second spike train
    ilow = 0
    ihigh = 0
    j = 0
    
    n_st2 = len(st2)
    n_st1 = len(st1)
    
    K = np.zeros((2*nbins+1,))
    
    while j < n_st2:                      # walk over all spikes in 2nd spike train
        while (ihigh < n_st1) and (st1[ihigh] < st2[j]+dt):            
            ihigh = ihigh + 1             # increase upper bound until its outisde the dt range
        while (ilow < n_st1) and (st1[ilow] <= st2[j]-dt):
            ilow = ilow + 1                # increase lower bound until it is inside the dt range
        if ilow > n_st1:
            break
        if st1[ilow] > st2[j] + dt:
            # if the lower bound is actually outside of the dt range, means
            # there were no spikes in range of the ccg
            # just move on to next spike st2
            j = j + 1
            continue
        for k in range(ilow,ihigh):
            # for all spikes within the plus/minus dt range
            ibin = int(np.round((st2[j]-st1[k])/tbin))    # calculate which bin
            K[ibin + nbins] = K[ibin + nbins] + 1    # increment corresponding bin in correlogram
        j = j + 1   # go to next spike in st2
        
    if auto:
        # print('nspikes, zero bin: ' + repr(n_st1) + ', ' + repr(K[nbins]))
        # if this is an autocorrelogram, remove the self-found spikes from the zero bin
        K[nbins] = K[nbins] - n_st1     # remove "self found" spikes from 
    
    irange1 = np.concatenate((np.arange(1, int(nbins/2)), np.arange(int(3/2*nbins), 2*nbins-1)),0) # this index range corresponds to the CCG shoulders, excluding end bins
    irange2 = np.arange(nbins-50, nbins-10)  # 40 channels to negative side of peak
    irange3 = np.arange(nbins+10, nbins+50)  # 40 channels to positive side of peak
    
    # Normalize the firing rate in the shoulders by the mean firing rate
    # A Poisson process has a flat ACG (equal numbers of spikes at all ISIs) and these ratios would = 1
    mean_firing_rate = (n_st2)/T
    Q00 = (sum(K[irange1])/(n_st1 * tbin * len(irange1)))/mean_firing_rate
    Q01_neg = (sum(K[irange2])/(n_st1 * tbin * len(irange2)))/mean_firing_rate
    Q01_pos = (sum(K[irange3])/(n_st1 * tbin * len(irange3)))/mean_firing_rate
    Q01 = max(Q01_neg, Q01_pos)
    
    #print('firing rate, Q00, Q01: ' + repr(mean_firing_rate) + ', ' + repr(Q00) + ', ' + repr(Q01))
    
    # Get highest spike rate of the sampled time regions
    R00 = max(np.mean(K[irange2]), np.mean(K[irange3])) # Larger of the two shoulders near t = 0
    R00 = max(R00, np.mean(K[irange1])) # compare this to the asymptotic shoulder
    
    # Calculate "refractoriness for periods from 1*tbin to 10*tbin
    Qi = np.zeros((11,))
    Ri = np.zeros((11,))
    for i in range(1,11):
        irange = np.arange(nbins-i,nbins+i)
        Qi[i] = (sum(K[irange])/(2*i*tbin+1))/mean_firing_rate    #rate in this time period/mean rate
        #print( 'K[nbins-i], Qi: ' + repr(K[nbins-i]) + ', ' + repr( Qi[i]))
        

        # Marius note: this is tricky: we approximate the Poisson likelihood with a gaussian of equal mean and variance
        # that allows us to integrate the probability that we would see <N spikes in the center of the
        # cross-correlogram from a distribution with mean R00*i spikes
        
        # this calculation is done in KS2 but never used
        # n = sum(K[irange])/2
        # lam = R00 + i
        # Ri[i] =  1/2 * (1+ special.erf((n - lam)/np.sqrt(2*lam)))
        
    return K, Qi, Q00, Q01, Ri

def contamination_rate(st_sec, tbin_sec, refPer_sec):
    # given a set of spike times in sec, calculate the KS2 contamination percent
    # differences from the KS2 standard calc:
    #      when calculating an acg (as here) only remove self-counted spikes (rather than zeroing the lowest bin)
    #      this will give higher values for the contamination rate when there are duplicate spikes
    #
    #      instead of just taking the range of the acg with the lowest contamination, take the range corresponding
    #      to the user specified refractory period. This will also usually give higher values for the contamination rate.
    
    refPerBin = int(refPer_sec/tbin_sec)
    if refPerBin == 0:
        refPerBin = 1   # if refractory period < bin size, take the first bin
    
    K, Qi, Q00, Q01, rir = ccg(st_sec, st_sec, 500, tbin_sec, True); # compute the auto-correlogram with 500 bins at 1ms bins
    
    normFactor = (max(Q00, Q01))
    
    if normFactor > 0:
        contam_rate  = Qi[refPerBin]/normFactor # get the Q[i] that includes the refractory period
    else:
        contam_rate = 1
    
    return contam_rate