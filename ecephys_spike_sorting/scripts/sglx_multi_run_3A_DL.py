import os
import subprocess

from helpers import SpikeGLX_utils
from helpers import log_from_json
from helpers import run_one_probe
from create_input_json import createInputJson


# script to run CatGT, KS2, postprocessing and TPrime on data collected using
# SpikeGLX. The construction of the paths assumes data was saved with
# "Folder per probe" selected (probes stored in separate folders) AND
# that CatGT is run with the -out_prb_fld option

# -------------------------------
# -------------------------------
# User input -- Edit this section
# -------------------------------
# -------------------------------

# brain region specific params
# can add a new brain region by adding the key and value for each param
# can add new parameters -- any that are taken by create_input_json --
# by adding a new dictionary with entries for each region and setting the 
# according to the new dictionary in the loop to that created json files.


refPerMS_dict = {'default': 2.0, 'cortex': 2.0, 'medulla': 1.5, 'thalamus': 1.0}

# threhold values appropriate for KS2, KS2.5
ksTh_dict = {'default':'[10,4]', 'cortex':'[10,4]', 'medulla':'[10,4]', 'thalamus':'[10,4]'}
# threshold values appropriate for KS3.0
#ksTh_dict = {'default':'[9,9]', 'cortex':'[9,9]', 'medulla':'[9,9]', 'thalamus':'[9,9]'}



# -----------
# Input data
# -----------
# Name for log file for this pipeline run. Log file will be saved in the
# output destination directory catGT_dest
# If this file exists, new run data is appended to it
logName = 'dl56_20181126_log.csv'

# Raw data directory = npx_directory, all runs to be processed are in
# subfolders of this folder
npx_directory = r'D:\ecephys_fork\test_data\3A_DL'

# run_specs = name, gate, trigger and probes to process
# Each run_spec is a list:
#   (string) animal name = undecorated run name , e.g. 'dl56',
#   (string) date of recording, as yyyymmdd, eg '20181126'
#   (string) gate index, as a string (e.g. '0')
#   (string) triggers to process/concatenate, as a string e.g. '0,400', '0,0', 
#           can replace first limit with 'start', last with 'end'; 'start,end'
#           will concatenate all trials in the probe folder
#   (list of strings) computer/ probe labels to process, as a list, e.g. ['ww2','ww4']
#   (list of strings) 'SY' if there is a digital/sync channel 'None' if no digital channel
#   (list of strings) rain regions, one per probe, to set region specific params
#           these strings must match a key in the param dictionaries above.
#
#   The assumed file structure for input is:
#   /probe(computer) label/date/animal name/*.bin files
#   Note that the both the folder name and run name = animal name
#   Does not use SpikeGLX generated run folders

run_specs = [									
					['dl56', '20181126', '0', 'start,end', ['ww2','ww4'], ['SY','SY'], ['cortex', 'cortex']  ]	
       
]

# ------------------
# Output destination
# ------------------
# Set to an existing directory; all output will be written here.
# Output will be in the standard SpikeGLX directory structure:
# run_folder/probe_folder/*.bin
catGT_dest_parent = r'D:\ecephys_fork\test_data\3A_DL\DL56_new'

# ------------
# CatGT params
# ------------
run_CatGT = True   # set to False to sort/process previously processed data.


# CAR mode for CatGT. Must be equal to 'None', 'gbldmx', or 'loccar'
car_mode = 'gbldmx'
# inner and outer radii, in um for local comman average reference, if used
loccar_min = 40
loccar_max = 160

# CatGT commands for bandpass filtering, artifact correction, and zero filling
# Note 2: this command line includes specification of edge extraction
# see CatGT readme for details
# these parameters will be used for all runs
catGT_cmd_string = '-prb_3A -no_run_fld -t_miss_ok -aphipass=300 -aplopass=9000 -gbldmx -gfix=0,0.10,0.02'

# SYNC extraction string; this will be applied to all probes for whicch the sync = 'SY'
# probe always = 0 (3A one probe per run), word = -1 tells CatGT to take the last 
# channel in the file
sync_extract_string = ' -SY=0,-1,0,0 -SY=0,-1,1,50 -SY=0,-1,1,10 -SY=0,-1,1,1200,0.2 '


# ----------------------
# KS2 or KS25 parameters
# ----------------------
# parameters that will be constant for all recordings
# Template ekmplate radius and whitening, which are specified in um, will be 
# translated into sites using the probe geometry.
ks_remDup = 0
ks_saveRez = 1
ks_copy_fproc = 0
ks_templateRadius_um = 163
ks_whiteningRadius_um = 163
ks_minfr_goodchannels = 0.1


# ----------------------
# C_Waves snr radius, um
# ----------------------
c_Waves_snr_um = 160

# ----------------------
# psth_events parameters
# ----------------------
# extract param string for psth events -- copy the CatGT params used to extract
# events that should be exported with the phy output for PSTH plots
# If not using, remove psth_events from the list of modules
event_ex_param_str = 'SY=0,-1,1,50'

