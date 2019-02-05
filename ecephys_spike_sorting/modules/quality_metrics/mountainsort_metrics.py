#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 16:43:45 2018

@author: joshs
"""

import numpy as np
from sklearn import decomposition, neighbors

def compute_overlap(data, t1, t2, num_to_use = 500):
    
    num = np.min([t1.size, t2.size, num_to_use])
    
    times1 = sample(t1, num)
    times2 = sample(t2, num)
    
    all_times = np.concatenate((times1, times2))
    all_labels = np.concatenate((np.ones(times1.shape),np.ones(times2.shape)*2))
    
    all_clips = extract_clips(data, all_times)
    
    return overlap_metric(all_clips, all_labels)
    
    
def compute_noise_overlap(data, t1, num_to_use = 500, clip_size=70, clip_offset=15):
    
    num = np.min([t1.size, num_to_use])
    
    times1 = sample(t1, num)
    times2 = np.random.random_integers(0 + clip_offset, data.shape[0] - clip_size + clip_offset, num)
    
    clips = extract_clips(data, times1)
    
    noise_times = np.random.random_integers(0 + clip_offset, data.shape[0] - clip_size + clip_offset, num)
    noise_clips = extract_clips(data, noise_times)
    noise_shape = compute_noise_shape(noise_clips, np.mean(clips,0))
    
    
    all_times = np.concatenate((times1, times2))
    all_labels = np.concatenate((np.ones(times1.shape),np.ones(times2.shape)*0))
    all_clips = extract_clips(data, all_times)
    
    all_clips_new = regress_out_noise_shape(all_clips, noise_shape)
    
    return overlap_metric(all_clips_new, all_labels)
    
    
def overlap_metric(clips, labels):
    
     # do some PCA -- decomposition.pca
    
    num_correct = 0
    num_total = 0
    
    for i, t in enumerate(all_times):
        
        nbrs = neighbors.NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(X)
        distances, indices = nbrs.kneighbors(X)
        
        count 'em up
        
    return 1 - (num_correct / num_total)
    
    
def compute_noise_shape(data, mean_clip):
    
    # something about weighting


def regress_out_noise_shape(clips, shape):
    
    norm = np.linalg.norm(shape)
    
    for i in range(clips.shape[0]):
        clips[i,:] = np.dot(clips[i,:], shape)
        # divide by square of norm
        
    return clips
        


def sample(arr, num):
    
    rand_order = np.random.permutation(arr.size)
    return arr[rand_order[:num]]


def extract_clips(data, times, clip_size=70, clip_offset=15):
    
    clips = np.zeros((times.size, clip_size,data.shape[1]))
    
    for i, t in enumerate(times):
        
        clips[i,:,:] = data[t-clip_offset:t-clip_offset+clip_size,:]
    
    
    return clips
