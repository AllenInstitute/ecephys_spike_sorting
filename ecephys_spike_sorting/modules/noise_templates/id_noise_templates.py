import numpy as np

from scipy.signal import correlate

from ecephys_spike_sorting.common.spike_template_helpers import find_depth

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
    waveform_spread = params['waveform_spread']/2
    thresh2 = params['thresh2']

    # #############################################

    auto_noise = np.zeros(cluster_ids.shape,dtype=bool)

    for idx, tempID in enumerate(cluster_ids):
    
        these_clusters = spike_clusters == tempID
    
        template = templates[tempID,:,:]
        
        times = spike_times[these_templates]
    
        depth = find_depth(template)
    
        S = np.std(template[:,depth-waveform_spread:depth+waveform_spread],1)
        
        wv = template[:,depth]
        C = correlate(wv,wv,mode='same')
        C = C/np.max(C)
        
        a = np.where(C > thresh2)[0]
        d = np.diff(a)
        b = np.where(d > 1)[0]
        
        h, bins = np.histogram(np.diff(times), bins=np.linspace(0,0.1,100))
        h = h/np.max(h)
        
        H = np.mean(h[:3])/np.max(h)
    
        if ((np.max(S) < std_thresh or \
            np.argmax(wv) < params['min_peak_sample'] or \
            np.argmin(wv) < params['min_trough_sample']) and \
             H > params['contamination_ratio']) or \
             len(b) > 0 or \
             np.min(wv) > params['min_height']:
            auto_noise[idx] = True;
        else:
            auto_noise[idx] = False

    is_noise = np.zeros(auto_noise.shape)
    is_noise[auto_noise] = -1
    
    return ids, is_noise
    