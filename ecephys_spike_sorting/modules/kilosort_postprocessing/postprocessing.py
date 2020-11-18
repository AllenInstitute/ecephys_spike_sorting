import numpy as np
import pandas as pd
from collections import OrderedDict

from ...common.utils import printProgressBar

def remove_double_counted_spikes(spike_times, spike_clusters, spike_templates, 
                                 amplitudes, channel_map, channel_pos, templates, pc_features, 
                                 pc_feature_ind, template_features, cluster_amplitude, 
                                 sample_rate, params, epochs = None):

    """ Remove putative double-counted spikes from Kilosort outputs

    Inputs:
    ------
    spike_times : numpy.ndarray (num_spikes x 0)
        Spike times in samples 
    spike_clusters : numpy.ndarray (num_spikes x 0)
        Cluster IDs for each spike time
    spike_templates : numpy.ndarray (num_spikes x 0)
        Template IDs for each spike time
    amplitudes : numpy.ndarray (num_spikes x 0)
        Amplitude value for each spike time
    channel_map : numpy.ndarray (num_units x 0)
        Original data channel for pc_feature_ind array
    channel_pos : numpy.ndarray (num_channels x 2)
        X and Z coordinates for each channel used in the sort    
    templates : numpy.ndarray (num_units x num_channels x num_samples)
        Spike templates for each unit
    pc_features : numpy.ndarray (num_spikes x num_pcs x num_channels)
        Pre-computed PCs for blocks of channels around each spike
    pc_feature_ind : numpy.ndarray (num_units x num_channels)
        Channel indices of PCs for each unit
    sample_rate : Float
        Sample rate of spike times
    params : dict of parameters
        'within_unit_overlap_window' : time window for removing overlapping spikes
        'between_unit_overlap_window' : time window for removing overlapping spikes
        'between_unit_channel_distance' : number of channels over which to search for overlapping spikes
    epochs : list of Epoch objects
        contains information on Epoch start and stop times

    
    Outputs:
    --------
    spike_times : numpy.ndarray (num_spikes x 0)
        Spike times in seconds (same timebase as epochs)
    spike_clusters : numpy.ndarray (num_spikes x 0)
        Cluster IDs for each spike time
    spike_templates : numpy.ndarray (num_spikes x 0)
        Template IDs for each spike time
    amplitudes : numpy.ndarray (num_spikes x 0)
        Amplitude value for each spike time
    pc_features : numpy.ndarray (num_spikes x num_pcs x num_channels)
        Pre-computed PCs for blocks of channels around each spike
    template_features : numpy.ndarray (num_spikes x number of template features)
        projections of each spike onto the template features
    overlap_matrix : numpy.ndarray (num_clusters x num_clusters)
        Matrix indicating number of spikes removed for each pair of clusters

    """

    peak_chan_idx = np.squeeze(np.argmax(np.max(templates,1) - np.min(templates,1),1))

    # to accomdate case where matlab writes out chan map as (1,nchan) instead of (nchan,1)
    channel_map = np.squeeze(channel_map);
    peak_channels = np.squeeze(channel_map[peak_chan_idx])
    
    num_clusters = peak_channels.size;
    
    order = np.argsort(peak_channels)
    
    unit_list = np.arange(order.size+1)
    
    sorted_unit_list = unit_list[order]

    overlap_matrix = np.zeros((num_clusters, num_clusters))
    

    within_unit_overlap_samples = int(params['within_unit_overlap_window'] * sample_rate)
    between_unit_overlap_samples = int(params['between_unit_overlap_window'] * sample_rate)

    print('Removing within-unit overlapping spikes...')

    spikes_to_remove = np.zeros((0,))

    for idx1, unit_id1 in enumerate(sorted_unit_list):

        printProgressBar(idx1+1, len(unit_list))

        for_unit1 = np.where(spike_clusters == unit_id1)[0]

        to_remove = find_within_unit_overlap(spike_times[for_unit1], within_unit_overlap_samples)

        overlap_matrix[idx1, idx1] = len(to_remove)

        spikes_to_remove = np.concatenate((spikes_to_remove, for_unit1[to_remove]))

    spike_times, spike_clusters, spike_templates, amplitudes, pc_features, template_features = remove_spikes(spike_times, 
                                                                        spike_clusters, 
                                                                        spike_templates, 
                                                                        amplitudes, 
                                                                        pc_features, 
                                                                        template_features, 
                                                                        spikes_to_remove)

    print('Removing between-unit overlapping spikes...')

    spikes_to_remove = np.zeros((0,))

    for idx1, unit_id1 in enumerate(sorted_unit_list):

        printProgressBar(idx1+1, len(unit_list))

        for_unit1 = np.where(spike_clusters == unit_id1)[0]
        
        for idx2, unit_id2 in enumerate(unit_list[order]):
            
            deltaX = np.squeeze(channel_pos[peak_chan_idx[unit_id2],0] - channel_pos[peak_chan_idx[unit_id1],0])
            deltaZ = np.squeeze(channel_pos[peak_chan_idx[unit_id2],1] - channel_pos[peak_chan_idx[unit_id1],1])
            
            dist = pow( (pow(deltaX,2) + pow(deltaZ,2)), 0.5 )
            
            if idx2 > idx1 and dist < params['between_unit_dist_um']:
                
                amp1 = cluster_amplitude[unit_id1]
                amp2 = cluster_amplitude[unit_id2]
                
                for_unit2 = np.where(spike_clusters == unit_id2)[0]

                to_remove1, to_remove2 = find_between_unit_overlap(spike_times[for_unit1], spike_times[for_unit2], amp1, amp2, between_unit_overlap_samples, params['deletion_mode'] )

                overlap_matrix[idx1, idx2] = overlap_matrix[idx1, idx2] + len(to_remove1) 
                overlap_matrix[idx2, idx1] = overlap_matrix[idx2, idx1] + len(to_remove2)

                spikes_to_remove = np.concatenate((spikes_to_remove, for_unit1[to_remove1], for_unit2[to_remove2]))


    spike_times, spike_clusters, spike_templates, amplitudes, pc_features, template_features = remove_spikes(spike_times, 
                                                                         spike_clusters,
                                                                         spike_templates, 
                                                                         amplitudes, 
                                                                         pc_features, 
                                                                         template_features, 
                                                                         np.unique(spikes_to_remove))
