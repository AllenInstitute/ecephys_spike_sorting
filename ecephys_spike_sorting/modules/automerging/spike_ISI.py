import numpy as np
import matplotlib.pyplot as plt
import scipy as scipy
from scipy.signal import convolve
import collections

def find_ISI(spike_times1):
    #spike_times = template_times_list[template_ID]
    intervals = np.diff(spike_times1)
    return intervals

def find_cISI(spike_times1, spike_times2, max_time):
    insert_spikes1 = np.searchsorted(spike_times1,spike_times2,side = 'right')
    insert_spikes2 = np.searchsorted(spike_times2,spike_times1,side = 'right')
    spike_times1end = np.concatenate(([0],spike_times1,[max_time]))
    spike_times2end = np.concatenate(([0],spike_times2,[max_time])) 
    intervals1 = np.concatenate((spike_times1end[insert_spikes1+1]-spike_times2,spike_times2-spike_times1end[insert_spikes1]))
    intervals2 = np.concatenate((spike_times2end[insert_spikes2+1]-spike_times1,spike_times1-spike_times2end[insert_spikes2]))
    intervals = np.hstack((intervals1,intervals2)) # np.diff(np.sort(np.concatenate((spike_times1, spike_times2)))) 
    return intervals

def reverse_spikes(spike_times, max_time, num_bins = 100):
    reverse_times = np.zeros(np.prod(spike_times.shape))
    bin_size = max_time/100
    for i in range(num_bins):
        time_min = i*bin_size
        time_max = (i+1)*bin_size
        spikes_in_bin = np.flatnonzero(np.logical_and(spike_times>=time_min, spike_times<=time_max))
        reverse_times[spikes_in_bin] = np.sort(time_max-spike_times[spikes_in_bin]+time_min)
        #####TODO Fix this. I think we need to re index after the flat nonzero
    return reverse_times   

def find_rcISI(spike_times1,spike_times2, max_time):
    reverse_times1 = reverse_spikes(spike_times1, max_time)
    reverse_times2 = reverse_spikes(spike_times2, max_time)
    intervals1 = find_cISI(spike_times1,reverse_times2, max_time)
    intervals2 = find_cISI(spike_times2,reverse_times1, max_time)
    intervals = np.hstack((intervals1,intervals2))
    #a = np.concatenate((spike_times1, spike_times2))
    
    #intervals = np.diff(np.sort(-a) + np.max(a))
    
    return intervals

#%%
def ISI_mode(template_ID):
    #print(template_ID)
    ISI_dist = ISI_list[template_ID]
    mode = interval_dist_mode(ISI_dist)
    return mode

def interval_dist_mode(interval_dist):
    try:
        mode_window = min(500,np.int(np.nan_to_num(np.median(interval_dist))))
        values,num_in_window = smooth_ISI(interval_dist, mode_window)
        mode = np.min(np.nonzero(values>.9*np.max(values))) #perhaps double this
    except ValueError:
        mode = 0
    return mode
"""
def find_window(interval_dist):
    mode = dist_mode(interval_dist)
    xmax = mode*1.25
    return xmax

def compare_interval_distributions(dist1,dist2,xmax):
    xmin = 0
    N1 = np.prod(np.shape(np.nonzero(dist1<xmax)))
    N2 = np.prod(np.shape(np.nonzero(dist2<xmax)))
    num_bins = np.floor(np.sqrt(np.min((N1,N2))))
    height1,bins1 = np.histogram(dist1,bins = num_bins,range = (xmin,xmax))
    height2,bins2 = np.histogram(dist2,bins = num_bins,range = (xmin,xmax))
    norm_height1 = height1.astype(float)/N1
    norm_height2 = height2.astype(float)/N2
    adjusted_height1 = norm_height1-np.max(norm_height1)/2
    adjusted_height2 = norm_height2-np.max(norm_height2)/2                                     
    perfect_score1 = np.dot(adjusted_height1,adjusted_height1)
    perfect_score2 = np.dot(adjusted_height2,adjusted_height2)
    perfect_score = np.max((perfect_score1,perfect_score2))
    actual_score = np.dot(adjusted_height1,adjusted_height2)
    percentage_score = actual_score/perfect_score
    return percentage_score

def find_dist_similarity(dist1,dist2):
    xmax = np.max((find_window(dist1),find_window(dist2)))*1.5
    ISI_similarity_score = compare_interval_distributions(dist1,dist2,xmax) 
    return ISI_similarity_score   
"""    
#%%

