from scipy.interpolate import griddata
from scipy.signal import correlate
import numpy as np
from .spike_ISI import *    

def find_depth(template):
    
    """
    Finds depth based on channel with maximum range.
    """
    
    return np.argmax(np.max(template,0)-np.min(template,0))

def find_height(template):

    """
    Maximum peak-to-trough amplitude of a template
    """
    
    return np.max(np.max(template,0)-np.min(template,0))

def check_template(template, times):

    """
    Detects noise templates based on a set of heuristics
    """
   
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

    if ((np.max(S) < std_thresh or np.argmax(wv) < 10 or np.argmin(wv) < 10) and H > 0.01) or len(b) > 0 or np.min(wv) > -5:
        return False
    else:
        return True


def make_actual_channel_locations(min_chan, max_chan):
    actual_channel_locations = np.zeros((max_chan-min_chan,2))
    xlocations = [16, 48, 0, 32]
    for i in range(min_chan,max_chan):
        actual_channel_locations[i,0] = xlocations[i%4]
        actual_channel_locations[i,1] = np.floor(i/2)*20
    return actual_channel_locations


def make_interp_channel_locations(min_chan, max_chan):
    interp_channel_locations = np.zeros(((max_chan-min_chan)*7,2))
    xlocations = [0, 8, 16, 24, 32, 40, 48]
    for i in range(min_chan,(max_chan-min_chan)*7+min_chan):
        interp_channel_locations[i,0] = xlocations[i%7]
        interp_channel_locations[i,1] = np.floor(i/7)*10
    return interp_channel_locations


def make_interp_temp(templates, indices):
    
    total_samples = templates.shape[1]
    total_channels = templates.shape[2]
    refs = np.array([36, 75, 112, 151, 188, 227, 264, 303, 340, 379])
    loc_a = make_actual_channel_locations(0, total_channels)
    loc_i = make_interp_channel_locations(0, total_channels)

    indices = np.array(indices)
    to_include = np.arange(0,total_channels)
    to_include = np.delete(to_include, refs)
    
    interp_temp = np.zeros((templates.shape[1],templates.shape[2]*7,indices.size))
    
    for i in np.arange(indices.size):
        
        temp = templates[indices[i], :, :]
        
        for t in range(0,total_samples):
            
            interp_temp[t,:,i] = griddata(loc_a[to_include,:], temp[t,to_include], loc_i, method='cubic', fill_value=0, rescale=False)  
        
    return np.reshape(np.mean(interp_temp,2), (total_samples, total_channels, 7)).astype('float')       


def compare_templates(t1, t2):
    
    depth1 = find_depth(t1) / 7
    depth2 = find_depth(t2) / 7
    
    total_channels = t1.shape[1]
    max_padding = 10
    if np.max((depth1,depth2)) < max_padding:
        padding_neg = int(np.max((depth1, depth2)))
    else:
        padding_neg = max_padding
        
    if np.min((depth1,depth2)) > total_channels - max_padding:
        padding_pos = int(total_channels - np.min((depth1, depth2)))
    else:
        padding_pos = max_padding
    
    m1 = np.zeros((61, total_channels+padding_neg+padding_pos, 7))
    m1[:,padding_neg:total_channels+padding_neg,:] = t1
    m2 = np.zeros((61, total_channels+padding_neg+padding_pos, 7))
    
    sim = np.zeros((padding_neg + padding_pos,))
    offset_distance = np.zeros((padding_neg + padding_pos,))
    ii = 0
    
    for idx, offset in enumerate(range(-padding_neg, padding_pos)):
        m2[:,padding_neg+offset:total_channels+padding_neg+offset,:] = t2
        sim[ii] = np.corrcoef(m1.flatten(), m2.flatten())[0,1]
        offset_distance[idx] = -offset*10
        ii += 1
        
    return sim, offset_distance


def compute_isi_score(t1, t2, max_time):
    
    cISI_score, score_weight, ISI1, ISI2, cISI, rcISI = find_cISI_score(t1, t2, max_time)
    
    ms = 5
    ratio = (cISI[:ms*10] + 0.001) / (rcISI[:ms*10] + 0.001)
    weight = 10 - np.linspace(0,9,ms*10)
    weighted_ratio = (ratio * weight)/10
    another_score = np.mean(weighted_ratio)
    
    if np.isnan(another_score) or np.isinf(another_score) or another_score > 1 or another_score < 0:
        another_score = 1
    
    return cISI_score, score_weight, ISI1, ISI2, cISI, rcISI, another_score


def percent_overlap(t1, t2, min_t, max_t, num_bins = 50):
    
    h1,b = np.histogram(t1, bins=np.linspace(min_t, max_t, num_bins))
    h2,b = np.histogram(t2, bins=np.linspace(min_t, max_t, num_bins))
    
    overlap = np.intersect1d(np.where(h1 > 0)[0], np.where(h2 > 0)[0]).size/float(num_bins)
    
    return overlap

def get_templates_for_cluster(spike_templates, spike_clusters, clusterId):
    
    templatesForCluster = np.unique(spike_templates[spike_clusters == clusterId])
    
    return templatesForCluster