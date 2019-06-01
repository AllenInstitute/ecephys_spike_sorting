import numpy as np
        

def constrainValues(input_array):
    
    output_array = np.copy(input_array)
    output_array[np.isinf(input_array)] = 0
    output_array[np.isnan(input_array)] = 0
    output_array[input_array > 1] = 0
    output_array[input_array < 0] = 0
    
    return output_array

def getNextMerge(comparison_matrix):
    
    overall_score, i_index, j_index = compute_overall_score(comparison_matrix)
    
    nextMerge = np.argmax(overall_score)
    mergeScore = np.max(overall_score)
    
    i = i_index[nextMerge]
    j = j_index[nextMerge]
    
    return mergeScore, i, j, overall_score

def compute_overall_score(comparison_matrix):
    
    num_units = comparison_matrix.shape[0]
    
    index_matrix = np.zeros((num_units,num_units,2),dtype='int')
                
    for i in range(0,num_units):
        for j in range(i+1,num_units):
            index_matrix[i,j,0] = i
            index_matrix[i,j,1] = j
    
    selection = comparison_matrix[:,:,0].flatten() == 1
    waveform_sim = comparison_matrix[:,:,1].flatten()
    isi_sim = comparison_matrix[:,:,3].flatten()
    isi_score = 1 - comparison_matrix[:,:,2].flatten()
    i_index = index_matrix[:,:,0].flatten()
    j_index = index_matrix[:,:,1].flatten()

    overall_score = constrainValues(isi_score) + constrainValues(isi_sim) + constrainValues(waveform_sim)
    
    return overall_score[selection], i_index[selection], j_index[selection]
    
def getTemplateIndsForCluster(spike_templates, spike_clusters, clusterId, templateIDs):
    
    templatesForCluster = np.unique(spike_templates[spike_clusters == clusterId])
    
    tempInds = np.zeros((templateIDs.size,))
    
    for ID in templatesForCluster:
        
        tempInds = tempInds + (templateIDs == ID)
    
    return np.squeeze(np.argwhere(tempInds))

# %%

# decision for whether or not to merge, based on waveform similarity and isi similarity scores:

def should_merge(waveform_similarity, isi_similarity, isi_score, t1 = 0.2, t2 =0.75, t3 =0.5, t4=0.9, t5 = 0.9):

    if not np.isnan(isi_score) and not np.isinf(isi_score) and isi_score < t1 and isi_score > 0.001:
        
       if not np.isnan(isi_similarity): 
           
           return isi_similarity >= 0.9 - pow(waveform_similarity*1.1, np.e)
    
    return False
    

# identify the merge groups
                
def ID_merge_groups(merges):    
    
    connected_groups = []
        
    for u1 in range(0,merges.shape[0]):
        
        for u2 in range(0, merges.shape[0]):
            
            if merges[u1,u2] == 1 and u1 != u2:
                
                if len(connected_groups) == 0: # initialize merge groups
                    
                    connected_groups.append([u1, u2])
                    
                else:
                    
                    foundMatch = False
                    
                    for idx, group in enumerate(connected_groups):
                        
                        if u1 in group or u2 in group:

                            if u1 not in group:
                                group.extend([u1])
                            if u2 not in group:
                                group.extend([u2])
                            
                            foundMatch = True
                            
                        
                    if not foundMatch:
                         connected_groups.append([u1,u2])
                            
                    # check for overlapping groups
                    if True:
                        for idx, group1 in enumerate(connected_groups):
                            
                            for idx2, group2 in enumerate(connected_groups):
                                
                                L = len(set(group1).intersection(group2))
                                
                                if L > 0 and idx != idx2:

                                    connected_groups[idx] = list(np.sort(group1 + list(set(group2) - set(group1))))
                                    connected_groups[idx2] = []
                                
    connected_groups[:] = [item for item in connected_groups if item != []] # remove empty elements
                                
    return connected_groups


# make the merges
def make_merges(connected_groups, spike_clusters, spike_templates, templateIDs):
        
    maxId = np.max(spike_clusters)
    
    for merge_group in connected_groups:
        
        maxId += 1
        
        for unit_idx in merge_group:

            spike_clusters[np.where(spike_templates == templateIDs[unit_idx])[0]] = maxId
            
    return spike_clusters
