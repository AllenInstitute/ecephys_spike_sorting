import os
import subprocess

from create_input_json import createInputJson

input_test_directory = ['/Volumes/sd4/766640955_412804_20181022/766640955_412804_20181022_probeC_sorted/continuous/Neuropix-3a-100.0']
#npx_directories = [r'L:\766640955_412804_20181022_probeC']
output_test_directory = '/Users/xiaoxuanj/work/work_allen/Ephys/module_test/spike_sorting_test'

probe_type = '3A'

json_directory = '/Users/xiaoxuanj/work/work_allen/Ephys/module_test/input_json'
#json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

for directory in input_test_directory:

	session_id = os.path.basename(directory)

	input_json = os.path.join(json_directory, session_id + '-input.json')
	output_json = os.path.join(json_directory, session_id + '-output.json')

	info = createInputJson(input_json, 
		kilosort_output_directory=directory, 
		kilosort_output_tmp=output_test_directory)

	modules = [ #'extract_from_npx',
				#'depth_estimation',
				#'median_subtraction',
				#'kilosort_helper',
				#'kilosort_postprocessing',
				#'noise_templates',
				'mean_waveforms',
				'quality_metrics']

	for module in modules:

		command = "python -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json

		subprocess.check_call(command.split(' '))