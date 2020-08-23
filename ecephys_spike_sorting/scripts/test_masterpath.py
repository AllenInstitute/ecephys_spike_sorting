import os
import subprocess

from helpers import SpikeGLX_utils
from create_input_json import createInputJson

# run a set of SpikeGLX tcat.probeN.bin files that can be in any folder
# creates an output folder for each, generatees a channel map file from
# the SpikeGLX metadata, then runs any other listed modules.

# directory for json files -- these record the parameters used for processing
json_directory = r'D:\ecephys_fork\json_files'


# directory with the raw data files. The metadata should be present, also
#npx_directory = r'D:\ecephys_fork\test_data\test_no_preprocess'


# list of paths to binary files

 
run_paths = [												

             r'E:\simons_short\data\cortexlab-single-phase-3-10sec_g0_t0.imec.ap.bin',
             r'E:\simons_short\data\allen-mouse419112-probee-10sec.imec0.ap.bin'
]



run_seed = 1

# List of modules to run per probe
# if not running kilosort_helper, KS2 output must be in directories
# named according to this script, i.e. run_name_gN_tcat.imecN_phy
modules = [
			'kilosort_helper',
            'kilosort_postprocessing',
            'noise_templates',
            'mean_waveforms',
            'quality_metrics'
		  ]

for path in run_paths:
    npx_directory = os.path.dirname(path)
    name = os.path.basename(path)
    baseName = SpikeGLX_utils.ParseTcatName(name)
    prbStr = SpikeGLX_utils.GetProbeStr(name)   # returns empty string for 3A
    session_id = baseName

    # Create output directory
    kilosort_output_parent = os.path.join(npx_directory, baseName)
    
    if not os.path.exists(kilosort_output_parent):
        os.mkdir(kilosort_output_parent)
        
    # output subdirectory
    outputName = 'imec' + prbStr + '_ks2'
    
    kilosort_output_dir = os.path.join(kilosort_output_parent, outputName)


    input_json = os.path.join(json_directory, session_id + '-input.json')
    output_json = os.path.join(json_directory, session_id + '-output.json')
    
    # kilosort_postprocessing and noise_templates moduules alter the files
    # that are input to phy. If using these modules, keep a copy of the
    # original phy output
    if ('kilosort_postprocessing' in modules) or ('noise_templates' in modules):
        ks_make_copy = True
    else:
        ks_make_copy = False
    
    print( 'Creating json file for KS2 and postprocessing')
    print( 'npx_directory:', npx_directory)
    print( 'continuous file: ', os.path.join(npx_directory,name) )
    info = createInputJson(input_json, npx_directory=npx_directory, 
	                                   continuous_file = os.path.join(npx_directory,name),
                                       spikeGLX_data = 'True',
									   kilosort_output_directory=kilosort_output_dir, 
                                       ks_make_copy = ks_make_copy,
                                       extracted_data_directory = npx_directory,
                                       noise_template_use_rf = False,
                                       CSBseed = run_seed
                                       )
   
 
    for module in modules:
        command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json
        subprocess.check_call(command.split(' '))
        
        
        
	


    
