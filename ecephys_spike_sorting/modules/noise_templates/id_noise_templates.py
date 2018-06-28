import numpy as np

from scipy.signal import correlate

from ecephys_spike_sorting.common.spike_template_helpers import find_depth
from ecephys_spike_sorting.common.utils import write_cluster_group_tsv, load_kilosort_data

def id_noise_templates(kilosortFolder, sample_rate, params):

    spike_times, spike_clusters, amplitudes, templates, channel_map, clusterIDs, cluster_quality = \
            load_kilosort_data(kilosortFolder, sample_rate)

    auto_noise = np.zeros(ids.shape,dtype=bool)

    for idx, tempID in enumerate(ids):
    
        these_clusters = spike_clusters == tempID
    
        template = templates[tempID,:,:]
        
        times = spike_times[these_templates]
    
        depth = find_depth(template)
    
        std_thresh = params['std_thresh']
        waveform_spread = params['waveform_spread']/2
    
        S = np.std(template[:,depth-waveform_spread:depth+waveform_spread],1)
        
        thresh2 = params['thresh2']
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

    quality = np.zeros(auto_noise.shape)
    quality[auto_noise] = -1
    
    write_cluster_group_tsv(ids, quality, folder)
    
    return ids, auto_noise
    