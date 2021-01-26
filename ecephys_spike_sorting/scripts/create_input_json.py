import os, io, json, sys

if sys.platform == 'linux':
    import pwd
from helpers import SpikeGLX_utils

import numpy as np

def create_samba_directory(samba_server, samba_share):

    if sys.platform == 'linux':
        proc_owner_uid = str(pwd.getpwnam(os.environ['USER']).pw_uid)
        share_string = 'smb-share:server={},share={}'.format(samba_server, samba_share)
        data_dir = os.path.join('/', 'var', 'run', 'user', proc_owner_uid, 'gvfs', share_string)
    else:
        data_dir = r'\\' + os.path.join(samba_server, samba_share)

    return data_dir

def createInputJson(output_file, 
                    npx_directory=None, 
                    continuous_file = None,
                    spikeGLX_data=True,
                    extracted_data_directory=None,
                    kilosort_output_directory=None,
                    ks_make_copy=False,
                    probe_type='3A',
                    catGT_run_name=None,
                    gate_string='0',
                    trigger_string='0,0',
                    probe_string='0',
                    catGT_stream_string = '-ap',
                    catGT_car_mode = 'gbldmx',
                    catGT_loccar_min_um = 40,
                    catGT_loccar_max_um = 160,
                    catGT_cmd_string = '-prb_fld -out_prb_fld -aphipass=300-gfix=0.40,0.10,0.02',
                    catGT_extract_string = '',
                    noise_template_use_rf = True,
                    event_ex_param_str = 'XD=4,1,50',
                    sync_period = 1.0,
                    toStream_sync_params = 'SY=0,384,6,500',
                    niStream_sync_params = 'XA=0,1,3,500',
                    toStream_path_3A = None,
                    fromStream_list_3A = None,
                    ks_remDup = 0,                   
                    ks_finalSplits = 1,
                    ks_labelGood = 1,
                    ks_saveRez = 1,
                    ks_minfr_goodchannels = 0.1,                  
                    ks_whiteningRadius_um = 163,
                    ks_Th = '[10,4]',
                    ks_CSBseed = 1,
                    ks_LTseed = 1,
                    ks_templateRadius_um = 163,
                    c_Waves_snr_um = 160,
                    qm_isi_thresh = 1.5/1000
                    ):

    # hard coded paths to code on your computer and system
    ecephys_directory = r'D:\ecephys_fork\ecephys_spike_sorting\ecephys_spike_sorting'
    
    # location of kilosor respository and KS2 version
    kilosort_repository = r'C:\Users\labadmin\Documents\jic\KS20_release'
    KS2ver = '2.0'
    
    npy_matlab_repository = r'C:\Users\labadmin\Documents\jic\npy-matlab-master'
    catGTPath = r'C:\Users\labadmin\Documents\jic\CatGT-win'
    tPrime_path=r'C:\Users\labadmin\Documents\jic\TPrime-win'
    cWaves_path=r'C:\Users\labadmin\Documents\jic\C_Waves-win'
    
     
    # for config files and kilosort working space
    kilosort_output_tmp = r'D:\kilosort_datatemp' 
    
    
    # derived directory names
    
    modules_directory = os.path.join(ecephys_directory,'modules')
    
    if kilosort_output_directory is None \
         and extracted_data_directory is None \
         and npx_directory is None:
        raise Exception('Must specify at least one output directory')


    #default ephys params. For spikeGLX, these get replaced by values read from metadata
    sample_rate = 30000
    num_channels = 384    
    reference_channels = [191]
    uVPerBit = 2.34375
    acq_system = 'PXI'
     
    
    if spikeGLX_data:
        # location of the raw data is the continuous file passed from script
        # metadata file should be located in same directory
        # 
        # kilosort output will be put in the same directory as the input raw data,
        # set in kilosort_output_directory passed from script
        # kilososrt postprocessing (duplicate removal) and identification of noise
        # clusters will act on phy output in the kilosort output directory
        #
        # 
        if continuous_file is not None:
            probe_type, sample_rate, num_channels, uVPerBit = SpikeGLX_utils.EphysParams(continuous_file)  
            print('SpikeGLX params read from meta')
            print('probe type: {:s}, sample_rate: {:.5f}, num_channels: {:d}, uVPerBit: {:.4f}'.format\
                  (probe_type, sample_rate, num_channels, uVPerBit))
        print('kilosort output directory: ' + kilosort_output_directory )
        # set Open Ephys specific dictionary keys; can't be null and still 
        # pass argshema parser, even when unused
        settings_json = npx_directory
        probe_json = npx_directory
        settings_xml = npx_directory
        
    else:
    # Data from Open Ephys; these params are sent manually from script
    
        if probe_type == '3A':
            acq_system = '3a'
            reference_channels = [36, 75, 112, 151, 188, 227, 264, 303, 340, 379]
            uVPerBit = 2.34375      # for AP gain = 500
        elif (probe_type =='NP1' or probe_type =='3B2'):
            acq_system = 'PXI'
            reference_channels = [191] 
            uVPerBit = 2.34375      # for AP gain = 500
        elif (probe_type == 'NP21' or probe_type == 'NP24'):
            acq_system = 'PXI'
            reference_channels = [127]
            uVPerBit = 0.763      # for AP gain = 80, fixed in 2.0
        else:
            raise Exception('Unknown probe type')
        
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
    
        if continuous_file is None:
            continuous_file = os.path.join(kilosort_output_directory, 'continuous.dat')
            

    # geometry params by probe type. expand the dictoionaries to add types
    # vertical probe pitch vs probe type
    vpitch = {'3A': 20, 'NP1': 20, 'NP21': 15, 'NP24': 15, 'NP1100': 6}  
    hpitch = {'3A': 32, 'NP1': 32, 'NP21': 32, 'NP24': 32, 'NP1100': 6} 
    nColumn = {'3A': 2, 'NP1': 2, 'NP21': 2, 'NP24': 2, 'NP1100': 8} 
    
    
    # CatGT needs the inner and outer redii for local common average referencing
    # specified in sites
    catGT_loccar_min_sites = int(round(catGT_loccar_min_um/vpitch.get(probe_type)))
    catGT_loccar_max_sites = int(round(catGT_loccar_max_um/vpitch.get(probe_type)))
    # print('loccar min: ' + repr(catGT_loccar_min_sites))
    
    # whiteningRange is the number of sites used for whitening in KIlosort
    # preprocessing. Calculate the number of sites within the user-specified
    # whitening radius for this probe geometery
    # for a Np 1.0 probe, 163 um => 32 sites
    nrows = np.sqrt((np.square(ks_whiteningRadius_um) - np.square(hpitch.get(probe_type))))/vpitch.get(probe_type)
    ks_whiteningRange = int(round(2*nrows*nColumn.get(probe_type)))
    
    # nNeighbors is the number of sites kilosort includes in a template.
    # Calculate the number of sites within that radisu.
    nrows = np.sqrt((np.square(ks_templateRadius_um) - np.square(hpitch.get(probe_type))))/vpitch.get(probe_type)
    ks_nNeighbors = int(round(2*nrows*nColumn.get(probe_type)))
    # print('ks_nNeighbors: ' + repr(ks_nNeighbors))
    
    c_waves_radius_sites = int(round(c_Waves_snr_um/vpitch.get(probe_type)))

    # Create string designating temporary output file for KS2 (gets inserted into KS2 config.m file)
    fproc = os.path.join(kilosort_output_tmp,'temp_wh.dat') # full path for temp whitened data file
    fproc_forward_slash = fproc.replace('\\','/')
    fproc_str = "'" + fproc_forward_slash + "'"
    

    
    dictionary = \
    {

        "directories": {
            "ecephys_directory":ecephys_directory,
            "npx_directory": npx_directory,
            "extracted_data_directory": extracted_data_directory,
            "kilosort_output_directory": kilosort_output_directory,
            "kilosort_output_tmp": kilosort_output_tmp
        },

        "common_files": {
            "settings_json" : settings_json,
            "probe_json" : probe_json,
        },

        "waveform_metrics" : {
            "waveform_metrics_file" : os.path.join(kilosort_output_directory, 'waveform_metrics.csv')
        },
        
        "cluster_metrics" : {
            "cluster_metrics_file" : os.path.join(kilosort_output_directory, 'metrics.csv')
        },

        "ephys_params": {
            "probe_type" : probe_type,
            "sample_rate" : sample_rate,
            "lfp_sample_rate" : 2500,
            "bit_volts" : uVPerBit,
            "num_channels" : num_channels,
            "reference_channels" : reference_channels,
            "vertical_site_spacing" : 10e-6,
            "ap_band_file" : continuous_file,
            "lfp_band_file" : os.path.join(extracted_data_directory, 'continuous', 'Neuropix-' + acq_system + '-100.1', 'continuous.dat'),
            "reorder_lfp_channels" : True,
            "cluster_group_file_name" : 'cluster_group.tsv'
        }, 

        "extract_from_npx_params" : {
            "npx_directory": npx_directory,
            "settings_xml": settings_xml,
            "npx_extractor_executable": r"C:\Users\svc_neuropix\Documents\GitHub\npxextractor\Release\NpxExtractor.exe",
            "npx_extractor_repo": r"C:\Users\svc_neuropix\Documents\GitHub\npxextractor"
        },

        "depth_estimation_params" : {
            "hi_noise_thresh" : 50.0,
            "lo_noise_thresh" : 3.0,
            "save_figure" : 1,
            "figure_location" : os.path.join(extracted_data_directory, 'probe_depth.png'),
            "smoothing_amount" : 5,
            "power_thresh" : 2.5,
            "diff_thresh" : -0.06,
            "freq_range" : [0, 10],
            "max_freq" : 150,
            "channel_range" : [374, 384],
            "n_passes" : 10,
            "air_gap" : 25,
            "time_interval" : 5,
            "skip_s_per_pass" : 10,
            "start_time" : 10
        }, 

        "median_subtraction_params" : {
            "median_subtraction_executable": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\spikebandmediansubtraction\\Builds\\VisualStudio2013\\Release\\SpikeBandMedianSubtraction.exe",
            "median_subtraction_repo": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\spikebandmediansubtraction\\",
        },

        "kilosort_helper_params" : {

            "matlab_home_directory": kilosort_output_tmp,
            "kilosort_repository" : kilosort_repository,
            "npy_matlab_repository" : npy_matlab_repository,
            "kilosort_version" : 2,
            "spikeGLX_data" : True,
            "ks_make_copy": ks_make_copy,
            "surface_channel_buffer" : 15,

            "kilosort2_params" :
            {
                "KSver" : KS2ver,
                "remDup" : ks_remDup,       #these are expressed as int rather than Bool for matlab compatability
                "finalSplits" : ks_finalSplits,
                "labelGood" : ks_labelGood,
                "saveRez" : ks_saveRez,
                "fproc" : fproc_str,
                "chanMap" : "'chanMap.mat'",
                "fshigh" : 150,
                "minfr_goodchannels" : ks_minfr_goodchannels,
                "Th" : ks_Th,
                "lam" : 10,
                "AUCsplit" : 0.9,
                "minFR" : 1/50.,
                "momentum" : '[20 400]',
                "sigmaMask" : 30,
                "ThPre" : 8,
                "gain" : uVPerBit,
                "CSBseed" : ks_CSBseed,
                "LTseed" : ks_LTseed,
                "whiteningRange" : ks_whiteningRange,
                "nNeighbors" : ks_nNeighbors
            }
        },

# as implemented, "within_unit_overlap window" must be >= "between unit overlap window"
        "ks_postprocessing_params" : {
            "within_unit_overlap_window" : 0.000333,
            "between_unit_overlap_window" : 0.000333,
            "between_unit_dist_um" : 42,
            "deletion_mode" : 'lowAmpCluster'
        },

        "mean_waveform_params" : {
        
            "mean_waveforms_file" : os.path.join(kilosort_output_directory, 'mean_waveforms.npy'),
            "samples_per_spike" : 82,
            "pre_samples" : 20,
            "num_epochs" : 1,           #epochs not implemented for c_waves
            "spikes_per_epoch" : 1000,
            "spread_threshold" : 0.12,
            "site_range" : 16,    
            "cWaves_path" : cWaves_path,
            "use_C_Waves" : True,
            "snr_radius" : c_waves_radius_sites       
        },
            

        "noise_waveform_params" : {
            "classifier_path" : os.path.join(modules_directory, 'noise_templates', 'rf_classifier.pkl'),
            "multiprocessing_worker_count" : 10,
            "use_random_forest" : noise_template_use_rf
        },

        "quality_metrics_params" : {
            "isi_threshold" : qm_isi_thresh,
            "min_isi" : 0.000166,
            "num_channels_to_compare" : 13,
            "max_spikes_for_unit" : 500,
            "max_spikes_for_nn" : 10000,
            "n_neighbors" : 4,
            'n_silhouette' : 10000,
            "drift_metrics_interval_s" : 51,
            "drift_metrics_min_spikes_per_interval" : 10
        },
        
        "catGT_helper_params" : {
            "run_name" : catGT_run_name,
            "gate_string" : gate_string,
            "probe_string" : probe_string,
            "trigger_string": trigger_string,
            "stream_string" : catGT_stream_string,
            "car_mode" : catGT_car_mode,
            "loccar_inner" : catGT_loccar_min_sites,
            "loccar_outer": catGT_loccar_max_sites,
            "cmdStr" : catGT_cmd_string,
            "extract_string" : catGT_extract_string,
            "catGTPath" : catGTPath
        },

        "tPrime_helper_params" : {
                "tPrime_path" : tPrime_path,
                "sync_period" : sync_period,
                "toStream_sync_params" : toStream_sync_params,
                "ni_sync_params" : niStream_sync_params,
                "toStream_path_3A" : toStream_path_3A,
                "fromStream_list_3A" : fromStream_list_3A
                },  
                
        "psth_events": {
                "event_ex_param_str": event_ex_param_str
                }
        
    }

    with io.open(output_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(dictionary, ensure_ascii=False, sort_keys=True, indent=4))

    return dictionary