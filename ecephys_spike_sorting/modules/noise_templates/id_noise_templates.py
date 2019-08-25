import numpy as np

from scipy.signal import correlate
from sklearn.ensemble import RandomForestClassifier

import pickle

def id_noise_templates_rf(spike_times, spike_clusters, cluster_ids, templates, params):

    """
    Uses a random forest classifier to identify noise units based on waveform shape

    Inputs:
    -------
    spike_times : spike times (in seconds)
    spike_clusters : cluster IDs for each spike time []
    cluster_ids : all unique cluster ids
    templates : template for each unit output by Kilosort

    Outputs:
    -------
    cluster_ids : same as input
    is_noise : numpy array with -1 for noise, 0 otherwise

    Parameters:
    ----------
    'classifier_path' : path to pickled classifier object

    """
    
    # #############################################

    classifier_path = params['classifier_path']

    # #############################################

    classifier = pickle.load(open(classifier_path, 'rb'))

    feature_matrix = np.zeros((cluster_ids.size, 61, 32))

    peak_channels = np.squeeze(np.argmax(np.max(templates,1) - np.min(templates,1),1))

    for idx, unit in enumerate(cluster_ids):
        
        peak_channel = peak_channels[unit]

        min_chan = np.max([0,peak_channel-16])
        if min_chan == 0:
            max_chan = 32
        else:
            max_chan = np.min([templates.shape[2], peak_channel+16])
            if max_chan == templates.shape[2]:
                min_chan = max_chan - 32

        sub_template = templates[unit, :, min_chan:max_chan]

        feature_matrix[idx,:,:] = sub_template

    feature_matrix = np.reshape(feature_matrix[:,:,:], (feature_matrix.shape[0], feature_matrix.shape[1] * feature_matrix.shape[2]), 2)
    feature_matrix = feature_matrix[:,::4]

    is_noise = classifier.predict(feature_matrix)
    is_noise[is_noise > 0] = -1

    return cluster_ids, is_noise
    


def id_noise_templates(cluster_ids, templates, channel_map, params):

    """
    Uses a set of heuristics to identify noise units based on waveform shape

    Inputs:
    -------
    cluster_ids : all unique cluster ids
    templates : template for each unit output by Kilosort
    channel_map : mapping between template channels and actual probe channels

    Outputs:
    -------
    cluster_ids : same as input
    is_noise : numpy array with -1 for noise, 0 otherwise

    """

    is_noise = np.zeros((templates.shape[0],),dtype='bool')

    is_noise += check_template_spread(templates, channel_map, params)
    is_noise += check_template_spatial_peaks(templates, channel_map, params)
    is_noise += check_template_temporal_peaks(templates, channel_map, params)
   
    return cluster_ids, is_noise[cluster_ids]
    

def check_template_spread(templates, channel_map, params):

    """
    Checks templates for abnormally large or small channel spread

    Inputs:
    -------
    templates : template for each unit output by Kilosort
    channel_map : mapping between template channels and actual probe channels

    Outputs:
    -------
    is_noise : boolean array, True at index of noise templates

    Parameters:
    ----------
    """

    return np.zeros((templates.shape[0],),dtype='bool')


def check_template_spatial_peaks(templates, channel_map, params):

    """
    Checks templates for multiple spatial peaks

    Inputs:
    -------
    templates : template for each unit output by Kilosort
    channel_map : mapping between template channels and actual probe channels

    Outputs:
    -------
    is_noise : boolean array, True at index of noise templates

    Parameters:
    ----------
    """

    return np.zeros((templates.shape[0],),dtype='bool')


def check_template_temporal_peaks(templates, channel_map, params):

    """
    Checks templates for multiple or abnormal temporal peaks

    Inputs:
    -------
    templates : template for each unit output by Kilosort
    channel_map : mapping between template channels and actual probe channels

    Outputs:
    -------
    is_noise : boolean array, True at index of noise templates

    Parameters:
    ----------
    """

    return np.zeros((templates.shape[0],),dtype='bool')