#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 14:01:40 2018

@author: joshs
"""

import os
import glob
import numpy as np

import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier

base_directory = '/mnt/md0/data'

mice = ('386467', '386129', '386130')

def load(directory, file):
    return np.load(os.path.join(directory, file))

def read_cluster_group_tsv(filename):

    info = np.genfromtxt(filename, dtype='str')
    cluster_ids = info[1:,0].astype('int')
    cluster_quality = info[1:,1]
    
    return cluster_ids, cluster_quality

convert_to_seconds = True

features = np.zeros((10000, 61))
labels = np.zeros((10000,))

unit_idx = 0

for mouse in mice:
    
    directory = os.path.join(base_directory, 'mouse' + mouse)
    
    probe_directories = glob.glob(directory + '/probe*')
    
    for folder in probe_directories:
        
        print(folder)
        
        spike_times = load(folder,'spike_times.npy')
        spike_clusters = load(folder,'spike_clusters.npy')
        amplitudes = load(folder,'amplitudes.npy')
        templates_raw = load(folder,'templates.npy')
        unwhitening_mat = load(folder,'whitening_mat_inv.npy')
        channel_map = np.squeeze(load(folder, 'channel_map.npy'))
        channel_positions = load(folder, 'channel_positions.npy')
                    
        templates_raw = templates_raw[:,21:,:] # remove zeros
        spike_clusters = np.squeeze(spike_clusters) # fix dimensions
        spike_times = np.squeeze(spike_times)# fix dimensions
        if convert_to_seconds:
           spike_times = spike_times / 30000 # convert to seconds
                        
        templates = np.zeros((templates_raw.shape))
        
        cluster_ids = np.unique(spike_clusters)
        
        for temp_idx in range(templates.shape[0]):
            
            templates[temp_idx,:,:] = np.dot(np.ascontiguousarray(templates_raw[temp_idx,:,:]),np.ascontiguousarray(unwhitening_mat))
            
        new_cluster_ids, cluster_quality = read_cluster_group_tsv(os.path.join(folder, 'cluster_group.tsv'))
        
        is_noise = new_cluster_ids[cluster_quality == 'noise']
        
        manual_labels = np.zeros((cluster_ids.shape))
        manual_labels[is_noise] = 1
        
        for idx, unit in enumerate(cluster_ids):
                    
            template = templates[unit,:,:]
            depth = find_depth(template)
            features[unit_idx,:] = template[:,depth]
            
            labels[unit_idx] = manual_labels[unit]
            unit_idx += 1
    
    print(probe_directories)
# %%
    
features = features[:unit_idx,:]
labels = labels[:unit_idx]
    
# %%
    
def find_depth(template):
    
    return np.argmax(np.max(template,0)-np.min(template,0))

    # %%
    
train_size = 2000 #int(6*labels.size/8)

order = np.random.permutation(labels.size)

feat_train = features[order[:train_size],:]
label_train = labels[order[:train_size]]

feat_test = features[order[train_size:],:]
label_test = labels[order[train_size:]]

clf = RandomForestClassifier(n_estimators=10, max_depth=4, random_state=10)
clf.fit(feat_train, label_train)

predicted_labels = clf.predict(feat_test)

a = np.where(predicted_labels == label_test)[0]

plt.figure(99)
plt.clf()

for i in range(0,200):
    if label_train[i] == 0:
        plt.subplot(2,2,1)
    else:
        plt.subplot(2,2,2)
        
    plt.plot(feat_train[i,:],'k',alpha=0.2)
    
for i in range(0,200):
    if predicted_labels[i] == 0:
        plt.subplot(2,2,3)
    else:
        plt.subplot(2,2,4)
        
    plt.plot(feat_test[i,:],'k',alpha=0.2)

accuracy = int(len(a) / len(label_test) * 100)

plt.subplot(2,2,4)
plt.title(str(accuracy) + '% classification accuracy')
    
    # %%
    
plt.figure(100)
plt.clf()
plt.plot(clf.feature_importances_)

