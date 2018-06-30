import pytest
import numpy as np
import os

from ecephys_spike_sorting.modules.noise_templates.id_noise_templates import id_noise_templates
import ecephys_spike_sorting.common.utils as utils

os.environ['ECEPHYS_SPIKE_SORTING_DATA'] = r'C:\Users\svc_neuropix\Documents\GitHub\ecephys_spike_sorting\cached_data'

DATA_DIR = os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

def test_extract_waveforms():

	sample_rate = 30000.0

	params = {}
	params['std_thresh'] = 2.5
	params['waveform_spread'] = 10
	params['thresh2'] = 0.2
	params['min_peak_sample'] = 10
	params['min_trough_sample'] = 10
	params['contamination_ratio'] = 0.01
	params['min_height'] = -5

	spike_times, spike_clusters, amplitudes, \
	 templates, channel_map, cluster_ids, cluster_quality \
	 = utils.load_kilosort_data(DATA_DIR, sample_rate, convert_to_seconds=True)
	
	cluster_ids, is_noise = id_noise_templates(spike_times, spike_clusters, cluster_ids, templates, params)

	assert(len(cluster_ids) == len(is_noise))