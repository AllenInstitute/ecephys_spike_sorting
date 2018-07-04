import numpy as np

from scipy.signal import correlate
from sklearn.ensemble import RandomForestClassifier

import pickle

from ecephys_spike_sorting.common.spike_template_helpers import find_depth


def id_noise_templates_rf(spike_times, spike_clusters, cluster_ids, templates, params):

    """Identify non-neural units based on waveform shape and ISI histogram

    Inputs:
    -------
    spike_times : spike times (in seconds)
    spike_clusters : cluster IDs for each spike time []
    cluster_ids : all unique cluster ids
    templates : template for each unit output by Kilosort
    classifier : sklearn Random Forest classifier trained on hand-curated data

    Outputs:
    -------
    cluster_ids : same as input
    is_noise : numpy array with -1 for noise, 0 otherwise

    Parameters:
    ----------
    none

    """
    
    # #############################################

    classifier_path = params['classifier_path']

    # #############################################

    classifier = pickle.load(open(classifier_path, 'rb'))

    feature_matrix = np.zeros((cluster_ids.size,templates.shape[1]))

    for idx, unit in enumerate(cluster_ids):
        
        template = templates[unit,:,:]
        depth = find_depth(template)
        feature_matrix[idx,:] = template[:,depth]

    is_noise = 1-2*classifier.predict(feature_matrix)
    
    return cluster_ids, is_noise
    


def id_noise_templates(spike_times, spike_clusters, cluster_ids, templates, params):

    """Identify non-neural units based on waveform shape and ISI histogram

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
    std_thresh : 
    waveform_spread :
    thresh2 :
    min_peak_sample :
    min_trough_sample :
    contamination_ratio :
    min_height :

    """
    
    # #############################################

    std_thresh = params['std_thresh']
    waveform_spread = int(params['waveform_spread']/2)
    thresh2 = params['thresh2']

    # #############################################


    auto_noise = np.zeros(cluster_ids.shape,dtype=bool)


    for idx, clusterID in enumerate(cluster_ids):
    
        for_this_cluster = (spike_clusters == clusterID)
    
        template = templates[clusterID,:,:]
        
        times = spike_times[for_this_cluster]

        if times.size > 0:

            depth = find_depth(template)

            min_chan = np.max([0, depth-waveform_spread])
            max_chan = np.min([depth+waveform_spread, template.shape[1]])

            S = np.std(template[:,min_chan:max_chan],1)
            
            wv = template[:,depth]

            C = correlate(wv,wv,mode='same')

            if np.max(C) > 0:
                C = C/np.max(C)
            
            a = np.where(C > thresh2)[0]
            d = np.diff(a)
            b = np.where(d > 1)[0]

            b = [ ]
                
            h, bins = np.histogram(np.diff(times), bins=np.linspace(0,0.1,100))

            if np.max(h) > 0 and np.max(h) != np.nan:
                h = h/np.max(h)
                H = np.mean(h[:3])/np.max(h)
            else:
                H = 0
            
            if ((np.max(S) < std_thresh or \
                np.argmax(wv) < params['min_peak_sample'] or \
                np.argmin(wv) < params['min_trough_sample']) and \
                 H > params['contamination_ratio']) or \
                 len(b) > 0 or \
                 np.min(wv) > params['min_height']:
                auto_noise[idx] = True;

    is_noise = np.zeros(auto_noise.shape)
    is_noise[auto_noise] = -1
    
    return cluster_ids, is_noise
    