#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 11 17:09:07 2018

@author: joshs
"""

spike_times = np.load(folder + '/spike_times.npy')
spike_templates = np.load(folder + '/spike_templates.npy')
amplitudes = np.load(folder + '/amplitudes.npy')
templates = np.load(folder + '/templates.npy')
unwhitening_mat = np.load(folder + '/whitening_mat_inv.npy')

templates = templates[:,21:,:] # remove zeros
spike_templates = np.squeeze(spike_templates) # fix dimensions
spike_times = np.squeeze(spike_times) # convert to seconds
min_t = np.min(spike_times)
max_t = np.max(spike_times)

# %%
# step 0: un-whiten the templates

unwhitened_temps = np.zeros((templates.shape))

for temp_idx in range(templates.shape[0]):

unwhitened_temps[temp_idx,:,:] = np.dot(np.ascontiguousarray(templates[temp_idx,:,:]),np.ascontiguousarray(unwhitening_mat))

# step 1: figure out which units to compare, based on distance, while ignoring noise templates

# LOTS OF HARD-CODED PARAMETERS IN HERE:
templateIDs, is_noise = id_noise_templates(spike_templates, unwhitened_temps, spike_times)

depths = np.zeros((templateIDs.size,))

for idx, templateID in enumerate(templateIDs):

template = unwhitened_temps[templateID,:,:]
depths[idx] = int(find_depth(template))

sorted_by_depth = np.argsort(depths)
templateIDs = templateIDs[sorted_by_depth]
depths = depths[sorted_by_depth]
is_good = np.invert(is_noise[sorted_by_depth])

comparison_matrix = np.zeros((depths.size, depths.size, 5))
    
for i in range(0,depths.size):
for j in range(i+1,depths.size):
    if np.abs(depths[i] - depths[j]) <= distance_to_compare and is_good[i] and is_good[j]:
        comparison_matrix[i,j,0] = 1
        
print('Total comparisons: ' + str(np.where(comparison_matrix[:,:,0] == 1)[0].size))

# %%
# first pass

print('Calculating initial metrics...')

max_time = np.max(spike_times)

for i in range(0,depths.size):

if is_good[i]:
    
    #print("unit " + str(i))
    
    temp1 = make_interp_temp(unwhitened_temps,[templateIDs[i]]) #
    times1 = spike_times[spike_templates == templateIDs[i]]
    
    for j in range(i+1,depths.size):
        
        if comparison_matrix[i,j,0] == 1:
            
            temp2 = make_interp_temp(unwhitened_temps, [templateIDs[j]]) #
            times2 = spike_times[spike_templates == templateIDs[j]]
            
            rms, offset_distance = compare_templates(temp1, temp2) #
           # overlap = percent_overlap(times1, times2, min_t, max_t, 50) #
            cISI_score, score_weight, ISI1, ISI2, cISI, rcISI, another_score = compute_isi_score(times1, times2, max_time)
            is_good
            comparison_matrix[i,j,1] = np.max(rms)
            comparison_matrix[i,j,2] = another_score
            comparison_matrix[i,j,3] = cISI_score

# %%
overall_score, i_index, j_index = compute_overall_score(comparison_matrix)

comparison_matrix[:,:,4] = 0

for index in np.arange(overall_score.size)   :

if overall_score[index] > merge_threshold: 
    
    comparison_matrix[i_index[index],j_index[index],4] = 1


# %%

print('Total merges = ' + str(np.where(comparison_matrix[:,:,4] == 1)[0].size))
print(' ')

groups = ID_merge_groups(comparison_matrix[:,:,4])

if False: # check for extra large groups
lengths = np.zeros((len(groups),))

for idx,group in enumerate(groups):
    if len(group) > 20:
        indices = np.array(group)
        reduced_matrix = comparison_matrix[indices,:,:]
        rm2 = reduced_matrix[:,indices,:]
        plt.figure(2)
        plt.clf()
        plt.imshow(rm2[:,:,4],vmin=0,vmax=0.4)
    lengths[idx] = len(group)
    
clusters = np.copy(spike_templates) 
clusters = make_merges(groups, clusters, spike_templates, templateIDs) 

print('  Total clusters = ' + str(np.unique(clusters).size))

# %%

# save files

cluster_quality = []
cluster_index = []

for idx, ID in enumerate(np.unique(clusters)):

cluster_index.append(ID)

if ID > np.max(templateIDs):
    cluster_quality.append('good')
else:
    if is_good[np.where(templateIDs == ID)[0]]:
        cluster_quality.append('good')
    else:
        cluster_quality.append('noise')
   
df = pd.DataFrame(data={'cluster_id' : cluster_index, 'group': cluster_quality})

print('Saving data...')

df.to_csv(folder + '/cluster_group_new.tsv', sep='\t', index=False)
np.save(folder + '/spike_clusters_new.npy', clusters)
np.save(folder + '/comparison_matrix.npy', comparison_matrix)