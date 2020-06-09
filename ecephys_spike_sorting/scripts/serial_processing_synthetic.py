import os
import subprocess
import shutil
from create_input_json import createInputJson
import time

#time.sleep(14400)
sorted_directories = [r'G:\766640955_412804_20181022_probeC_sorted\continuous\Neuropix-3a-100.0']
#npx_directories = [r'L:\766640955_412804_20181022_probeC']

probe_type = 'PXI'

#json_directory = '/mnt/md0/data/json_files'
json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

for directory in sorted_directories:

	session_id = os.path.basename(directory)

	input_json = os.path.join(json_directory, session_id + '-input.json')
	output_json = os.path.join(json_directory, session_id + '-output.json')

	info = createInputJson(input_json, kilosort_output_directory=directory,
									   extracted_data_directory=directory)

	modules = [ #'extract_from_npx',
				#'depth_estimation',
				##'median_subtraction',
				#'kilosort_helper',
				#'kilosort_postprocessing',
				#'noise_templates',
				#'mean_waveforms',
				'quality_metrics'
				]

	for module in modules:
		for name in os.listdir(directory):
			path = os.path.join(directory, name)
			if ('manipulated' in name) and os.path.isdir(path):
				try:
					src = os.path.join(path, 'spike_clusters.npy')
					dest = os.path.join(directory, 'spike_clusters.npy')
					shutil.copyfile(src, dest)
					command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
					          + " --output_json " + output_json

					subprocess.check_call(command.split(' '))
					src = os.path.join(directory, 'new_metrics.csv')#'spike_clusters.npy')
					dest = os.path.join(path, 'new_metrics.csv')#'spike_clusters.npy')
					shutil.move(src, dest)
				except Exception as E:
					print(E)



