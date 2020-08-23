import os, io, json, glob, sys

if sys.platform == 'linux':
    import pwd
from helpers import SpikeGLX_utils

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
                    catGT_cmd_string = '-prb_fld -out_prb_fld -aphipass=300 -gbldmx -gfix=0.40,0.10,0.02',
                    catGT_gfix_edits = 0,
                    noise_template_use_rf = True,
                    event_ex_param_str = 'XD=4,1,50',
                    sync_period = 1.0,
                    toStream_sync_params = 'SY=0,384,6,500',
                    niStream_sync_params = 'XA=0,1,3,500',
                    toStream_path_3A = None,
                    fromStream_list_3A = None,
                    minfr_goodchannels = 0.1,
                    whiteningRange = 32,
                    CSBseed = 1,
                    LTseed = 1,
                    nNeighbors = 32
                    ):

    # hard coded paths to code on your computer and system
    ecephys_directory = r'D:\ecephys_fork\ecephys_spike_sorting\ecephys_spike_sorting'
    kilosort_repository = r'C:\Users\labadmin\Documents\jic\KS2_040920\Kilosort2'
    npy_matlab_repository = r'C:\Users\labadmin\Documents\jic\npy-matlab-master'
    catGTPath = r'C:\Users\labadmin\Documents\jic\CatGT'
    tPrime_path=r'C:\Users\labadmin\Documents\jic\TPrimeApp\TPrime'
    cWaves_path=r'C:\Users\labadmin\Documents\jic\C_Waves'
    
    # set paths to KS2 master file to run; these should be appropriate for the
    # kilosort repository specified above
    # default inside the ecephys pipeline are:
    #       master_file_path = os.path.join(ecephys_directory,'modules','kilosort_helper')
    #       master_file_name = 'kilosort2_master_file.m'          
    master_file_path = os.path.join(ecephys_directory,'modules','kilosort_helper')    
    master_file_name = 'kilosort2_master_file.m'   
     
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
            "master_file_path" : master_file_path,
            "master_file_name" : master_file_name,
            "kilosort_version" : 2,
            "spikeGLX_data" : True,
            "ks_make_copy": ks_make_copy,
            "surface_channel_buffer" : 15,

            "kilosort2_params" :
            {
                "fproc" : fproc_str,
                "chanMap" : "'chanMap.mat'",
                "fshigh" : 150,
                "minfr_goodchannels" : minfr_goodchannels,
                "Th" : '[10 4]',
                "lam" : 10,
                "AUCsplit" : 0.9,
                "minFR" : 1/50.,
                "momentum" : '[20 400]',
                "sigmaMask" : 30,
                "ThPre" : 8,
                "gain" : uVPerBit,
                "CSBseed" : CSBseed,
                "LTseed" : LTseed,
                "whiteningRange" : whiteningRange,
                "nNeighbors" : nNeighbors
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
            "snr_radius" : 8
        },
            

        "noise_waveform_params" : {
            "classifier_path" : os.path.join(modules_directory, 'noise_templates', 'rf_classifier.pkl'),
            "multiprocessing_worker_count" : 10,
            "use_random_forest" : noise_template_use_rf
        },

        "quality_metrics_params" : {
            "isi_threshold" : 0.0015,
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
            "cmdStr" : catGT_cmd_string,
            "catGTPath" : catGTPath,
            "gfix_edits": catGT_gfix_edits
        },

        "tPrime_helper_params" : {
                "tPrime_path" : tPrime_path,
                "sync_period" : sync_period,
                "toStream_sync_params" : toStream_sync_params,
                "niStream_sync_params" : niStream_sync_params,
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