# -----------------
# TPrime parameters
# -----------------
runTPrime = True   # set to False if not using TPrime
sync_period = 12.0   # true for SYNC wave generated by imec basestation
toStream_sync_params = 'SY=0,-1,0,0'  # this sync signal from the first probe will be the toStream


# ---------------
# Modules List
# ---------------
# List of modules to run per probe; CatGT and TPrime are called once for each run.
modules = [
			'kilosort_helper',
            'kilosort_postprocessing',
            'noise_templates',
            'mean_waveforms',
            'quality_metrics'
			]

json_directory = r'D:\ecephys_fork\json_files'

# -----------------------
# -----------------------
# End of user input
# -----------------------
# -----------------------

# delete the existing CatGT.log
try:
    os.remove('CatGT.log')
except OSError:
    pass

# delete existing Tprime.log
try:
    os.remove('Tprime.log')
except OSError:
    pass

# delete existing C_waves.log
try:
    os.remove('C_Waves.log')
except OSError:
    pass

# check for existence of log file, create if not there
logFullPath = os.path.join(catGT_dest_parent, logName)
if not os.path.isfile(logFullPath):
    # create the log file, write header
    log_from_json.writeHeader(logFullPath)
    
    


for spec in run_specs:
    
    
    session_id = spec[0] + '_' + spec[1] + '_g' + spec[2]

    # if the directory animal name_date does not yet exist, create it
    catGT_dest = os.path.join(catGT_dest_parent, session_id)
    if not os.path.exists(catGT_dest):
        os.mkdir(catGT_dest)

    # probe list == probe label list for 3A
    prb_list = spec[4]

    # inputs for tPrime
    fromStream_list = list()
    
    # build path to the first probe folder; look into that folder
    # to determine the range of trials if the user specified t limits as
    # start and end
    runFolder = os.path.join(npx_directory, prb_list[0], spec[0], spec[1])
    first_trig, last_trig = SpikeGLX_utils.ParseTrigStr(spec[3], '', spec[2], runFolder)
    trigger_str = repr(first_trig) + ',' + repr(last_trig)
    
    # loop over all probes in hte run to build json files of input parameters
    # initalize lists for input and output json files
    catGT_input_json = []
    catGT_output_json = []
    module_input_json = []
    module_output_json = []
    session_id = []
    data_directory = []
    
    # first loop over probes creates json files containing parameters for
    # both preprocessing (CatGt) and sorting + postprocessing
    
    for i, prb in enumerate(prb_list):
            
        #create CatGT command for this probe
        print('Creating json file for CatGT on probe: ' + prb)
        # names for CatGT json files
        catGT_input_json.append(os.path.join(json_directory, spec[0] + prb + '_CatGT' + '-input.json'))
        catGT_output_json.append(os.path.join(json_directory, spec[0] + prb + '_CatGT' + '-output.json'))
        
      
        #   Path to folder containing bindaries.
        #   The assumed file structure for input is:
        #   /probe(computer) label/animal name/date/*.bin files
        run_folder = os.path.join(npx_directory, prb, spec[0], spec[1])
        
        # name of run in input data; note that this run name is not unique
        # but repeated for different dates
        runName = spec[0]

        # build parameter strings for catGT edge extractions for this probe
        currSY = spec[5][i]
        
        if currSY != 'None':
            extract_string = sync_extract_string
        else:
            extract_string = ''
            
        # if this is the first probe proceessed, make this the toStream
        # else, append to list of from stream paths
        catGT_sub_name = 'catgt_' + spec[0] + '_' + spec[1] + prb + '_g' + spec[2]
        catGT_sub = os.path.join( catGT_dest, catGT_sub_name)


        
        # build name of first trial to be concatenated/processed;
        # allows reaidng of the metadata

        input_data_directory = os.path.join(npx_directory, run_folder)
        fileName = runName + '_g' + spec[2] + '_t' + repr(first_trig) + '.imec.ap.bin'
        continuous_file = os.path.join(input_data_directory, fileName)
        metaName = runName + '_g' + spec[2] + '_t' + repr(first_trig) + '.imec.ap.meta'
        input_meta_fullpath = os.path.join(input_data_directory, metaName)
        
        print(input_meta_fullpath)
         
        info = createInputJson(catGT_input_json[i], npx_directory=input_data_directory, 
                                       continuous_file = continuous_file,
                                       kilosort_output_directory=catGT_dest,
                                       spikeGLX_data = True,
                                       input_meta_path = input_meta_fullpath,
                                       catGT_run_name = spec[0],
                                       gate_string = spec[2],
                                       trigger_string = trigger_str,
                                       probe_string = '0',
                                       catGT_stream_string = '-ap',
                                       catGT_car_mode = car_mode,
                                       catGT_loccar_min_um = loccar_min,
                                       catGT_loccar_max_um = loccar_max,
                                       catGT_cmd_string = catGT_cmd_string + ' ' + extract_string,
                                       extracted_data_directory = catGT_sub
                                       )      
        
        #create json files for the other modules
        session_id.append(spec[0] + '_imec' + prb)
        
        module_input_json.append(os.path.join(json_directory, session_id[i] + '-input.json'))
        
        
        # location of the binary created by CatGT, for 3A, not using prb_fld
        run_str = spec[0] + '_g' + spec[2]
