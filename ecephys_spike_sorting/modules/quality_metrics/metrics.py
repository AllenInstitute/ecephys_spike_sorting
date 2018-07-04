import numpy as np
import pandas as pd
from sklearn import decomposition, neighbors
from collections import OrderedDict

from ecephys_spike_sorting.common.spike_template_helpers import find_depth

def calculate_metrics(data, spike_times, spike_clusters, amplitudes, sample_rate, params):

	#iso = calculate_isolation_quality(data, spike_times, spike_clusters)
	#noise_o = calculate_noise_overlap(data, spike_times, spike_clusters)
	print("Calculating SNR")
	snr, peak_chan = calculate_snr_and_peak_chan(data, spike_times.astype('int64'), spike_clusters, params['snr_spike_count'], params['samples_per_spike'], params['pre_samples'])
	print("Calculating isi violations")
	isi_viol = calculate_isi_violations(spike_times / sample_rate, spike_clusters, params['isi_threshold'])
	print("Calculating firing rate")
	firing_rate = calculate_firing_rate(spike_times / sample_rate, spike_clusters)

	cluster_ids = np.unique(spike_clusters)

	# package it into a DataFrame called metrics
	metrics = pd.DataFrame(data= OrderedDict((('cluster_ids', cluster_ids), 
		                    ('peak_chan' , peak_chan),
		                    ('snr' , snr),
		                    ('firing_rate' , firing_rate),
		                    ('isi_viol' , isi_viol))))

	return metrics 

def calculate_isolation_quality(spike_times, spike_clusters, rawDataFile):

	# code goes here

	pass


def calculate_noise_overlap(spike_times, spike_clusters, rawDataFile):

	# code goes here

	pass


def calculate_isi_violations(spike_times, spike_clusters, isi_threshold):

	cluster_ids = np.unique(spike_clusters)

	viol_rate = np.zeros(cluster_ids.shape)

	for idx, cluster_id in enumerate(cluster_ids):
		for_this_cluster = (spike_clusters == cluster_id)
		viol_rate[idx], num_violations = isi_violations(spike_times[for_this_cluster], isi_threshold=isi_threshold)

	return viol_rate


def calculate_snr_and_peak_chan(data, spike_times, spike_clusters, spike_count, samples_per_spike, pre_samples):

	cluster_ids = np.unique(spike_clusters)

	snrs = np.empty(cluster_ids.shape, dtype='float64')
	peak_chans = np.empty(cluster_ids.shape, dtype='int32')

	snrs[:] = np.nan
	peak_chans[:] = np.nan

	for idx, cluster_id in enumerate(cluster_ids):

		for_this_cluster = (spike_clusters == cluster_id)
		times = spike_times[for_this_cluster]
		np.random.shuffle(times)
		total_waveforms = np.min([spike_count, times.size])
		times_for_snr = times[:total_waveforms]
		waveforms = extract_clips(data, times_for_snr, samples_per_spike, pre_samples)

		if waveforms is not None:
			
			mean_waveform = np.nanmean(waveforms, 0)

			if len(mean_waveform.shape) == 2:

				# subtract offset
				for channel in range(0, mean_waveform.shape[1]):
					mean_waveform[:, channel] = \
					mean_waveform[:,channel] - mean_waveform[0, channel]
	            
				peak_chans[idx] = find_depth(mean_waveform)

				snrs[idx] = snr(waveforms[:,:,peak_chans[idx]])


	return snrs, peak_chans


def calculate_firing_rate(spike_times, spike_clusters):

	cluster_ids = np.unique(spike_clusters)

	firing_rates = np.zeros(cluster_ids.shape)

	for idx, cluster_id in enumerate(cluster_ids):
		for_this_cluster = (spike_clusters == cluster_id)
		firing_rates[idx] = firing_rate(spike_times[for_this_cluster])

	return firing_rates


def calculate_depths(spike_times, spike_clusters):

	cluster_ids = np.unique(spike_clusters)

	firing_rates = np.zeros(cluster_ids.shape)

	for idx, cluster_id in enumerate(cluster_ids):
		for_this_cluster = (spike_clusters == cluster_id)
		firing_rates[idx] = firing_rate(spike_times[for_this_cluster])

	return depths


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
        
       # count 'em up
        
    return 1 - (num_correct / num_total)
    
    
def compute_noise_shape(data, mean_clip):
    
    # something about weighting
    pass


def regress_out_noise_shape(clips, shape):
    
    norm = np.linalg.norm(shape)
    
    for i in range(clips.shape[0]):
        clips[i,:] = np.dot(clips[i,:], shape)
        # divide by square of norm
        
    return clips
        


def sample(arr, num):
    
    rand_order = np.random.permutation(arr.size)
    return arr[rand_order[:num]]


def extract_clips(data, times, clip_size=82, clip_offset=20):
    
	if times.size > 1:
	    
		clips = np.zeros((times.size, clip_size, data.shape[1]))
	    
		for i, t in enumerate(times):
	        
			try:
				clips[i,:,:] = data[int(t-clip_offset):int(t-clip_offset+clip_size),:]
			except (ValueError, TypeError) as e:
				clips[i,:,:] = np.nan
	    
	elif times.size == 1:

		clips = data[int(times[0])-clip_offset:int(times[0])-clip_offset+clip_size,:]

	else:

		clips = None

	return clips



def firing_rate(spike_train, min_time = None, max_time = None):
	"""Calculate firing rate for a spike train.

	If no temporal bounds are specified, the first and last spike time are used.

    Inputs:
    -------
	spike_train : array of spike times
	min_time : time of first possible spike (optional)
	max_time : time of last possible spike (optional)

	Outputs:
	--------
	fr : firing rate in Hz

	"""

	if min_time is not None and max_time is not None:
		duration = max_time - min_time
	else:
		duration = np.max(spike_train) - np.min(spike_train)

	fr = spike_train.size / duration

	return fr


def isi_violations(spike_train, isi_threshold, min_isi=0):
	"""Calculate ISI violations for a spike train.

    modified by Dan Denman from cortex-lab/sortingQuality GitHub by Nick Steinmetz

    Inputs:
    -------
	spike_train : array of spike times
	isi_threshold : threshold for isi violation
	min_isi :

	Outputs:
	--------
	fpRate : rate of isi violations as a fraction of overall rate
	num_violations : total number of violations

	"""

	isis = np.diff(spike_train)
	num_spikes = len(spike_train)
	num_violations = sum(isis < isi_threshold) 
	violation_time = 2*num_spikes*(isi_threshold - min_isi)
	total_rate = firing_rate(spike_train)
	violation_rate = num_violations/violation_time
	fpRate = violation_rate/total_rate

	#assert(fpRate < 1.0) # it is nonsense to have a rate > 1; a rate > 1 means the assumputions of this analysis are failing

	return fpRate, num_violations


def snr(W):
	"""Calculate SNR of spike waveforms.

	based on Xiaoxuan's Matlab code. 

	ref: (Nordhausen et al., 1996; Suner et al., 2005)

	Input:
	-------
	W : array of N waveforms (N x samples)

	Output:
	snr : signal-to-noise ratio for unit (scalar)

	"""

	W_bar = np.nanmean(W,axis=0)
	A = np.max(W_bar) - np.min(W_bar)
	e = W - np.tile(W_bar,(np.shape(W)[0],1))
	snr = A/(2*np.nanstd(e.flatten()))

	return snr   