#   build overlap summary 
    overlap_summary = np.zeros((num_clusters, 5), dtype=int )
    for idx1, unit_id1 in enumerate(unit_list[order]):
        overlap_summary[idx1,0] = unit_id1
        overlap_summary[idx1,1] = np.sum(spike_clusters == unit_id1)
        overlap_summary[idx1,2] = overlap_matrix[idx1,idx1]
        overlap_summary[idx1,3] = np.sum(overlap_matrix[idx1,:]) - overlap_matrix[idx1,idx1]
        overlap_summary[idx1,4] = sorted_unit_list[np.argmax(overlap_matrix[idx1,:])]     
#   sort by label
    new_order = np.argsort(overlap_summary[:,0])
    overlap_summary = overlap_summary[new_order,:]

    return spike_times, spike_clusters, spike_templates, amplitudes, pc_features, template_features, overlap_matrix, overlap_summary

                
def find_within_unit_overlap(spike_train, overlap_window = 5):

    """
    Finds overlapping spikes within a single spike train.

    Parameters
    ----------
    spike_train : numpy.ndarray
        Spike times (in samples)
    overlap_window : int
        Number of samples to search for overlapping spikes


    Outputs
    -------
    spikes_to_remove : numpy.ndarray
        Indices of overlapping spikes in spike_train

    """

    spikes_to_remove = np.where(np.diff(spike_train) < overlap_window)[0]

    return spikes_to_remove


def find_between_unit_overlap(spike_train1, spike_train2, amp1, amp2, overlap_window = 5, deletionMode = 'lowAmpCluster'):

    """
    Finds overlapping spikes between two spike trains

    Parameters
    ----------
    spike_train1 : numpy.ndarray
        Spike times (in samples)
    spike_train2 : numpy.ndarray
        Spike times (in samples)
    overlap_window : int
        Number of samples to search for overlapping spikes
    deletionMode : 'lowAmpCluster' or 'deleteFirst'
        For between unit overlap, option to always delete the earlier spike, or
        delete all duplicates from the cluster with lower average amplitude.


    Outputs
    -------
    spikes_to_remove1 : numpy.ndarray
        Indices of overlapping spikes in spike_train1
    spikes_to_remove2 : numpy.ndarray
        Indices of overlapping spikes in spike_train2

    """


    spike_train = np.concatenate( (spike_train1, spike_train2) )
    original_inds = np.concatenate( (np.arange(len(spike_train1)), np.arange(len(spike_train2)) ) )
    cluster_ids = np.concatenate( (np.zeros((len(spike_train1),)), np.ones((len(spike_train2),))) )

    order = np.argsort(spike_train)
    sorted_train = spike_train[order]
