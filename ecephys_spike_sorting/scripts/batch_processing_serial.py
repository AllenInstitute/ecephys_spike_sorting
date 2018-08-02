import subprocess
import shutil
import os
import time

from create_input_json import createInputJson

######################### UPDATE ME ###############################

npx_directories = [ r"J:\727666025_394208_20180731_probeA",
					r"K:\727666025_394208_20180731_probeB",
					r"L:\727666025_394208_20180731_probeC"]


####################################################################

json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

def copy_processed_data_to_backup_drive(info):
	extracted_data_location = info['directories']['extracted_data_directory']
	new_location = os.path.join(r'D:', os.path.basename(extracted_data_location))
	shutil.move(extracted_data_location, new_location)

def copy_raw_data_to_backup_drive(npx_directory):
	new_location = os.path.join(r'D:', os.path.basename(npx_directory))
	shutil.copy(npx_directory, new_location)


modules = ('extract_from_npx',
		   'depth_estimation',
		   'median_subtraction',
		   'kilosort_helper',
		   'noise_templates',
		   'mean_waveforms',
		   'quality_metrics',
		   'copy_data')

for idx, npx_directory in enumerate(npx_directories):

	copy_data_to_backup_drive(npx_directory)

	try:

		for module in modules:

			processes = []

			session_id = os.path.basename(npx_directory)

			input_json = os.path.join(json_directory, session_id + '_' + module + '-input.json')
			output_json = os.path.join(json_directory, session_id + '_' + module +'-output.json')

			info = createInputJson(npx_directory, input_json)

			command_string = ["python", "-m", "ecephys_spike_sorting.modules." + module, 
						"--input_json", input_json,
			            "--output_json", output_json]

			print(command_string)

			if module == 'kilosort_helper':
				subprocess.check_call(command_string) # not in parallel -- requires GPU
			elif module == 'copy_data':
				copy_data_to_backup_drive(info) # not in parallel
			else:
				subprocess.check_call(command_string)
				#processes.append(subprocess.Popen(command_string)) # parallel
	except:
		print("Error processing " + npx_directory)

		#for p in processes:
	#	while p.poll() is None: 
	#		time.sleep(0.5)



