import pytest
import numpy as np
import os

#from ecephys_spike_sorting.modules.automerging.automerging import automerging
#import ecephys_spike_sorting.common.utils as utils

#DATA_DIR = os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

def test_automerging():

	sample_rate = 30000.0

	params = {}
	params['merge_threshold'] = 2.5
	params['distance_to_compare'] = 5

	pass

	#spike_times, spike_clusters, amplitudes, \
	# templates, channel_map, cluster_ids, cluster_quality \
	#= utils.load_kilosort_data(DATA_DIR, sample_rate, convert_to_seconds=True)

	#clusters, ids, labels = automerging(spike_times, spike_clusters, cluster_ids, cluster_quality, templates, params)

	#assert(len(ids) == len(labels))
