import subprocess
import shutil
import os
import time
import psutil
from collections import namedtuple, 
from pprint import pprint
from recordclass import recordclass
import datetime

from create_input_json import createInputJson

npx_params = namedtuple('npx_params',['backup_location','start_module','end_module'])

backup_drive = r'I:'
default_start = 'copy_raw_data'
default_end = 'copy_processed_data'

npx_directories = {r'J:\759883607_412799_20181002_probeA':npx_params(backup_drive,default_start,default_end),
					r'K:\759883607_412799_20181002_probeB':npx_params(backup_drive,default_start,default_end),
					r'L:\759883607_412799_20181002_probeC':npx_params(backup_drive,default_start,default_end)
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
process_dict = {}
warning_dict = {}
def copy_processed_data_to_backup_drive(info, npx_directory):
	print("Copying processed data to backup drive...")
	extracted_data_location = info['directories']['extracted_data_directory']
	drive = npx_directories[npx_directory].backup_location
	new_location = os.path.join(drive, os.path.basename(extracted_data_location))
	try:
		os.mkdir(new_location)
	except Exception as E:
		print("WARNING: Processed files were not copied if they already existed.")
		try:
			warning_dict[npx_directory].append("WARNING: Processed files were not copied if they already existed.")
		except KeyError as E:
			warning_dict[npx_directory]=("WARNING: Processed files were not copied if they already existed.")
	command_string = "robocopy "+ extracted_data_location +" "+new_location +r" /e /xc /xn /xo"
	print(command_string)
	process_dict[npx_directory].append(subprocess.Popen(command_string))
		#shutil.copytree(extracted_data_location, new_location)


def copy_raw_data_to_backup_drive(npx_directory):
	print("Copying raw data to backup drive...")
	drive = npx_directories[npx_directory].backup_location
	new_location = os.path.join(drive, os.path.basename(npx_directory))
	print(new_location)
	try:
		os.mkdir(new_location)
	except Exception as E:
		print("WARNING: Raw files were not copied if they already existed.")
		try:
			warning_dict[npx_directory].append("WARNING: Raw files were not copied if they already existed.")
		except KeyError:
			warning_dict[npx_directory]=("WARNING: Raw files were not copied if they already existed.")
	command_string = "robocopy "+ npx_directory +" "+new_location +r" /e /xc /xn /xo"
	print(command_string)
	process_dict[npx_directory].append(subprocess.Popen(command_string))
	#shutil.copytree(npx_directory, new_location)


#TODO change format so there is a process state dict to make things more self documenting
finished_list = [1]*len(npx_directories)
current_modules = [False]*len(npx_directories)
info_dict = {}
failed_dict = {}
module_info = recordclass('module_info', ['rcode', 'output', 'error','start_time','end_time' ])


for npx_directory in npx_directories:
	info_dict[npx_directory] = {}
	failed_dict[npx_directory] = 0
	process_dict[npx_directory] = []

while sum(finished_list) > 0:

	for idx, npx_directory in enumerate(npx_directories):
		busy = False
		for p in process_dict[npx_directory]:
			if p.poll() is None:
				busy = True	
		if not busy and current_modules[idx]:
			if info_dict[npx_directory][current_modules[idx]].rcode == None:
				try:
					p = process_dict[npx_directory][-1]
					output,error  = p.communicate()
					now = datetime.datetime.now()
					info_dict[npx_directory][current_modules[idx]]._replace(rcode = p.returncode, output = p.output, error = p.error, end_time = now)
					if p.returncode is not 0:
						failed_dict[npx_directory] = 1
				except IndexError as E:
					pass	
		try:
			next_module_idx = modules.index(current_modules[idx])+1
			next_module =  modules[next_module_idx]
		except ValueError as E:
			next_module = npx_directories[npx_directory].start_module	
		kilosort_wait = next_module == 'kilosort_helper' and 'kilosort_helper' in current_modules
		if (current_modules[idx] == npx_directories[npx_directory].end_module) and info_dict[npx_directory][current_modules[idx]].rcode is not None:	
			finished_list[idx] = 0
		if  not(busy) and not(kilosort_wait) and not finished_list[idx] and (failed_dict[npx_directory]==0 or next_module == 'copy_processed_data'):

			print("initiating "+next_module+" for "+npx_directory)
			current_modules[idx] = next_module
			now = datetime.datetime.now()
			info_dict[npx_directory][current_modules[idx]] = module_info(None,None,None,now,None)
			module = next_module
			try:
				session_id = os.path.basename(npx_directory)

				input_json = os.path.join(json_directory, session_id + '_' + module + '-input.json')
				output_json = os.path.join(json_directory, session_id + '_' + module +'-output.json')

				info = createInputJson(npx_directory, input_json)

				command_string = ["python", "-m", "ecephys_spike_sorting.modules." + module, 
							"--input_json", input_json,
				            "--output_json", output_json]

				print(command_string)

				if module == 'copy_processed_data':
					copy_processed_data_to_backup_drive(info,npx_directory)
				elif module == 'copy_raw_data':
					copy_raw_data_to_backup_drive(npx_directory)
				elif module == 'extract_from_npx':
					recording_size = sum(os.path.getsize(os.path.join(npx_directory,recording)) for recording in os.listdir(npx_directory))
					backup_location = os.path.join(npx_directories[npx_directory].backup_location,os.path.basename(npx_directory))
					backup_size = sum(os.path.getsize(os.path.join(backup_location,recording)) for recording in os.listdir(npx_directory))
					if not recording_size == backup_size:
						raise ValueError('One of the backups failed')
					else:
						process_dict[npx_directory].append(subprocess.Popen(command_string))
				#TODO check median subtraction doesn't fail as well? before starting kilosort?
				else:
					process_dict[npx_directory].append(subprocess.Popen(command_string, stdout = subprocess.PIPE, stderr = subprocess.PIPE)) # parallel

			except Exception as E:
				print("Error processing " + npx_directory)
				failed_dict[npx_directory] = [module,E]
				finished_list[idx] = 0
		time.sleep(0.5)

pprint(warning_dict)
pprint(failed_dict)
for npx_directory in npx_directories:
	for module, info in info_dict[npx_directory].items:
		print(npx_directory,": ",module)
		print("Start time: ", info.start_time, " End_time: ", info.end_time, )

#Then once we know what the exit codes shoule be we can halt kilosort if ms fails