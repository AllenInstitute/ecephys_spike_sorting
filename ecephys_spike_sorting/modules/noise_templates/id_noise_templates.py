#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 14:56:49 2018

@author: joshs
"""

import numpy as np

from scipy.signal import correlate

from ecephys_spike_sorting.common.spike_template_helpers import find_depth
from ecephys_spike_sorting.common.utils import write_cluster_group_tsv

def id_noise_templates(folder):

    spike_times = np.load(os.path.join(folder,'spike_times.npy'))
    spike_templates = np.load(os.path.join(folder,'spike_templates.npy'))
    amplitudes = np.load(os.path.join(folder,'amplitudes.npy'))
    templates = np.load(os.path.join(folder,'templates.npy'))
    unwhitening_mat = np.load(os.path.join(folder,'whitening_mat_inv.npy'))
                    
    templates = templates[:,21:,:] # remove zeros
    spike_templates = np.squeeze(spike_templates) # fix dimensions
    spike_times = np.squeeze(spike_times) / args['sample_rate'] # fix dimensions and convert to seconds
                    
    unwhitened_temps = np.zeros((templates.shape))
    
    for temp_idx in range(templates.shape[0]):
        
        unwhitened_temps[temp_idx,:,:] = np.dot(np.ascontiguousarray(templates[temp_idx,:,:]),np.ascontiguousarray(unwhitening_mat))
    
    ids = np.unique(spike_templates) #np.arange(templateIDs.size) # [425, 426, 428, 100, 31, 61, 64, 11, 0, 506]
    
    auto_noise = np.zeros(ids.shape,dtype=bool)

    for idx, tempID in enumerate(ids):
    
        these_templates = spike_templates == tempID
    
        template = unwhitened_temps[tempID,:,:]
        
        times = spike_times[these_templates]/30000.
    
        depth = find_depth(template)
    
        std_thresh = 2.5
    
        S = np.std(template[:,depth-5:depth+5],1)
        
        thresh2 = 0.2
        wv = template[:,depth]
        C = correlate(wv,wv,mode='same')
        C = C/np.max(C)
        
        a = np.where(C > thresh2)[0]
        d = np.diff(a)
        b = np.where(d > 1)[0]
        
        h, bins = np.histogram(np.diff(times), bins=np.linspace(0,0.1,100))
        h = h/np.max(h)
        
        H = np.mean(h[:3])/np.max(h)
    
        if False: #((np.max(S) < std_thresh or np.argmax(wv) < 10 or np.argmin(wv) < 10) and H > 0.01) or len(b) > 0 or np.min(wv) > -5:
            auto_noise[idx] = True;
        else:
            auto_noise[idx] = False

    quality = np.zeros(auto_noise.shape)
    quality[auto_noise] = -1
    
    write_cluster_group_tsv(ids, quality, folder)
    
    return ids, auto_noise
    