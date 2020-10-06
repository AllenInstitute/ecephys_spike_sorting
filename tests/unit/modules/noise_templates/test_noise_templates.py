import pytest
import numpy as np
import os

#from ecephys_spike_sorting.modules.noise_templates.id_noise_templates import id_noise_templates_rf
#import ecephys_spike_sorting.common.utils as utils

#DATA_DIR = os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

def test_noise_templates():

	sample_rate = 30000.0

	params = {}
	#params['classifier_path'] = os.path.join(DATA_DIR, 'classifier.pkl')

	#spike_times, spike_clusters, amplitudes, \
	# templates, channel_map, cluster_ids, cluster_quality \
	# = utils.load_kilosort_data(DATA_DIR, sample_rate, convert_to_seconds=True)

	#cluster_ids, is_noise = id_noise_templates_rf(spike_times, spike_clusters, cluster_ids, templates, params)

	#assert(len(cluster_ids) == len(is_noise))
