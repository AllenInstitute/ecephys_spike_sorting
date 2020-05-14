import os
import subprocess

from create_input_json import createInputJson

sorted_directories = [	

	'/path/to/kilosort/outputs'					

]

probe_type = '3a'

json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

for directory in sorted_directories:

	session_id = os.path.basename(directory)

	input_json = os.path.join(json_directory, session_id + '-input.json')
	output_json = os.path.join(json_directory, session_id + '-output.json')

	info = createInputJson(input_json, kilosort_output_directory=directory)

	modules = [ #'extract_from_npx',
				#'depth_estimation'
				#'median_subtraction',
				#'kilosort_helper',
				#'kilosort_postprocessing'
				#'noise_templates',
				#'mean_waveforms',
				'quality_metrics'
				]


	for module in modules:

		command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json

		subprocess.check_call(command.split(' '))