#   trim off the first member of the array of cluster labels; means the later spike will be picked for any pair
    sorted_cluster_ids = cluster_ids[order][1:]

#   Note that when applying this method to spike trains from two different clusters, we are assuming that
#   any pair within the overlap window will consist of a spike from each train. Therefor, only works if
#   the "within_unit_overlap_window" is >= "between_unit_overlap_window".
    
    spikes_to_remove = np.diff(sorted_train) < overlap_window

    if deletionMode == 'deleteFirst':
#   trim off the first member of the array of sorted inds; means the later spike will be picked for any pair
        sorted_inds = original_inds[order][1:] 
        spikes_to_remove1 = sorted_inds[spikes_to_remove * (sorted_cluster_ids == 0)]
        spikes_to_remove2 = sorted_inds[spikes_to_remove * (sorted_cluster_ids == 1)]
    else:
#    for first member of a pair, need sorted index array starting from 0; for late, start from 1
        lateInd = original_inds[order][1:]
        earlyInd = original_inds[order][0:(len(original_inds)-1)]
        if ( amp1 < amp2 ):
#       Remove spikes the cluster with lower amplitude; many duplicate cases are 
#       fitting a tail on a large amplitude feature with a low amplitude spike
#        if (len(spike_train1) < len(spike_train2)):
#           Remove spikes from cluster with fewer spikes
#           Still have the first member of sorted_cluster_ids; to get cases where label 0 is 2nd, add 1
            late0 = lateInd[spikes_to_remove * (sorted_cluster_ids == 0)]
            early0 = earlyInd[spikes_to_remove * (sorted_cluster_ids == 1)]
            spikes_to_remove1 = np.concatenate((late0, early0))
            spikes_to_remove2 = np.array([], dtype=int)
        else:
#           Still have the first member of sorted_cluster_ids; to get cases where label 0 is 2nd, add 1
            late1 = lateInd[spikes_to_remove * (sorted_cluster_ids == 1)]
            early1 = earlyInd[spikes_to_remove * (sorted_cluster_ids == 0)]
            spikes_to_remove2 = np.concatenate((late1, early1))
            spikes_to_remove1 = np.array([], dtype=int)

    return spikes_to_remove1, spikes_to_remove2


def remove_spikes(spike_times, spike_clusters, spike_templates, amplitudes, pc_features, template_features, spikes_to_remove):

    """
    Removes spikes from Kilosort outputs

    Inputs:
    ------
    spike_times : numpy.ndarray (num_spikes x 0)
        Spike times in samples 
    spike_clusters : numpy.ndarray (num_spikes x 0)
        Cluster IDs for each spike time
    spike_templates : numpy.ndarray (num_spikes x 0)
        Template IDs for each spike time
    amplitudes : numpy.ndarray (num_spikes x 0)
        Amplitude value for each spike time
    pc_features : numpy.ndarray (num_spikes x num_pcs x num_channels)
        Pre-computed PCs for blocks of channels around each spike
    spikes_to_remove : numpy.ndarray
        Indices of spikes to remove

    Outputs:
    --------
    spike_times : numpy.ndarray (num_spikes - spikes_to_remove x 0)
    spike_clusters : numpy.ndarray (num_spikes - spikes_to_remove x 0)
    spike_templates : numpy.ndarray (num_spikes - spikes_to_remove x 0)
    amplitudes : numpy.ndarray (num_spikes - spikes_to_remove x 0)
    pc_features : numpy.ndarray (num_spikes - spikes_to_remove x num_pcs x num_channels)

    """

    spike_times = np.delete(spike_times, spikes_to_remove, 0)
    spike_clusters = np.delete(spike_clusters, spikes_to_remove, 0)
    spike_templates = np.delete(spike_templates, spikes_to_remove, 0)
    amplitudes = np.delete(amplitudes, spikes_to_remove, 0)
    pc_features = np.delete(pc_features, spikes_to_remove, 0)
    template_features = np.delete(template_features, spikes_to_remove, 0)

    return spike_times, spike_clusters, spike_templates, amplitudes, pc_features, template_features

