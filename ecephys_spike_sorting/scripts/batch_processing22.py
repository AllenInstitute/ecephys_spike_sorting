import subprocess
import shutil
import os
import time
import psutil
from collections import namedtuple

from create_input_json import createInputJson

npx_params = namedtuple('npx_params',['backup_location','start_module','end_module'])

backup_drive = r'I:'
default_start = 'copy_raw_data'
default_end = 'copy_processed_data'

npx_directories = {r'J:\762602078_408152_20181011_probeA':npx_params(backup_drive,default_start,default_end),
					r'K:\762602078_408152_20181011_probeA':npx_params(backup_drive,default_start,default_end),
					r'L:\762120172_410343_20181010_probeC':npx_params(backup_drive,default_start,default_end)
					}

######################################################################################

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

npx_module_dict = {}
for dirname,params in npx_directories.items():
	module_list = []
	start_num = modules.index(params.start_module)
	end_num = modules.index(params.end_module)
	for idx, module in enumerate(modules):
		if idx >= start_num and idx <= end_num:
			module_list.append(module)
	npx_module_dict[dirname] = module_list

backup_size_dict = {}
max_c_space_needed = 0
def dir_size(dir_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

for npx_directory,params in npx_directories.items():
	module_list = npx_module_dict[npx_directory]
	copy_raw = 'copy_raw_data' in module_list
	copy_processed = 'copy_processed_data' in module_list
	kilosort='kilosort_helper' in module_list
	extract = 'extract_from_npx' in module_list
	drive, dirname = os.path.split(npx_directory)
	sorted_dirname = dirname+"_sorted"
	sorted_dir = os.path.join(drive,sorted_dirname)
	sorted_backup_dir = os.path.join(params.backup_location,sorted_dirname)
	free_space = psutil.disk_usage(os.path.splitdrive(npx_directory)[0]).free
	if 'copy_raw_data' in npx_module_dict[npx_directory] or 'extract_from_npx' in npx_module_dict[npx_directory]:
		try:
			recording_size = sum(os.path.getsize(os.path.join(npx_directory,recording)) for recording in os.listdir(npx_directory))
			extracted_size = 1.4*recording_size
		except FileNotFoundError as E:
			print('One of the directories probably doesn\'t exist - check '+npx_directory)
			raise E
	else: 
		try:
			recording_size = 0
			if os.path.isdir(sorted_dir):
				extracted_size = dir_size(sorted_dir)
			else:
				raise FileNotFoundError
		except FileNotFoundError as E:
			print('One of the directories probably doesn\'t exist - check '+sorted_dir)
			raise E
	processing_size = (30*(10**9))
	try:
		current_processed_backup = dir_size(sorted_backup_dir)
	except Exception:
		current_processed_backup = 0

	backup_space_needed = copy_raw*recording_size + copy_processed*(processing_size+max(0,extracted_size-current_processed_backup))
	c_space_needed = kilosort*extracted_size
	data_space_needed = extract*extracted_size + processing_size
	try:
		backup_size_dict[params.backup_location] += backup_space_needed
	except:
		backup_size_dict[params.backup_location] = backup_space_needed
	max_c_space_needed = max(c_space_needed,max_c_space_needed)
	if free_space < data_space_needed:
		print('check ' +npx_directory)
		raise ValueError('There is not enough space on one of the drives')
	print(npx_directory+' exist and there appears to be enough disk space free for processing')

if psutil.disk_usage(r'C:').free < max_c_space_needed:
	raise ValueError('There is not enough space on the C drive for kilosort to process the largest dataset')
else: print('There appears to be enough space on the C drive for kilosort')
for bdrive, size_needed in backup_size_dict.items():
	if psutil.disk_usage(bdrive).free < size_needed:
		raise ValueError('There is not enough space on the backup drive for all the data')
	else: print('And there appears to be enough space on backup drive '+bdrive)
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