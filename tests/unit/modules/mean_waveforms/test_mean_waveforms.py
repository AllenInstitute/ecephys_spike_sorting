import pytest
import numpy as np
import os

#from ecephys_spike_sorting.modules.mean_waveforms.extract_waveforms import extract_waveforms
#mport ecephys_spike_sorting.common.utils as utils

#DATA_DIR = os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

def test_extract_waveforms():

    sample_rate = 30000.0
    numChannels = 384
    bit_volts = 0.195

    params = {}
    params['samples_per_spike'] = 82
    params['pre_samples'] = 20
    params['num_epochs'] = 4
    params['spikes_per_epoch'] = 5

    pass

    #raw_data_file = os.path.join(DATA_DIR, 'continuous_ap_post.dat')
    #rawData = np.memmap(raw_data_file, dtype='int16', mode='r')
    #data = np.reshape(rawData, (int(rawData.size/384), 384))

    #spike_times, spike_clusters, amplitudes, \
    # templates, channel_map, cluster_ids, cluster_quality \
    # = utils.load_kilosort_data(DATA_DIR, sample_rate, False)

    #data, spike_counts, coords, labels = extract_waveforms(data, spike_times, spike_clusters, cluster_ids, cluster_quality, bit_volts, sample_rate, params)

    #print(labels)
