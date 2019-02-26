import subprocess
import shutil
import os
import time
import psutil
from collections import namedtuple, OrderedDict
from pprint import pprint
from recordclass import recordclass
import datetime
import logging
logging.basicConfig(level = logging.DEBUG)


from cleanup.check_data_processing import postprocessing, check_data_processing
from create_input_json import createInputJson

npx_params = namedtuple('npx_params',['start_module','end_module','backup1','backup2'])

default_backup1 = r'\\sd4\SD4\715093703_386129_20180627'#r'Q:'
default_backup2 = r'\\sd4\SD4\715093703_386129_20180627'
default_start = 'primary_backup_raw_data'
default_end = 'secondary_backup_processed_data'
json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

npx_directories = OrderedDict()
npx_directories[r'J:\715093703_386129_20180627_probeA']=npx_params(default_start,default_end,default_backup1,default_backup2)
npx_directories[r'K:\715093703_386129_20180627_probeB']=npx_params(default_start,default_end,default_backup1,default_backup2)
#npx_directories[r'L:\797828357_421529_20181218_probeC']=npx_params('kilosort_helper',default_end,default_backup1,default_backup2)

######################################################################################

modules = [
		   'primary_backup_raw_data',
		   'extract_from_npx',
		   'depth_estimation',
		   'median_subtraction',
		   'kilosort_helper',
		   'noise_templates',
		   'mean_waveforms',
		   'quality_metrics',
		   'primary_backup_processed_data',
		   'secondary_backup_raw_data',
		   'secondary_backup_processed_data'#,
		   #'cleanup'
		   ]

