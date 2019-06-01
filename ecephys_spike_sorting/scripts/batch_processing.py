import os
import subprocess

from create_input_json import createInputJson

sorted_directories = ['/mnt/md0/data/mouse412804/766640955_412804_20181022_probeC_sorted/continuous/Neuropix-3a-100.0']

probe_type = '3A'

json_directory = '/mnt/md0/data/json_files'

for directory in sorted_directories:

	path = os.path.normpath(directory)
	session_id = path.split(os.sep)[4]

	input_json = os.path.join(json_directory, session_id + '-input.json')
	output_json = os.path.join(json_directory, session_id + '-output.json')

	info = createInputJson(None, directory, input_json, probe_type)

	modules = [#'kilosort_postprocessing',
				#'noise_templates',
				#'mean_waveforms',
				'quality_metrics']

	for module in modules:

		command = "python -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json

		subprocess.check_call(command.split(' '))