def make_ISI_list(times_list):
    ISI_list = []
    for i in range(len(times_list)):
        ISI = find_ISI(times_list[i])
        ISI_list.append(ISI)
    return ISI_list

def compare_ISI(clusterID1,clusterID2):
    window = max((mode_list[clusterID1],mode_list[clusterID2]))
    window = max((100,min((window,400))))
    window = np.int(1.25*window)
    if window>0:
        smoothISI1 = smooth_ISI(ISI_list[clusterID1],window)
        smoothISI2 = smooth_ISI(ISI_list[clusterID2],window)
        norm_smoothISI1 = normalize_smoothed_ISI(smoothISI1)
        norm_smoothISI2 = normalize_smoothed_ISI(smoothISI2)
        dot12 = np.dot(norm_smoothISI1,norm_smoothISI2)
        dot1_self = np.dot(norm_smoothISI1,norm_smoothISI1)
        dot2_self = np.dot(norm_smoothISI2,norm_smoothISI2)
        ISI_sim_score = dot12/np.max((dot1_self,dot2_self))
    else: ISI_sim_score = 0
    return ISI_sim_score

def make_ISI_sim_matrix(ISI_list):
    ISI_sim_matrix = np.zeros([len(ISI_list),len(ISI_list)])
    for i in range(len(ISI_list)):
        #ISI_sim_matrix[i,i] = 0 - could set this to a metric of absolute ISI quality?
        for j in range(i+1,len(ISI_list)):
            if comparison_matrix[i,j]>0:
                print('calculating ISI sim for',i,j)
                ISI_sim = compare_ISI(i,j)
                ISI_sim_matrix[i,j] = ISI_sim
                ISI_sim_matrix[j,i] = ISI_sim 
    return ISI_sim_matrix
#%%
def smooth_ISI(ISI,window):
    gaussian_window = 4*window/np.sqrt(max((1,np.size(np.nonzero(ISI<window)))))
    gaussian_std = gaussian_window/6
    box_filter_size = np.floor((gaussian_std*.75*np.sqrt(2*np.pi)+.5))//2*2+1
    kernel = np.ones(np.int(box_filter_size))/box_filter_size
    values,bins = np.histogram(ISI,window,range = (0,window))
    num_in_window = sum(values)
    #print("Num in window:",sum(values))
    for i in range(3):
        smoothed_ISI = scipy.signal.correlate(values,kernel,'same')
        #Think about using fft to convolve?
    return smoothed_ISI, num_in_window

def normalize_smoothed_ISI(smoothedISI):
    """
    avg = np.average(smoothedISI)
    norm_smoothISI = smoothedISI-avg
    norm = np.linalg.norm(norm_smoothISI)
    unitnorm_smoothISI = norm_smoothISI/norm\
    """
    total = np.sum(smoothedISI)
    if total > 0:
        smoothedISI = smoothedISI/total
    avg = np.average(smoothedISI)
    norm_smoothISI = smoothedISI - avg
    return norm_smoothISI

def compare_cISI(ISI1, cISI, rcISI, window):
    if window>0:
        window = max((100,min((window,400))))
        window = np.int(1.25*window)

        smoothISI1, num1 = smooth_ISI(ISI1,window)
        smoothcISI, numc = smooth_ISI(cISI,window)
        smoothrcISI, numrc = smooth_ISI(rcISI,window)
        norm_smoothISI1 = normalize_smoothed_ISI(smoothISI1)
        norm_smoothcISI = normalize_smoothed_ISI(smoothcISI)
        norm_smoothrcISI = normalize_smoothed_ISI(smoothrcISI)
        dotc_1 = np.dot(norm_smoothISI1,norm_smoothcISI)
        dotr_1 = np.dot(norm_smoothISI1,norm_smoothrcISI)
        dot1_self = np.dot(norm_smoothISI1,norm_smoothISI1)
        dotc_self = np.dot(norm_smoothcISI,norm_smoothcISI)
        dotrc_self= np.dot(norm_smoothrcISI,norm_smoothrcISI)
        simc_1 = dotc_1/np.max((dot1_self,dotc_self))
        simr_1 = np.max((0,dotr_1/np.max((dot1_self,dotrc_self))))
        score = (simc_1 - simr_1)/(1-simr_1)
    else: 
        score = 0 
        num1 = 0
        numc = 0
    return score, num1, numc

