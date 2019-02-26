import subprocess
import shutil
import os
import time
import psutil

from create_input_json import createInputJson

npx_directories = [r'J:\757970808_412793_20180925_probeA',
					r'K:\757970808_412793_20180925_probeB',
					r'L:\757970808_412793_20180925_probeC'
					]

backup_drive = r'H:'

total_size = 0
max_size = 0
for idx, npx_directory in enumerate(npx_directories):
	try:
		free_space = psutil.disk_usage(npx_directory).free
		recording_size = sum(os.path.getsize(os.path.join(npx_directory,recording)) for recording in os.listdir(npx_directory))
		processed_size = (recording_size*1.4+(30*(10**9)))
		total_size = total_size+processed_size+recording_size
		max_size = max(max_size,recording_size)
		if free_space < processed_size:
			raise ValueError('There is not enough space on one of the drives')
		print(npx_directory+' exist and there appears to be enough disk space free for processing')
	except Exception as E:
		print('One of the directories probably doesn\'t exist - check '+npx_directory)
		raise E

if psutil.disk_usage(r'C:').free < max_size:
	raise ValueError('There is not enough space on the C drive for kilosort to process the largest dataset')
else: print('There appears to be enough space on the C drive for kilosort')
if psutil.disk_usage(backup_drive).free < total_size:
	raise ValueError('There is not enough space on the backup drive for all the data')
else: print('And there appears to be enough space on backup drive '+backup_drive)

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
		   'copy_processed_data'
		   ]

failed = [0]*len(npx_directories)

for module in modules:

	processes = []

	for idx, npx_directory in enumerate(npx_directories):
		if failed[idx]==0:
			try:
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
				elif module == 'copy_processed_data':
					copy_processed_data_to_backup_drive(info) # not in parallel
				elif module == 'copy_raw_data':
					copy_raw_data_to_backup_drive(npx_directory)
				else:
					#subprocess.check_call(command_string)
					processes.append(subprocess.Popen(command_string)) # parallel

			except:
				print("Error processing " + npx_directory)
				failed[idx] = 1

	for p in processes:
		while p.poll() is None: 
			time.sleep(0.5)