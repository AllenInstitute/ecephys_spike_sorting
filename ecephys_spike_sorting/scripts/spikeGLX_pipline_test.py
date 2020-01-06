import os
import subprocess

from helpers import SpikeGLX_utils
from create_input_json import createInputJson

run_preprocess = True   # set to False to rerun KS2 or processing on previously processed data.

# batch file catGT_helper module for a set of runs in the 
# directory npx_directory. Gate, trigger, probes to process are set
# in the run_spec
# Other CatGT params are set in create_input_json.py (cmdStr)

npx_directory = r'D:\ecephys_fork\test_data\SC_artifact_test_data'

# Set to an existing directory to send all output to a new directory. It will then have 
# the standard SpikeGLX directory structure: run_folder/probe_folder/*.bin

catGT_dest = r'D:\ecephys_fork\test_data\SC_artifact_test_data\CatGT_out'

# Each run_spec is a list of 4 strings:
#   undecorated run name (no g/t specifier, the run field in CatGT)
#   gate index, as a string (e.g. '0')
#   triggers to process/concatenate, as a string e.g. '0,400', '0,0 for a single file
#   probes to process, as a string, e.g. '0', '0,3', '0:3'

 
run_specs = [												
						['SC011_022319', '0', '0,2', '3']
]



json_directory = r'D:\ecephys_fork\json_files'

# delete the existing CatGT.log
try:
    os.remove('CatGT.log')
except OSError:
    pass


for spec in run_specs:

    session_id = spec[0]
    
    input_json = os.path.join(json_directory, session_id + '-input.json')
    output_json = os.path.join(json_directory, session_id + '-output.json')
    print( 'Creating json file for preprocessing')
    info = createInputJson(input_json, npx_directory=npx_directory, 
	                                   continuous_file = None,
                                       spikeGLX_data = 'True',
									   kilosort_output_directory=catGT_dest,
                                       catGT_run_name = session_id,
                                       gate_string = spec[1],
                                       trigger_string = spec[2],
                                       probe_string = spec[3],
                                       extracted_data_directory = catGT_dest
                                       )

    # Make list of probes from the probe string
    prb_list = SpikeGLX_utils.ParseProbeStr(spec[3])
    
    # CatGT operates on whole runs with multiple probes, so gets called in just
    # once per run_spec
    if run_preprocess:
        command = "python -W ignore -m ecephys_spike_sorting.modules." + 'catGT_helper' + " --input_json " + input_json \
		          + " --output_json " + output_json
        subprocess.check_call(command.split(' '))             

        # parse the CatGT log and write results to command line
        logPath = os.getcwd()
        gfix_edits = SpikeGLX_utils.ParseCatGTLog( logPath, spec[0], spec[1], prb_list )
    
        for i in range(0,len(prb_list)):
            edit_string = '{:.3f}'.format(gfix_edits[i])
            print('Probe ' + prb_list[i] + '; gfix edits/sec: ' + repr(gfix_edits[i]))
            
    # finsihed preprocessing. All other modules are are called once per probe
    
    # List of modules to run per probe
    modules = [
				'kilosort_helper',
                'kilosort_postprocessing',
                'noise_templates'
				]

    for prb in prb_list:
        #create json files specific to this probe
        session_id = spec[0] + '_imec' + prb
        input_json = os.path.join(json_directory, session_id + '-input.json')
        output_json = os.path.join(json_directory, session_id + '-output.json')  
        
        # location of the binary created by CatGT, using -out_prb_fld
        run_str = spec[0] + '_g' + spec[1]
        run_folder = 'catgt_' + run_str
        prb_folder =  run_str + '_imec' + prb
        data_directory = os.path.join(catGT_dest, run_folder, prb_folder)
        fileName = run_str + '_tcat.imec' + prb + '.ap.bin'
        continuous_file = os.path.join(data_directory, fileName)
        
        print(data_directory)
        print(continuous_file)
        
        info = createInputJson(input_json, npx_directory=npx_directory, 
	                                   continuous_file = continuous_file,
                                       spikeGLX_data = 'True',
									   kilosort_output_directory=data_directory,									   
                                       noise_template_use_rf = False,
                                       extracted_data_directory = catGT_dest
                                       )    
        for module in modules:
            command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json
            subprocess.check_call(command.split(' '))
        
        
        
	


    
