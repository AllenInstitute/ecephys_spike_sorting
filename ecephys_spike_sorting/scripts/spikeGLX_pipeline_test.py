import os
import shutil
import subprocess

from helpers import SpikeGLX_utils
from create_input_json import createInputJson

run_preprocess = True   # set to False to rerun KS2 or processing on previously processed data.

# batch file catGT_helper module for a set of runs in the 
# directory npx_directory. Gate, trigger, probes to process are set
# in the run_spec
# Other CatGT params are set in catGT_stream_string and catGT_cmd_string

npx_directory = r'D:\ecephys_fork\test_data\SC_trial'

# Set to an existing directory to send all output to a new directory. It will then have 
# the standard SpikeGLX directory structure: run_folder/probe_folder/*.bin

catGT_dest = r'D:\ecephys_fork\test_data\SC_trial\CatGT_out'

# Each run_spec is a list of 4 strings:
#   undecorated run name (no g/t specifier, the run field in CatGT)
#   gate index, as a string (e.g. '0')
#   triggers to process/concatenate, as a string e.g. '0,400', '0,0 for a single file
#   probes to process, as a string, e.g. '0', '0,3', '0:3'

 
run_specs = [												
						['SC024_092319_NP1.0_Midbrain', '0', '0,4', '0,1']
]

# catGT streams to process, e.g. just '-ap' for ap band only, '-ap -ni' for 
# ap plus ni aux inputs
catGT_stream_string = '-ap -ni'

# CatGT command string includes all instructions for catGT operations
# see CatGT readme for details
catGT_cmd_string = '-prb_fld -out_prb_fld -aphipass=300 -aplopass=9000 -gbldmx -gfix=0,0.10,0.02 -SY=0,384,6,500 -SY=1,384,6,500 -XA=0,1,3,500 -XA=1,3,3,0 -XD=4,1,50 -XD=4,2,1.7 -XD=4,3,5'

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
                                       catGT_stream_string = catGT_stream_string,
                                       catGT_cmd_string = catGT_cmd_string,
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

    for i, prb in enumerate(prb_list):
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
        
        outputName = 'imec' + prb + '_ks2'
        
        # kilosort_postprocessing and noise_templates moduules alter the files
        # that are input to phy. If using these modules, keep a copy of the
        # original phy output
        if ('kilosort_postprocessing' in modules) or('noise_templates' in modules):
            ks_make_copy = True
        else:
            ks_make_copy = False
            
        kilosort_output_dir = os.path.join(data_directory, outputName)
        
        print(data_directory)
        print(continuous_file)
        
        info = createInputJson(input_json, npx_directory=npx_directory, 
	                                   continuous_file = continuous_file,
                                       spikeGLX_data = True,
									   kilosort_output_directory=kilosort_output_dir,
                                       ks_make_copy = ks_make_copy,
                                       noise_template_use_rf = False,
                                       catGT_run_name = session_id,
                                       gate_string = spec[1],
                                       trigger_string = spec[2],
                                       probe_string = spec[3],
                                       catGT_stream_string = catGT_stream_string,
                                       catGT_cmd_string = catGT_cmd_string,
                                       catGT_gfix_edits = gfix_edits[i],
                                       extracted_data_directory = catGT_dest
                                       )
        
        # copy json file to data directory as record of the input parameters (and gfix edit rates)  
        shutil.copy(input_json, os.path.join(data_directory, session_id + '-input.json'))
        
        for module in modules:
            command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json
            subprocess.check_call(command.split(' '))
        
        
        
	


    
