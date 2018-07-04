import os, io, json

def createInputJson(npx_file, output_file):

	probe_directory = os.path.dirname(npx_file)
	settings_xml = os.path.join(probe_directory, 'settings.xml')

	drive, tail = os.path.split(probe_directory)

	extracted_data_directory = os.path.join(r'C:\data', tail + '_sorted')
	probe_json = os.path.join(extracted_data_directory, 'probe_info.json')
	kilosort_output_directory = os.path.join(extracted_data_directory, r'continuous\Neuropix-3a-100.0')

	dictionary = \
	{
		"npx_file": npx_file,
		"settings_xml": settings_xml,
		"probe_json" : probe_json,

		"npx_extractor_executable": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\npxextractor\\Release\\NpxExtractor.exe",
		"npx_extractor_repo": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\npxextractor",

	    "median_subtraction_executable": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\spikebandmediansubtraction\\Builds\\VisualStudio2013\\Release\\SpikeBandMedianSubtraction.exe",
	    "median_subtraction_repo": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\spikebandmediansubtraction\\",

	    "kilosort_location": "C:\\Users\\svc_neuropix\\Documents\\MATLAB",
	    "kilosort_repo": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\kilosort2",
	    "kilosort_version" : 2,
	    "surface_channel_buffer" : 15,

		"directories": {
			"extracted_data_directory": extracted_data_directory,
			"kilosort_output_directory": kilosort_output_directory
		},

		"ephys_params": {
			"sample_rate" : 30000,
			"lfp_sample_rate" : 2500,
			"bit_volts" : 0.195,
			"num_channels" : 384,
			"reference_channels" : [36, 75, 112, 151, 188, 227, 264, 303, 340, 379]
		}, 

		"depth_estimation_params" : {
			"hi_noise_thresh" : 50.0,
			"lo_noise_thresh" : 3.0,
			"save_figure" : 1,
			"figure_location" : extracted_data_directory,
			"smoothing_amount" : 5,
			"power_thresh" : 2.5,
			"diff_thresh" : 0.07,
			"freq_range" : [0, 10],
			"max_freq" : 150,
			"channel_range" : [370, 380],
			"n_passes" : 1,
			"air_gap" : 100,
			"skip_s_per_pass" : 100
		}, 

		"kilosort2_params" : {
			"chanMap" : "'chanMap.mat'",
			"trange" : '[0 Inf]',
			"fproc" : "fullfile('C:/data/kilosort', 'temp_wh.dat')",
			"fbinary" : "fullfile(ops.rootZ, 'continuous.dat')",
			"datatype" : "'.dat'",
			"fshigh" : 150,
			"Th" : '[12 12]',
			"lam" : 100,
			"mergeThreshold" : 0.25,
			"ccsplit" : 0.97,
			"minFR" : 1/50.,
			"ThS" : '[8 8]',
			"momentum" : '[20 400]',
			"sigmaMask" : 30,
			"Nfilt" : 1024,
			"nPCs" : 3,
			"useRAM" : 0,
			"ThPre" : 8,
			"GPU" : 1,
			"nSkipCov" : 5,
			"ntbuff" : 64,
			"scaleproc" : 200,
			"NT" : '64*1024 + ops.ntbuff',
			"spkTh" : -6,
			"loc_range" : '[5 4]',
			"long_range" : '[30 6]',
			"maskMaxChannels" : 5,
			"criterionNoiseChannels" : 0.2,
			"whiteningRange" : 32
		},

		"mean_waveform_params" : {
			"samples_per_spike" : 82,
			"pre_samples" : 20,
			"num_epochs" : 1,
			"spikes_per_epoch" : 100
		},

		"noise_waveform_params" : {
			"classifier_path" : "C:\\Users\\svc_neuropix\\Documents\\GitHub\\ecephys_spike_sorting\\ecephys_spike_sorting\\modules\\noise_templates\\classifier.pkl"

		},

		"quality_metrics_params" : {

			"isi_threshold" : 0.015,
			"snr_spike_count" : 100,
			"samples_per_spike" : 82,
			"pre_samples" : 20
		}

	}

	with io.open(output_file, 'w', encoding='utf-8') as f:
		f.write(json.dumps(dictionary, ensure_ascii=False, sort_keys=True, indent=4))

	return dictionary