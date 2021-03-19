import os, io, json, glob, sys

if sys.platform == 'linux':
    import pwd

def create_samba_directory(samba_server, samba_share):

    if sys.platform == 'linux':
        proc_owner_uid = str(pwd.getpwnam(os.environ['USER']).pw_uid)
        share_string = 'smb-share:server={},share={}'.format(samba_server, samba_share)
        data_dir = os.path.join('/', 'var', 'run', 'user', proc_owner_uid, 'gvfs', share_string)
    else:
        data_dir = r'\\' + os.path.join(samba_server, samba_share)

    return data_dir

def createInputJsonKS3(output_file, 
                    npx_directory=None, 
                    continuous_file = None,
                    extracted_data_directory=None,
                    lfp_directory=None,
                    kilosort_output_directory=None, 
                    kilosort_output_tmp=None, 
                    probe_type='3A'):

    if kilosort_output_directory is None \
         and extracted_data_directory is None \
         and npx_directory is None:
        raise Exception('Must specify at least one output directory')

    if probe_type == '3A':
        acq_system = '3a'
        reference_channels = [36, 75, 112, 151, 188, 227, 264, 303, 340, 379]
    else:
        acq_system = 'PXI'
        reference_channels = [191]

    if npx_directory is not None:
        settings_xml = os.path.join(npx_directory, 'settings.xml')
        if extracted_data_directory is None:
            extracted_data_directory = npx_directory + '_sorted'
        probe_json = os.path.join(extracted_data_directory, 'probe_info.json')
        settings_json = os.path.join(extracted_data_directory, 'open-ephys.json')
    else:
        if extracted_data_directory is not None:
            probe_json = os.path.join(extracted_data_directory, 'probe_info.json')
            settings_json = os.path.join(extracted_data_directory, 'open-ephys.json')
            settings_xml = None
        else:
            settings_xml = None
            settings_json = None
            probe_json = None
            extracted_data_directory = kilosort_output_directory

    if kilosort_output_directory is None:
        kilosort_output_directory = os.path.join(extracted_data_directory, 'continuous', 'Neuropix-' + acq_system + '-100.0')

    if kilosort_output_tmp is None:
        kilosort_output_tmp = kilosort_output_directory

    if continuous_file is None:
        continuous_file = os.path.join(kilosort_output_directory, 'continuous.dat')

    sorted_basedir = os.path.split(os.path.split(kilosort_output_directory)[0])[0]
    probe_json = os.path.join(sorted_basedir, 'probe_info.json')
    if lfp_directory is None:
        lfp_directory = os.path.join(sorted_basedir, 'continuous', 'Neuropix-' + acq_system + '-100.1')

    

    dictionary = \
    {

        "directories": {
            "extraction_location": extracted_data_directory,
            "extracted_data_directory": kilosort_output_directory, #"D:\\for_some_reason_this_is_being_made"
            "kilosort_output_directory": kilosort_output_directory, #"D:\\for_some_reason_this_is_being_made"
            "kilosort_output_tmp": kilosort_output_tmp
        },

        "common_files": {
            "settings_json" : settings_json,
            "probe_json" : probe_json,
        },

        "waveform_metrics" : {
            "waveform_metrics_file" : os.path.join(kilosort_output_directory, 'waveform_metrics.csv')
        },

        "ephys_params": {
            "sample_rate" : 30000,
            "lfp_sample_rate" : 2500,
            "bit_volts" : 0.195,
            "num_channels" : 384,
            "reference_channels" : reference_channels,
            "vertical_site_spacing" : 10e-6,
            "ap_band_file" : continuous_file,
            "lfp_band_file" : os.path.join(lfp_directory, 'continuous.dat'),
            "reorder_lfp_channels" : probe_type == '3A',
            "cluster_group_file_name" : "cluster_group.tsv.v2"
        }, 

        "extract_from_npx_params" : {
            "npx_directory": npx_directory,
            "settings_xml": settings_xml,
            "npx_extractor_executable": r"C:\Users\svc_neuropix\Documents\GitHub\npxextractor\NpxExtractor\Release\NpxExtractor.exe",
            "npx_extractor_repo": r"C:\Users\svc_neuropix\Documents\GitHub\npxextractor"
        },

        "depth_estimation_params" : {
            "hi_noise_thresh" : 50.0,
            "lo_noise_thresh" : 3.0,
            "save_figure" : 1,
            "figure_location" : os.path.join(sorted_basedir, 'probe_depth.png'),
            "smoothing_amount" : 5,
            "power_thresh" : 2.5,
            "diff_thresh" : -0.06,
            "freq_range" : [0, 10],
            "max_freq" : 150,
            "channel_range" : [374, 384],
            "n_passes" : 10,
            "air_gap" : 100,
            "time_interval" : 5,
            "skip_s_per_pass" : 100,
            "start_time" : 150
        }, 

        "median_subtraction_params" : {
            "median_subtraction_executable": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\spikebandmediansubtraction\\Builds\\VisualStudio2013\\Release\\SpikeBandMedianSubtraction.exe",
            "median_subtraction_repo": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\spikebandmediansubtraction\\",
        },

        "kilosort_helper_params" : {

            "matlab_home_directory": "C:\\Users\\svc_neuropix\\Documents\\MATLAB",
            "kilosort_repository": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\kilosort3",
            "kilosort_version" : 3,
            "surface_channel_buffer" : 15,

            "kilosort3_params" :
            {
                "chanMap" : "'chanMap.mat'",
                "fshigh" : 300,
                "minfr_goodchannels" : 0.1,
                "Th" : '[9 9]',
                "lam" : 10,
                "AUCsplit" : 0.8,
                "minFR" : 1/50.,
                "momentum" : '[20 400]',
                "sigmaMask" : 30,
                "ThPre" : 8,
                "sig" : 20,
                "nblocks" : 5
            }
        },

        "ks_postprocessing_params" : {
            "within_unit_overlap_window" : 0.000166,
            "between_unit_overlap_window" : 0.000166,
            "between_unit_overlap_distance" : 5
        },

        "mean_waveform_params" : {
        
            "mean_waveforms_file" : os.path.join(kilosort_output_directory, 'mean_waveforms.npy'),

            "samples_per_spike" : 82,
            "pre_samples" : 20,
            "num_epochs" : 1,
            "spikes_per_epoch" : 1000,
            "spread_threshold" : 0.12,
            "site_range" : 16
        },

        "noise_waveform_params" : {
            "classifier_path" : os.path.join(os.getcwd(), 'ecephys_spike_sorting', 'modules', 'noise_templates', 'rf_classifier.pkl'),
            "multiprocessing_worker_count" : 10
        },


        "quality_metrics_params" : {
            "isi_threshold" : 0.0015,
            "min_isi" : 0.000166,
            "num_channels_to_compare" : 13,
            "max_spikes_for_unit" : 500,
            "max_spikes_for_nn" : 10000,
            "n_neighbors" : 4,
            'n_silhouette' : 10000,
            "quality_metrics_output_file" : os.path.join(kilosort_output_directory, "metrics.csv"),
            "drift_metrics_interval_s" : 51,
            "drift_metrics_min_spikes_per_interval" : 10,
            "include_pc_metrics" : False
        }

    }

    with io.open(output_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(dictionary, ensure_ascii=False, sort_keys=True, indent=4))

    return dictionary