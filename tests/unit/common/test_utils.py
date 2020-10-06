import pytest
import numpy as np
import os

#import ecephys_spike_sorting.common.utils as utils

#DATA_DIR = os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

def test_read_cluster_group_tsv():

	pass

	#filename = os.path.join(DATA_DIR, 'cluster_group.tsv')

	#cluster_ids, cluster_quality = utils.read_cluster_group_tsv(filename)

	#assert(len(cluster_ids) == len(cluster_quality))

def test_load_kilosort_data():

	pass

	#spike_times, spike_clusters, amplitudes, \
	# templates, channel_map, cluster_ids, cluster_quality \
	# = utils.load_kilosort_data(DATA_DIR, 30000.0)

	#assert(len(cluster_ids) == len(cluster_quality))
	#assert(len(amplitudes) == len(spike_times))

def test_read_probe_json():

	pass

	#filename = os.path.join(DATA_DIR, 'probe_info.json')

	#mask, offset, scaling, surface_channel, air_channel = utils.read_probe_json(filename)

	#assert(len(mask) == len(scaling))

def test_rms():

	pass

	#data = np.array([1, -1, 1, -1, 1])

	#output = utils.rms(data)

	#assert(output == 1.0)

def test_find_range():

	pass

	#data = np.arange(0,100)

	#output = utils.find_range(data, 20, 30)

	#assert(np.array_equal(output, np.arange(20,31)))
