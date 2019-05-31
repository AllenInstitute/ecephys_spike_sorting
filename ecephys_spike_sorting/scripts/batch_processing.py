import os
import subprocess

from create_input_json import createInputJson

npx_files = [r'L:\766640955_412804_20181022_probeC\recording1.npx']

json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

for npx_file in npx_files:

	probe_directory = os.path.dirname(npx_file)
	session_id = os.path.basename(probe_directory)

	input_json = os.path.join(json_directory, session_id + '-input.json')
	output_json = os.path.join(json_directory, session_id + '-output.json')

	kilosort_output_directory = os.path.join(os.path.dirname(npx_file) + '_sorted', 'continuous','Neuropix-PXI-100.0')

	info = createInputJson(os.path.dirname(npx_file), kilosort_output_directory, input_json)

	commands = (#'depth_estimation', 
				'kilosort_helper',
				'kilosort_postprocessing',
				'noise_templates',
				'mean_waveforms',
				'quality_metrics')

	for command in commands:

		command = "python -m ecephys_spike_sorting.modules." + command + " --input_json " + input_json \
		          + " --output_json " + output_json

		subprocess.check_call(command.split(' '))



