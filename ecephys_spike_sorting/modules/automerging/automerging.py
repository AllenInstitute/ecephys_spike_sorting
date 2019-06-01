import os
import pandas as pd
import numpy as np

from .metrics import compare_templates, make_interp_temp, compute_isi_score, compute_isi_score
from .merges import compute_overall_score, ID_merge_groups, make_merges
from ...common.spike_template_helpers import find_depth

def automerging(spike_times, spike_clusters, clusterIDs, cluster_quality, templates, params):

    min_t = np.min(spike_times)
    max_t = np.max(spike_times)

    depths = np.zeros((clusterIDs.size,))

    is_noise = np.ones(cluster_quality.shape, dtype=bool)
    is_noise[cluster_quality == 'noise'] = False

    for idx, clusterID in enumerate(clusterIDs):

        template = templates[clusterID,:,:]
        depths[idx] = find_depth(template)

        sorted_by_depth = np.argsort(depths)
        clusterIDs = clusterIDs[sorted_by_depth]
        depths = depths[sorted_by_depth]
        is_good = np.invert(is_noise[sorted_by_depth])

    comparison_matrix = np.zeros((depths.size, depths.size, 5))
        
    for i in range(0,depths.size):
        for j in range(i+1,depths.size):
            if np.abs(depths[i] - depths[j]) <= params['distance_to_compare'] and is_good[i] and is_good[j]:
                comparison_matrix[i,j,0] = 1
            
    print('Total comparisons: ' + str(np.where(comparison_matrix[:,:,0] == 1)[0].size))

    print('Calculating initial metrics...')

    max_time = np.max(spike_times)

    for i in range(0,depths.size):

        if is_good[i]:
            
            temp1 = make_interp_temp(templates,[clusterIDs[i]]) #
            times1 = spike_times[spike_clusters == clusterIDs[i]]
            
            for j in range(i+1,depths.size):
                
                if comparison_matrix[i,j,0] == 1:
                    
                    temp2 = make_interp_temp(templates, [clusterIDs[j]]) #
                    times2 = spike_times[spike_clusters == clusterIDs[j]]
                    
                    rms, offset_distance = compare_templates(temp1, temp2) #
                   # overlap = percent_overlap(times1, times2, min_t, max_t, 50) #
                    cISI_score, score_weight, ISI1, ISI2, cISI, rcISI, another_score = compute_isi_score(times1, times2, max_time)
                    is_good
                    comparison_matrix[i,j,1] = np.max(rms)
                    comparison_matrix[i,j,2] = another_score
                    comparison_matrix[i,j,3] = cISI_score

    overall_score, i_index, j_index = compute_overall_score(comparison_matrix)

    comparison_matrix[:,:,4] = 0

    for index in np.arange(overall_score.size)   :

        if overall_score[index] > params['merge_threshold']: 
            
            comparison_matrix[i_index[index],j_index[index],4] = 1


    print('Total merges = ' + str(np.where(comparison_matrix[:,:,4] == 1)[0].size))
    print(' ')

    groups = ID_merge_groups(comparison_matrix[:,:,4])
    clusters = np.copy(spike_clusters) 
    clusters = make_merges(groups, clusters, spike_clusters, clusterIDs) 

    print('  Total clusters = ' + str(np.unique(clusters).size))

    cluster_quality = []
    cluster_index = []

    for idx, ID in enumerate(np.unique(clusters)):

        cluster_index.append(ID)

        if ID > np.max(clusterIDs):
            cluster_quality.append(1) # good
        else:
            if is_good[np.where(clusterIDs == ID)[0]]:
                cluster_quality.append(1) # good
            else:
                cluster_quality.append(-1) # noise

    return clusters, cluster_index, cluster_quality