def find_cISI_score(spike_times1, spike_times2, max_time):
    
    ISI1 = find_ISI(spike_times1)
    ISI2 = find_ISI(spike_times2)
    cISI = find_cISI(spike_times1, spike_times2, max_time)
    rcISI = find_rcISI(spike_times1, spike_times2, max_time)

    sim_1, num1, numc1 = compare_cISI(ISI1, cISI, rcISI, interval_dist_mode(ISI1))
    sim_2, num2, numc2 = compare_cISI(ISI2, cISI, rcISI, interval_dist_mode(ISI2))

    weight1 = np.min((1,num1/1000.)) #These will be changed to account for drastically different rates
    weight2 = np.min((1,num2/1000.)) #placing more value on the similarity to the cluster with a higher max rate
    rel_weight1 =  weight1/(weight1+weight2+.000001)   
    rel_weight2 = weight2/(weight1+weight2+.000001)
    min_weight = min((rel_weight1,rel_weight2))
    balanced = min_weight/.5
    min_score = min((sim_1,sim_2))
    rel_score = sim_1*rel_weight1+sim_2*rel_weight2 
    cISI_score = min_score*balanced+rel_score*(1-balanced)
    score_weight = np.min((1,(numc1+numc2)/200.))
 
    isi1 = normalize_smoothed_ISI(smooth_ISI(ISI1, window=1000)[0])
    isi2 = normalize_smoothed_ISI(smooth_ISI(ISI2, window=1000)[0])
    cisi = normalize_smoothed_ISI(smooth_ISI(cISI, window=1000)[0])
    rcisi = normalize_smoothed_ISI(smooth_ISI(rcISI, window=1000)[0])
    
    return cISI_score, score_weight, isi1, isi2, cisi, rcisi
    
def find_cISI_score_matrix(ISI_list, times_list):
    cISI_score_matrix = np.zeros([len(times_list),len(times_list)])
    cISI_score_weight_matrix = np.zeros([len(times_list),len(times_list)])
    for i in range(len(times_list)):
        for j in range(i+1,len(times_list)):
            if comparison_matrix[i,j]>0: 
                print('calculating cISI score for',i,j)
                cISI_score, score_weight = find_cISI_score(i,j)
                cISI_score_matrix[i,j] = cISI_score
                cISI_score_matrix[j,i] = cISI_score 
                cISI_score_weight_matrix[i,j] = score_weight
                cISI_score_weight_matrix[j,i] = score_weight 
    return cISI_score_matrix, cISI_score_weight_matrix


#%%
#visualization help
def compare(ID1, ID2):
    i=ID1
    j=ID2
    ISIi, numi = smooth_ISI(ISI_list[i],1000)
    ISIj, numj = smooth_ISI(ISI_list[j],1000)
    cISI = find_cISI(template_times_list[i],template_times_list[j])
    cISI, numc = smooth_ISI(cISI,1000)
    rcISI = find_rcISI(template_times_list[i],template_times_list[j])
    rcISI, numr = smooth_ISI(rcISI,1000)
    plt.figure(1)
    plt.subplot(221)
    plt.plot(ISIi)
    plt.subplot(222)
    plt.plot(ISIj)
    plt.subplot(223)
    plt.plot(cISI)
    plt.subplot(224)
    plt.plot(rcISI)
    plt.show()
    cISI_score = find_cISI_score(ID1,ID2)
    print("cISI_score:",cISI_score)
    return



def remove_outliers(dist,reps=3):
    for j in range(reps):
        int_max = np.mean(dist)+3*np.std(dist)
        mask = np.nonzero(dist>int_max)
        clean_dist=np.delete(dist, mask)
        return clean_dist

def hist(data):
    data = remove_outliers(data,3)
    #num_bins = np.floor(np.sqrt(N))
    xmin = 0
    xmax = 3000/5/6
    N = np.prod(np.shape(np.nonzero(data<xmax)))
    num_bins = np.floor(np.sqrt(N))
    #bin_size = xmax/30*.5
    #num_bins = int(np.floor(xmax/bin_size))
    n, bins, patches = plt.hist(data, bins = num_bins, range = (xmin,xmax))
    plt.show()
    return n, bins, patches 