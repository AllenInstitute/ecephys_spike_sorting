import pytest
import numpy as np
import os

#from ecephys_spike_sorting.modules.quality_metrics.metrics import calculate_metrics
#import ecephys_spike_sorting.common.utils as utils

#DATA_DIR = os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

def te_st_quality_metrics():

	sample_rate = 30000.0
	numChannels = 384
	bit_volts = 0.195

	params = {}
	params['samples_per_spike'] = 82
	params['pre_samples'] = 20
	params['snr_spike_count'] = 500
	params['isi_threshold'] = 0.015

	pass

	#raw_data_file = os.path.join(DATA_DIR, 'continuous_ap_post.dat')
	#rawData = np.memmap(raw_data_file, dtype='int16', mode='r')
	#data = np.reshape(rawData, (int(rawData.size/384), 384))

	#spike_times, spike_clusters, amplitudes, \
	 #templates, channel_map, cluster_ids, cluster_quality \
	#= utils.load_kilosort_data(DATA_DIR, sample_rate, False)

	#metrics = calculate_metrics(data, spike_times, spike_clusters, amplitudes, sample_rate, params)

	#print(metrics)

if __name__ == "__main__":
    #test_quality_metrics()
    pass
