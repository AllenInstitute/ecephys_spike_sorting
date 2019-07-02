import subprocess
import shutil
import os
import time

from create_input_json import createInputJson

######################### UPDATE ME ###############################


npx_directories = [ r"J:\750332458_412791_20180910_probeA",
					r"K:\750332458_412791_20180910_probeB",
					r"L:\750332458_412791_20180910_probeC"
					]

start_modules = ['copy_raw_data'] * len(npx_directories)

for idx, npx_directory in enumerate(npx_directories):
	if start_modules[idx] in {'copy_raw_data','extract_from_npx'}:
		if os.path.isdir(npx_directory) == False:
			raise ValueError(npx_directory+' does not exist')
	else:
		sorted_directory = npx_directory + "_sorted"
		if os.path.isdir(sorted_directory) == False:
			raise ValueError(sorted_directory+' does not exist')

backup_drive = r'G:'

####################################################################

json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

def copy_processed_data_to_backup_drive(info):
	print("Copying processed data to backup drive...")
	extracted_data_location = info['directories']['extracted_data_directory']
	new_location = os.path.join(backup_drive, os.path.basename(extracted_data_location))
	shutil.copytree(extracted_data_location, new_location)

def copy_raw_data_to_backup_drive(npx_directory):
	print("Copying raw data to backup drive...")
	new_location = os.path.join(backup_drive, os.path.basename(npx_directory))
	shutil.copytree(npx_directory, new_location)

modules = ['copy_raw_data',
		   'extract_from_npx',
		   'depth_estimation',
		   'median_subtraction',
		   'kilosort_helper',
		   'noise_templates',
		   'mean_waveforms',
		   'quality_metrics',
		   'copy_processed_data',
		   ]

start_module_idxs = []
for module in start_modules:
	start_module_idxs.append(modules.index(module))

for idx, npx_directory in enumerate(npx_directories):

	try:

		for Midx, module in enumerate(modules):
			if Midx < start_module_idxs[idx]:
				print("skipping "+module)
			else:
				processes = []

				session_id = os.path.basename(npx_directory)

				input_json = os.path.join(json_directory, session_id + '_' + module + '-input.json')
				output_json = os.path.join(json_directory, session_id + '_' + module +'-output.json')

				info = createInputJson(input_json, npx_directory=npx_directory)

				command_string = ["python", "-W", "ignore", "-m", "ecephys_spike_sorting.modules." + module, 
							"--input_json", input_json,
				            "--output_json", output_json]

				print(command_string)

				if module == 'kilosort_helper':
					subprocess.check_call(command_string) # not in parallel -- requires GPU
				elif module == 'copy_processed_data':
					copy_processed_data_to_backup_drive(info) # not in parallel
				elif module == 'copy_raw_data':
					copy_raw_data_to_backup_drive(npx_directory)
				else:
					subprocess.check_call(command_string)
					#processes.append(subprocess.Popen(command_string)) # parallel

	except Exception as E:
		print(E)
		print("Error processing " + npx_directory)

		#for p in processes:
	#	while p.poll() is None: 
	#		time.sleep(0.5)