#        run_folder = 'catgt_' + run_str
#        prb_folder = run_str + '_imec' + prb
        data_directory.append(os.path.join(catGT_sub, ('catgt_' + run_str)))
        
        if i == 0:
            toStream_path_3A = data_directory[i]
            print('i=0, setting toStream_path: ' + toStream_path_3A)
        else:
            fromStream_list.append(data_directory[i])
            fi = len(fromStream_list) -1
            print("setting from_path: " + repr(i) + ', ' + fromStream_list[fi])
            
        fileName = run_str + '_tcat.imec.ap.bin'
        continuous_file = os.path.join(data_directory[i], fileName)
 
        outputName = 'imec_' + prb + '_ks2'

        # kilosort_postprocessing and noise_templates moduules alter the files
        # that are input to phy. If using these modules, keep a copy of the
        # original phy output
        if ('kilosort_postprocessing' in modules) or('noise_templates' in modules):
            ks_make_copy = True
        else:
            ks_make_copy = False

        kilosort_output_dir = os.path.join(data_directory[i], outputName)

        print(data_directory[i])
        print(continuous_file)
        
        # get region specific parameters
        ks_Th = ksTh_dict.get(spec[6][i])
        refPerMS = refPerMS_dict.get(spec[6][i])
        print( 'ks_Th: ' + repr(ks_Th) + ' ,refPerMS: ' + repr(refPerMS))

        info = createInputJson(module_input_json[i], npx_directory=npx_directory, 
	                                   continuous_file = continuous_file,
                                       spikeGLX_data = True,
                                       input_meta_path = input_meta_fullpath,
									   kilosort_output_directory=kilosort_output_dir,
                                       ks_make_copy = ks_make_copy,
                                       noise_template_use_rf = False,
                                       catGT_run_name = session_id[i],
                                       gate_string = spec[2],
                                       probe_string = '0',  
                                       ks_remDup = ks_remDup,                   
                                       ks_finalSplits = 1,
                                       ks_labelGood = 1,
                                       ks_saveRez = ks_saveRez,
                                       ks_copy_fproc = ks_copy_fproc,
                                       ks_minfr_goodchannels = ks_minfr_goodchannels,                  
                                       ks_whiteningRadius_um = ks_whiteningRadius_um,
                                       ks_Th = ks_Th,
                                       ks_CSBseed = 1,
                                       ks_LTseed = 1,
                                       ks_templateRadius_um = ks_templateRadius_um,
                                       extracted_data_directory = catGT_dest,
                                       event_ex_param_str = event_ex_param_str,
                                       c_Waves_snr_um = c_Waves_snr_um,                               
                                       qm_isi_thresh = refPerMS/1000
                                       )   

       
        
    # loop over probes for processing.    
    for i, prb in enumerate(prb_list):  
        
        run_one_probe.runOne( session_id[i],
                 json_directory,
                 data_directory[i],
                 run_CatGT,
                 catGT_input_json[i],
                 catGT_output_json[i],
                 modules,
                 module_input_json[i],
                 logFullPath )
                 
        
    if runTPrime:
        # after loop over probes, run TPrime to create files of 
        # event times -- edges detected in auxialliary files and spike times 
        # from each probe -- all aligned to a reference stream.
    
        for i in range(len(fromStream_list)):
            print(fromStream_list[i])
            
        # create json files for calling TPrime
        session_id = spec[0] + '_TPrime'
        input_json = os.path.join(json_directory, session_id + '-input.json')
        output_json = os.path.join(json_directory, session_id + '-output.json')
           
        
        info = createInputJson(input_json, npx_directory=npx_directory, 
    	                                   continuous_file = continuous_file,
                                           spikeGLX_data = True,
                                           input_meta_path = input_meta_fullpath,
                                           catGT_run_name = spec[0],
    									   kilosort_output_directory=kilosort_output_dir,
                                           extracted_data_directory = catGT_dest,
                                           tPrime_im_ex_list = ' ',
                                           tPrime_ni_ex_list = ' ',
                                           event_ex_param_str = event_ex_param_str,
                                           sync_period = sync_period,
                                           toStream_sync_params = toStream_sync_params,
                                           niStream_sync_params = ' ',
                                           tPrime_3A = True,
                                           toStream_path_3A = toStream_path_3A,
                                           fromStream_list_3A = fromStream_list
                                           ) 
        
        command = "python -W ignore -m ecephys_spike_sorting.modules." + 'tPrime_helper' + " --input_json " + input_json \
    		          + " --output_json " + output_json
        subprocess.check_call(command.split(' '))  
    

