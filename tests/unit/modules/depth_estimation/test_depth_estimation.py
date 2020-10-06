import pytest
import numpy as np
import os

#from ecephys_spike_sorting.modules.depth_estimation.depth_estimation import compute_offset_and_surface_channel
#import ecephys_spike_sorting.common.utils as utils

#DATA_DIR = os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

def test_depth_estimation():

	ephys_params = {}
	ephys_params['sample_rate'] = 30000.0
	ephys_params['lfp_sample_rate'] = 2500.0
	ephys_params['bit_volts'] = 0.195
	ephys_params['num_channels'] = 384
	ephys_params['reference_channels'] = np.array([37, 76, 113, 152, 189, 228, 265, 304, 341, 380])

	params = {}
	params['hi_noise_thresh'] = 50.0
	params['lo_noise_thresh'] = 3.0
	params['save_figure'] = False
	params['smoothing_amount'] = 5
	params['power_thresh'] = 2.5
	params['diff_thresh'] = -0.07
	params['freq_range'] = [0, 10]
	params['max_freq'] = 150
	params['channel_range'] = [370, 380]
	params['n_passes'] = 1
	params['start_sample'] = 0
	params['air_gap'] = 100
	params['nfft'] = 4096
	params['skip_s_per_pass'] = 100

	pass

	#aw_data_file = os.path.join(DATA_DIR, 'continuous_ap_pre.dat')
	#rawData = np.memmap(raw_data_file, dtype='int16', mode='r')
	#data = np.reshape(rawData, (int(rawData.size/384), 384))

	#aw_data_file_lfp = os.path.join(DATA_DIR, 'continuous_lfp_pre.dat')
	#rawDataLfp = np.memmap(raw_data_file_lfp, dtype='int16', mode='r')
	#data_lfp = np.reshape(rawDataLfp, (int(rawDataLfp.size/384), 384))

	#info = compute_offset_and_surface_channel(data, data_lfp, \
    #            ephys_params, params)
