import os
import glob
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

base_directory = '/mnt/md0/data'

mice = ['392810', '405755', '448504', '407972', '444384']

def load(directory, file):
    return np.load(os.path.join(directory, file))

def read_template_ratings_file(filename):

    qualities = ['good','noise1','noise2','noise3','noise4','noise5']
    
    info = pd.read_csv(filename)
    cluster_ids = list(info['cluster_id'].values)
    cluster_quality = [qualities.index(x) for x in info['rating'].values]
    
    return cluster_ids, cluster_quality

original_features = np.zeros((15000, 61, 32))
labels = np.zeros((15000,))

unit_idx = 0

for mouse in mice:
    
    print(mouse)
    
    directory = os.path.join(base_directory, 'mouse' + mouse)
    
    probe_directories = glob.glob(directory + '/*probe*sorted')
    probe_directories.sort()
    
    for folder in probe_directories:
        
        subfolder = glob.glob(os.path.join(folder, 'continuous', 'Neuropix-*-100.0'))[0]
        
        templates_raw = load(subfolder,'templates.npy')
        unwhitening_mat = load(subfolder,'whitening_mat_inv.npy')
        cluster_ids, cluster_quality = read_template_ratings_file(os.path.join(subfolder, 'template_ratings_new.csv'))
        
        templates = np.zeros(templates_raw.shape)
        
        for temp_idx in range(templates.shape[0]):
            
            templates[temp_idx,:,:] = np.dot(np.ascontiguousarray(templates_raw[temp_idx,:,:]),np.ascontiguousarray(unwhitening_mat))
            
        peak_channels = np.argmin(np.min(templates,1),1)
        
        for idx, unit in enumerate(cluster_ids):
                    
            peak_channel = peak_channels[unit]

            min_chan = np.max([0,peak_channel-16])
            if min_chan == 0:
                max_chan = 32
            else:
                max_chan = np.min([templates.shape[2], peak_channel+16])
                if max_chan == templates.shape[2]:
                    min_chan = max_chan - 32
    
            sub_template = templates[unit, 21:, min_chan:max_chan]

            original_features[unit_idx,:,:] = sub_template
            labels[unit_idx] = cluster_quality[idx]
            unit_idx += 1
        
    print(probe_directories)
# %%
original_features = original_features[:unit_idx,:,:]
features = np.reshape(original_features[:,:,:], (original_features.shape[0], original_features.shape[1] * original_features.shape[2]), 2)
features = features[:,::4]
labels = labels[:unit_idx]

# %%

noise_templates = np.where(labels > 0)[0]
good_templates = np.where(labels == 0)[0]

order_noise = np.random.permutation(noise_templates.size)
order_good = np.random.permutation(good_templates.size)

# %%

# # # # # # # # # # # #

# These numbers are critical. The ratio of good units vs. noise units used in training
# determines the hit rate and false alarm rate.

n_train_noise = 300
n_train_good = 500
# # # # # # # # # # # #

x_train = np.concatenate((features[noise_templates[order_noise[:n_train_noise]],:], features[good_templates[order_good[:n_train_good]],:]))
y_train = np.concatenate((labels[noise_templates[order_noise[:n_train_noise]]], labels[good_templates[order_good[:n_train_good]]]))

x_test = np.concatenate((features[noise_templates[order_noise[n_train_noise:]],:], features[good_templates[order_good[n_train_good:]],:]))
y_test = np.concatenate((labels[noise_templates[order_noise[n_train_noise:]]], labels[good_templates[order_good[n_train_good:]]]))

# %%

from sklearn.ensemble import RandomForestClassifier

clf = RandomForestClassifier(n_estimators=50, max_depth=50, random_state=10, bootstrap = False, warm_start=True, criterion='entropy', class_weight={0 : 0.01, 1: 1})

clf.n_estimators = 50
clf.fit(x_train, y_train)

predicted_labels = clf.predict(x_test)

hits = np.sum((predicted_labels == 0) * (y_test == 0)) / np.sum(y_test == 0)
fp = np.sum((predicted_labels == 0) * (y_test > 0)) / np.sum(y_test > 0)

confusion_matrix = np.zeros((5,5))

for i in range(5):
    for j in range(5):
        confusion_matrix[i,j] = np.sum((predicted_labels == i) * (y_test == j)) / np.sum(y_test == j)

overall = np.sum(((predicted_labels == 0) * (y_test == 0)) + ((predicted_labels > 0) * (y_test > 0))) / len(y_test)

print('Hit rate: ' + str(hits))
print('FP rate: ' + str(fp))
print('Overall rate: ' + str(overall))

plt.figure(14111)
plt.clf()

plt.imshow(confusion_matrix)

# %%