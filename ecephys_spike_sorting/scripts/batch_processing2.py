import subprocess
import shutil
import os
import time

from create_input_json import createInputJson

#import ecephys_spike_sorting.modules.extract_from_npx as extract_from_npx

npx_files = [r'E:\704514354_380485_20180601_probeF\recording1.npx', 
             r'E:\704514354_380485_20180601_probeE\recording1.npx',
             r'E:\704514354_380485_20180601_probeD\recording1.npx']

json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

def copy_data_to_backup_drive(info):
	extracted_data_location = info['directories']['extracted_data_directory']
	new_location = os.path.join(r'E:', os.path.basename(extracted_data_location))
	shutil.move(extracted_data_location, new_location)

modules = ('noise_templates', 'mean_waveforms', 'quality_metrics')

for module in modules:

	processes = []

	for idx, npx_file in enumerate(npx_files):

		if idx != 1:

			probe_directory = os.path.dirname(npx_file)
			session_id = os.path.basename(probe_directory)

			input_json = os.path.join(json_directory, session_id + '_' + module + '-input.json')
			output_json = os.path.join(json_directory, session_id + '_' + module +'-output.json')

			info = createInputJson(npx_file, input_json)

			command_string = ["python", "-m", "ecephys_spike_sorting.modules." + module, 
						"--input_json", input_json,
			            "--output_json", output_json]

			print(command_string)

			# launch sub-processes for each file
			if module != 'kilosort_helper':
				processes.append(subprocess.Popen(command_string))
			else:
				subprocess.check_call(command)


	for p in processes:
		while p.poll() is None: 
			time.sleep(0.5)

	#copy_data_to_backup_drive(info)

	#stop




