import numpy as np
import pandas as pd
from collections import OrderedDict


def remove_double_counted_spikes(spike_times, spike_clusters, amplitudes, channel_map, templates, pc_features, pc_feature_ind, sample_rate, params, epochs = None):

    """ Remove putative double-counted spikes from Kilosort outputs

    Inputs:
    ------
    spike_times : numpy.ndarray (num_spikes x 0)
        Spike times in samples 
    spike_clusters : numpy.ndarray (num_spikes x 0)
        Cluster IDs for each spike time
    amplitudes : numpy.ndarray (num_spikes x 0)
        Amplitude value for each spike time
    channel_map : numpy.ndarray (num_units x 0)
        Original data channel for pc_feature_ind array
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
    amplitudes : numpy.ndarray (num_spikes x 0)
        Amplitude value for each spike time
    pc_features : numpy.ndarray (num_spikes x num_pcs x num_channels)
        Pre-computed PCs for blocks of channels around each spike
    overlap_matrix : numpy.ndarray (num_clusters x num_clusters)
        Matrix indicating number of spikes removed for each pair of clusters

    """

    unit_list = np.arange(np.max(spike_clusters)+1)

    peak_channels = channel_map[np.argmax(np.max(templates,1) - np.min(templates,1),1)]
    
    order = np.argsort(peak_channels)
    
    overlap_matrix = np.zeros((peak_channels.size, peak_channels.size))

    within_unit_overlap_samples = int(params['within_unit_overlap_window'] / sample_rate)
    between_unit_overlap_samples = int(params['between_unit_overlap_window'] / sample_rate)


    for idx1, unit_id1 in enumerate(unit_list[order]):

        for_unit1 = np.where(spike_clusters == unit_id1)[0]

        spikes_to_remove = find_within_unit_overlap(spike_times[for_unit1], within_unit_overlap_samples)

        spike_times, spike_clusters, amplitudes, pc_features = remove_spikes(spike_times, spike_clusters, amplitudes, pc_features, for_unit1[spikes_to_remove])

        overlap_matrix[idx1, idx1] = len(spikes_to_remove)


    for idx1, unit_id1 in enumerate(unit_list[order]):
        
        for_unit1 = np.where(spike_clusters == unit_id1)[0]
        
        for idx2, unit_id2 in enumerate(unit_list[order]):
            
            if idx2 > idx1 and np.abs(peak_channels[unit_id1] - peak_channels[unit_id2]) < params['between_unit_channel_distance']:
                
                for_unit2 = np.where(spike_clusters == unit_id1)[0]

                spikes_to_remove1, spikes_to_remove2 = find_between_unit_overlap(spike_times[for_unit1], spike_times[for_unit2], between_unit_overlap_samples)

                spike_times, spike_clusters, amplitudes, pc_features = remove_spikes(spike_times, 
                                                                                     spike_clusters, 
                                                                                     amplitudes, 
                                                                                     pc_features, 
                                                                                     np.concatenate((for_unit1[spikes_to_remove1], for_unit2[spikes_to_remove2])))

                overlap_matrix[idx1, idx2] = len(spikes_to_remove1) + len(spikes_to_remove2)

    return spike_times, spike_clusters, amplitudes, pc_features, overlap_matrix

                
def find_within_unit_overlap(spike_train, overlap_window = 9):

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

    return        


def find_between_unit_overlap(spike_train1, spike_train2, overlap_window = 9):

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


    Outputs
    -------
    spikes_to_remove1 : numpy.ndarray
        Indices of overlapping spikes in spike_train1
    spikes_to_remove2 : numpy.ndarray
        Indices of overlapping spikes in spike_train2

    """

    return      


def remove_spikes(spike_times, spike_clusters, amplitudes, pc_features, spikes_to_remove):

    """
    Removes spikes from Kilosort outputs

    Inputs:
    ------
    spike_times : numpy.ndarray (num_spikes x 0)
        Spike times in samples 
    spike_clusters : numpy.ndarray (num_spikes x 0)
        Cluster IDs for each spike time
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
    amplitudes : numpy.ndarray (num_spikes - spikes_to_remove x 0)
    pc_features : numpy.ndarray (num_spikes - spikes_to_remove x num_pcs x num_channels)

    """

    spike_times = np.delete(spike_times, spikes_to_remove, 0)
    spike_clusters = np.delete(spike_clusters, spikes_to_remove, 0)
    amplitudes = np.delete(amplitudes, spikes_to_remove, 0)
    pc_features = np.delete(pc_features, spikes_to_remove, 0)

    return spike_times, spike_clusters, amplitudes, pc_features

