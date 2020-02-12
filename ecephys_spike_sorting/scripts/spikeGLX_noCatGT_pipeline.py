import os
import subprocess

from helpers import SpikeGLX_utils
from create_input_json import createInputJson

# run a set of SpikeGLX tcat.probeN.bin files that are stored in one folder.
# creates an output folder for each, generatees a channel map file from
# the SpikeGLX metadata, then runs any other listed modules.

# directory for json files -- these record the parameters used for processing
json_directory = r'D:\ecephys_fork\json_files'

# directory with the raw data files. The metadata should be present, also
npx_directory = r'D:\ecephys_fork\test_data\test_no_preprocess'


# list of run names

 
run_names = [												
						'SC011_022319_g0_tcat.imec3.ap.bin',
                        'SC011_022319_g0_tcat.imec3.ap.bin',
                        'SC011_022319_g0_tcat.imec3.ap.bin',
                        'SC011_022319_g0_tcat.imec3.ap.bin',
                        'SC011_022319_g0_tcat.imec3.ap.bin',
                        'SC011_022319_g0_tcat.imec3.ap.bin',
                        'SC011_022319_g0_tcat.imec3.ap.bin',
                        'SC011_022319_g0_tcat.imec3.ap.bin',
                        'SC011_022319_g0_tcat.imec3.ap.bin',
                        'SC011_022319_g0_tcat.imec3.ap.bin',
                        'SC011_022319_g0_tcat.imec3.ap.bin'
]


probe_type = 'NP1'



# List of modules to run per probe
# if not running kilosort_helper, KS2 output must be in directories
# named according to this script, i.e. run_name_gN_tcat.imecN_phy
modules = [
			'kilosort_helper',
            'kilosort_postprocessing',
            'noise_templates'
		  ]

for name in run_names:

    baseName = SpikeGLX_utils.ParseTcatName(name)
    session_id = baseName
    
    outputDirName = baseName + '_phy'
    
    kilosort_output_dir = os.path.join(npx_directory, outputDirName)
    
    if not os.path.exists(kilosort_output_dir):
        os.mkdir(kilosort_output_dir)

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
    info = createInputJson(input_json, npx_directory=npx_directory, 
	                                   continuous_file = os.path.join(npx_directory,name),
                                       spikeGLX_data = 'True',
									   kilosort_output_directory=kilosort_output_dir, 
                                       ks_make_copy = ks_make_copy,
                                       extracted_data_directory = npx_directory,
                                       noise_template_use_rf = False
                                       )
   
 
    for module in modules:
        command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json
        subprocess.check_call(command.split(' '))
        
        
        
	


    
