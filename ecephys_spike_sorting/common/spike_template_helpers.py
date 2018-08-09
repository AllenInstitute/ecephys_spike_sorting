#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 19:00:45 2018

@author: joshs
"""

from scipy.interpolate import griddata
from scipy.signal import correlate
from scipy.ndimage.filters import gaussian_filter1d

import numpy as np

def find_depth(template):
    
    return np.argmax(np.max(template,0)-np.min(template,0))

def find_depth_std(template, channels_to_ignore=None):

    waveform_std = np.std(template,0)

    if channels_to_ignore is not None:
        waveform_std[channels_to_ignore] = 0

    waveform_std_smooth = gaussian_filter1d(waveform_std, 2)

    threshold = np.max(waveform_std) / 2
    above_threshold = np.where(waveform_std > threshold)[0]
    diffs = np.diff(above_threshold)
    continuous_segments = np.where(diffs > 1)[0]

    peak_chan = np.argmax(waveform_std_smooth)

    if len(continuous_segments) > 8 or len(above_threshold) > 10:
        is_noise = True
    else:
        is_noise = False

    return peak_chan, is_noise

def find_height(template):
    
    return np.max(np.max(template,0)-np.min(template,0))

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


def get_templates_for_cluster(spike_templates, spike_clusters, clusterId):
    
    templatesForCluster = np.unique(spike_templates[spike_clusters == clusterId])
    
    return templatesForCluster