copy_while_waiting_modules = [
			'copy_while_waiting_primary',
			'copy_while_waiting_secondary_raw',
			'copy_while_waiting_secondary_processed'
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
	sorted_backup_dir = os.path.join(params.backup1,sorted_dirname)
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
		backup_size_dict[params.backup1] += backup_space_needed
	except:
		backup_size_dict[params.backup1] = backup_space_needed
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


def copy_data(source, destination, npx_directory,module):
	logger_dict[npx_directory].info("{} Copying data from {} to {} ...".format(module,source,destination))
	try:
		os.mkdir(destination)
	except Exception as E:
		logger_dict[npx_directory].warning("For "+module+" files were not copied if they already existed.")
		try:
			warning_dict[npx_directory].append("WARNING: For "+module+" files were not copied if they already existed.")
		except KeyError as E:
			warning_dict[npx_directory]=["WARNING: For "+module+" files were not copied if they already existed."]
	command_string = "robocopy "+ source +" "+destination +r" /e /xc /xn /xo"
	logger_dict[npx_directory].info(command_string)
	process_dict[npx_directory].append(subprocess.Popen(command_string))#,stdout = subprocess.PIPE,stderr = subprocess.PIPE))
		#shutil.copytree(extracted_data_location, new_location)

def initiate_copy_while_waiting_module(info_dict, npx_directory, current_modules, copy_while_waiting_modules,idx):
	completed_modules = info_dict[npx_directory]
	next_module = False
	module_info = False
	failed = False
	for module in copy_while_waiting_modules:
		if not(module in completed_modules):
			next_module = module
			break
	network_modules = {'copy_while_waiting_secondary_raw',
			'copy_while_waiting_secondary_processed',		   
			'secondary_backup_raw_data',
		   'secondary_backup_processed_data'}
	other_modules = current_modules[:idx]+current_modules[idx+1:]
	network_busy = set(other_modules).intersection(network_modules)
	if next_module and not network_busy:
		next_module, module_info, failed = initiate_next_module(next_module, npx_directory, json_directory)
	else: next_module = False
	return next_module, module_info, failed

def initiate_next_module(next_module, npx_directory, json_directory):
	logger_dict[npx_directory].info('initiating {} for {}'.format(next_module,npx_directory))
	now = datetime.datetime.now()
	this_module_info = module_info(None,None,None,now,None)
	failed = 0
	try:
		session_id = os.path.basename(npx_directory)
		input_json = os.path.join(json_directory, session_id + '_' + next_module + '-input.json')
		output_json = os.path.join(json_directory, session_id + '_' + next_module +'-output.json')
		info = createInputJson(npx_directory, input_json)
		command_string = ["python", "-m", "ecephys_spike_sorting.modules." + next_module, 
								"--input_json", input_json,
					            "--output_json", output_json]
		logger_dict[npx_directory].info(command_string)
		start_module(npx_directory,next_module, command_string, info)
	except Exception as E:
		logger_dict[npx_directory].error("Error initiating " + next_module+" for " +npx_directory)
		logger_dict[npx_directory].exception(E)
		failed = 1
	return next_module, this_module_info, failed

def start_module(npx_directory, module, command_string, info):
	if module == 'primary_backup_raw_data':
		drive = npx_directories[npx_directory].backup1
		new_location = os.path.join(drive, os.path.basename(npx_directory))
		copy_data(npx_directory,new_location, npx_directory,module)
	elif module == 'primary_backup_processed_data' or module == 'copy_while_waiting_primary':
		extracted_data_location = info['directories']['extracted_data_directory']
		drive = npx_directories[npx_directory].backup1
		new_location = os.path.join(drive, os.path.basename(extracted_data_location))
		copy_data(extracted_data_location,new_location, npx_directory,module)
	elif module == 'secondary_backup_raw_data' or module == 'copy_while_waiting_secondary_raw':
		drive = npx_directories[npx_directory].backup2
		new_location = os.path.join(drive, os.path.basename(npx_directory))
		copy_data(npx_directory,new_location, npx_directory,module)
	elif module == 'secondary_backup_processed_data' or module == 'copy_while_waiting_secondary_processed':
		extracted_data_location = info['directories']['extracted_data_directory']
		drive = npx_directories[npx_directory].backup2
		new_location = os.path.join(drive, os.path.basename(extracted_data_location))
		copy_data(extracted_data_location, new_location, npx_directory,module)
	elif module == 'cleanup':
		check_data_processing(npx_directory,npx_directories[npx_directory])
		logger_dict[npx_directory].info('finished cleanup, no exit status to fetch')
		info_dict[npx_directory]['cleanup']._replace(rcode = None, output = None, error = None, endtime = datetime.datetime.now())
	elif module == 'extract_from_npx':
		try:
			recording_size = sum(os.path.getsize(os.path.join(npx_directory,recording)) for recording in os.listdir(npx_directory))
			backup_location = os.path.join(npx_directories[npx_directory].backup1,os.path.basename(npx_directory))
			backup_size = sum(os.path.getsize(os.path.join(backup_location,recording)) for recording in os.listdir(npx_directory))
			if not recording_size == backup_size:
				raise ValueError('One of the backups failed')
			else:
				process_dict[npx_directory].append(subprocess.Popen(command_string))#, stdout = subprocess.PIPE,stderr = subprocess.PIPE))
		except Exception as E:
			logger_dict[npx_directory].exception("Unable to verify raw backup of "+ npx_directory+" before extracting. If verification is not needed comment out this portion of the script")
			raise(E)
	else:
		process_dict[npx_directory].append(subprocess.Popen(command_string))#, stdout = subprocess.PIPE,stderr = subprocess.PIPE))

def get_next_module(current_module,npx_directory):
	try:
		if current_module in copy_while_waiting_modules:
			next_module = 'kilosort_helper'
		else:	
			next_module_idx = modules.index(current_module)+1
			next_module =  modules[next_module_idx]
	except (ValueError,IndexError) as E:
		if current_module:
			next_module = npx_directories[npx_directory].end_module
		else:
			next_module = npx_directories[npx_directory].start_module
	return next_module

def log_out(p,logger):
	try:
		p.stdout.seek(0,2)
		pos = p.stdout.tell()
		output = []
		if pos:
			tot_read = 0
			while tot_read < pos:
				line = p.stdout.readline()
				logger.info(line.rstrip())
				tot_read = tot_read +len(line)
	except ValueError as E:
		logger.warning('Failed to read stdout',exc_info = True)

def log_progress(npx_directory):
	if info_dict[npx_directory][current_modules[idx]].rcode == None and not(current_modules[idx] == 'cleanup'):
		p = process_dict[npx_directory][-1]
		#out_list = log_out(p,logger_dict[npx_directory])
	#for line in out_list: logger_dict[npx_directory].info(line)
		if not(busy):
			logger_dict[npx_directory].info("fetching exit status and info for"+current_modules[idx]+npx_directory)
			try:
				output,error  = p.communicate()
				now = datetime.datetime.now()
				info_dict[npx_directory][current_modules[idx]]._replace(rcode = p.returncode, output = output, error = error, endtime = now)
				logger_dict[npx_directory].info("finished fetching exit status and info for "+ current_modules[idx]+" "+npx_directory)
				copy_modules = {
							'primary_backup_raw_data',
					   'primary_backup_processed_data',
					   'secondary_backup_raw_data',
					   'secondary_backup_processed_data',							
						'copy_while_waiting_primary',
						'copy_while_waiting_secondary_raw',
						'copy_while_waiting_secondary_processed'
				}
				robocopy = current_modules[idx] in copy_modules
				print(robocopy)
				if not(p.returncode == 0) and not(robocopy and p.returncode < 4):
					failed_dict[npx_directory] == 1
					logger_dict[npx_directory].error("return code "+str(p.returncode)+" for "+ current_modules[idx]+" "+npx_directory)
					try:
						for line in error.splitlines():
							logger_dict[npx_directory].error(line)
					except Exception as E:
						logger_dict[npx_directory].info('No output to print')
					logger_dict[npx_directory].info("setting "+ npx_directory+ "status to failed ")
			except IndexError as E:
				logger_dict[npx_directory].exception('There was an error fetching the exit status for '+npx_directory)
				pass	

def create_file_handler(level_string,level_idx,limsID,probe):
	file_name = limsID+'_'+datetime.datetime.now().strftime("%y.%m.%d.%I.%M.%S")+'_'+level_string+'_'+probe+".log"
	log_file = os.path.join(json_directory,file_name)
	file_handler = logging.FileHandler(log_file)

	file_handler.setLevel(level_idx)
	file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
	return file_handler

def create_logger(npx_directory):
	full_session_id = os.path.basename(npx_directory)
	limsID = full_session_id.split('_')[0]
	probe = full_session_id.split('_')[-1]
	name_string = '_'.join([limsID, probe])
	mylogger = logging.getLogger(name_string)
	error_file_handler = create_file_handler('error',logging.ERROR,limsID,probe)
	info_file_handler = create_file_handler('info',logging.DEBUG,limsID,probe)
	mylogger.addHandler(error_file_handler)
	mylogger.addHandler(info_file_handler)
	#stream_handler = logging.StreamHandler()
	#stream_handler.setLevel(logging.INFO)
	#mylogger.addHandler(stream_handler)
	return mylogger

#TODO change format so there is a process state dict to make things more self documenting? might be worse...
process_dict = {}
warning_dict = {}
logger_dict = {}
finished_list = [0]*len(npx_directories)
current_modules = [False]*len(npx_directories)
copy_while_waiting = [False]*len(npx_directories)
info_dict = {}
failed_dict = {}
module_info = recordclass('module_info', ['rcode', 'output', 'error','starttime','endtime' ])

for npx_directory in npx_directories:
	logger_dict[npx_directory] = create_logger(npx_directory)
	info_dict[npx_directory] = {}
	failed_dict[npx_directory] = 0
	process_dict[npx_directory] = []

start = datetime.datetime.now()

while sum(finished_list) < len(npx_directories):

	for idx, npx_directory in enumerate(npx_directories):
		#print('looping')
		busy = False

		for p in process_dict[npx_directory]:
			if p.poll() is None:
				busy = True
		next_module = get_next_module(current_modules[idx],npx_directory)

		if current_modules[idx]:
			log_progress(npx_directory)

		time_elapsed =  (datetime.datetime.now()-start).seconds
		copy_wait = next_module == 'primary_backup_raw_data' and current_modules.count('primary_backup_raw_data')>0 and time_elapsed<1200*idx
		#TODO edit copy wait so it waits extra long to copy down if there is another drive letter already working, and estimates the expected time instaed of just 20 minutes
		kilosort_wait = next_module == 'kilosort_helper' and 'kilosort_helper' in current_modules
		wait = kilosort_wait or copy_wait

		if not(busy) and kilosort_wait:
			next_module, next_module_info ,copy_failed = initiate_copy_while_waiting_module(info_dict, npx_directory, current_modules, copy_while_waiting_modules,idx)
			if next_module and not(copy_failed):
				current_modules[idx] = next_module
				info_dict[npx_directory][current_modules[idx]] = next_module_info
		
		if (current_modules[idx] == npx_directories[npx_directory].end_module) and (info_dict[npx_directory][current_modules[idx]].rcode is not None) and (finished_list[idx] == 0):	
			finished_list[idx] = 1
			logger_dict[npx_directory].info("Finished processing "+ npx_directory)

		if  not(busy) and not(wait) and not(finished_list[idx]) and (failed_dict[npx_directory]==0 or next_module == 'copy_processed_data'):
			current_modules[idx], info_dict[npx_directory][next_module], failed_dict[npx_directory] = initiate_next_module(next_module, npx_directory, json_directory)

		time.sleep(3)

print("Finished processing all directories")
try:
	for npx_directory in npx_directories:
		for module, info in info_dict[npx_directory].items():
			print(npx_directory,": ",module)
			print("Start time: ", info.starttime, " Endtime: ", info.endtime, " Processing time: ", (info.endtime-info.starttime).seconds)
except Exception as E:
	print("Error printing processing info")
	print(E)

try:	
	for npx_directory in npx_directories:
		for module, info in info_dict[npx_directory].items():
			if info.rcode is not 0:
				print("Module: ", module,",  Return Code: ", info.rcode)
				print("Output: ", info.output)
				print("Error: ", info.error)
except Exception as E:
	print("Error printing nonzero returncodes")
	print(E)

if warning_dict:
	pprint(warning_dict)
else:
	print("No processing script warnings occurred")

if failed_dict:
	pprint(failed_dict)
else:
	print("No processing script failures occurred")

postprocessing(npx_directories)