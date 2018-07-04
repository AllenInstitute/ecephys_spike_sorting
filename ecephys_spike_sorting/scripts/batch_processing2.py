import subprocess
import shutil
import os
import time

from create_input_json import createInputJson

######################### UPDATE ME ###############################

npx_files = [r'E:\703270608_380480_20180529_probeC\recording1.npx', 
             r'E:\703270608_380480_20180529_probeB\recording1.npx']

####################################################################

json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

def copy_data_to_backup_drive(info):
	extracted_data_location = info['directories']['extracted_data_directory']
	new_location = os.path.join(r'E:', os.path.basename(extracted_data_location))
	shutil.move(extracted_data_location, new_location)


modules = ('extract_from_npx', 
		   'depth_estimation',
		   'median_subtraction',
		   'kilosort_helper',
		   'noise_templates',
		   'mean_waveforms',
		   'quality_metrics',
		   'copy_data')

for module in modules:

	processes = []

	for idx, npx_file in enumerate(npx_files):

		probe_directory = os.path.dirname(npx_file)
		session_id = os.path.basename(probe_directory)

		input_json = os.path.join(json_directory, session_id + '_' + module + '-input.json')
		output_json = os.path.join(json_directory, session_id + '_' + module +'-output.json')

		info = createInputJson(npx_file, input_json)

		command_string = ["python", "-m", "ecephys_spike_sorting.modules." + module, 
					"--input_json", input_json,
		            "--output_json", output_json]

		print(command_string)

		if module == 'kilosort_helper':
			subprocess.check_call(command_string) # not in parallel -- requires GPU
		elif module == 'copy_data':
			copy_data_to_backup_drive(info) # not in parallel
		else:
			processes.append(subprocess.Popen(command_string)) # parallel

	for p in processes:
		while p.poll() is None: 
			time.sleep(0.5)



