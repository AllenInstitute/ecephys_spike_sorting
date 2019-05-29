import subprocess
import shutil
import os
import time
from pprint import pprint
from collections import namedtuple
import glob
import datetime
import psutil

npx_paramstup = namedtuple('npx_paramstup',['backup_location','start_module','end_module'])

backup_drive = r'T:'
default_start = 'copy_raw_data'
default_end = 'copy_processed_data'

network_location = r"\\sd5\sd5"

npx_directories = {r'J:\800972939_366122_20181224_probeA':npx_paramstup(backup_drive,default_start,default_end),
					r'K:\800972939_366122_20181224_probeB':npx_paramstup(backup_drive,default_start,default_end),
					r'L:\800972939_366122_20181224_probeC':npx_paramstup(backup_drive,default_start,default_end)
					}


#todo modify so it will check all backup drives?

data_file_params = namedtuple('data_file_params',['relpath','upload','sorting_step'])

def check_data_processing(npx_directory,npx_params):
	try:
		a = npx_params.backup_location
	except Exception as E:
		npx_params_old = npx_params
		npx_params = npx_paramstup(npx_params_old.backup1,None,None)
		network_location = npx_params_old.backup2

	basepath,session = os.path.split(npx_directory)
	probe = session.split("_")[-1]
	local_sort_dir = os.path.join(basepath,session+"_sorted")
	relpaths, data_files = make_files()
	try:
			backup_temp = os.path.join(npx_params.backup_location, 'temp.txt')
	except Exception as E:
			backup_temp = os.path.join(npx_params.backup1, 'temp.txt')
	base_temp = os.path.join(basepath, 'temp.txt')
	try:
		open(backup_temp, 'a').close
	except Exception as E:
		pass
	try:
		open(base_temp, 'a').close
	except Exception as E:
		pass
	try:
		backup_drive_error = os.path.samefile(base_temp, backup_temp)
		if backup_drive_error:
			print('ERROR: the backup drive seems to be the same as the acquisition drive')
	except Exception as E:
		print('catch_specific')
		raise(E)
		backup_drive_error = True
		print('ERROR: Backup drive test failed, backup drive could be the same as the acquisition drive')

	raw_size_backup = 0
	try:
		raw_backup_path = os.path.join(npx_params.backup_location,session)
	except Exception as E:
		raw_backup_path = os.path.join(npx_params.backup_location,session)
	if os.path.isdir(raw_backup_path):
		#print('The raw data has been backed up for '+probe)
		raw_size_backup = dir_size(raw_backup_path)
	else:
		print('ERROR: Could not find raw data_backup for '+probe+':')

	raw_size = 0
	if os.path.isdir(npx_directory):
		raw_size = dir_size(npx_directory)
		if raw_size == raw_size_backup:
			pass
			#print('the raw data backup matches the acquired data for '+probe)
		else:
			print('ERROR: the raw data backup does not match the acquired data for '+probe)
	else:
		print('WARNING: could not find the acquired data to compare to backup size')

	missing_files_list = []
	acquisition_size_dict = {}
	backup_size_dict = {}
	network_size_dict = {}
	acquisition_mtime_dict = {}
	backup_mtime_dict = {}
	network_mtime_dict = {}
	for data_file,file_params in data_files.items():
		relpath = relpaths[file_params.relpath]		
		local_path = os.path.join(basepath,session+"_sorted",relpath,data_file)
		found = False
		try:
			acquisition_size_dict[data_file] = os.path.getsize(local_path)
			acquisition_mtime_dict[data_file] = os.path.getmtime(local_path)
			found = True
		except FileNotFoundError as E:
			pass

		backup_path = os.path.join(npx_params.backup_location,session+"_sorted",relpath,data_file)
		try:
			backup_size_dict[data_file] = os.path.getsize(backup_path)
			backup_mtime_dict[data_file] = os.path.getmtime(backup_path)
			found = True
		except FileNotFoundError as E:
			pass

		network_path = os.path.join(network_location,session+"_sorted",relpath,data_file)
		try:
			network_size_dict[data_file] = os.path.getsize(network_path)
			network_mtime_dict[data_file] = os.path.getmtime(network_path)
			found = True
		except FileNotFoundError as E:
			pass

		if not found:
			missing_files_list.append(data_file)

	if missing_files_list:
		print('ERROR: Some processing files were not found on any drive for '+probe)
		modules_missing = set()
		for file in missing_files_list:
			module = data_files[file].sorting_step
			modules_missing.add(module)
		print('The missing files are from the following modules:')
		print(modules_missing)
	else:
		pass
		#print('All the processing files were found on either the acquisition drive or the backup drive for '+probe)

	if raw_size_backup or raw_size:
		npx_size = max(raw_size_backup,raw_size)
		key = r"continuous\Neuropix-3a-100.0\continuous.dat"
		try:
			cont_back = backup_size_dict[key]
		except KeyError:
			cont_back = 0
		try:
			cont = acquisition_size_dict[key]
		except KeyError:
			cont = 0
		if cont or cont_back:
			continuous_size = max(cont,cont_back)
			if continuous_size > 1.2*npx_size and continuous_size < 1.3*npx_size:
				pass
				#print('The continuous size seems correct relative to the npx size for '+probe)
			else: print('ERROR: The continuous file seems too large or too small relative to the npx for '+probe)
		else:print('ERROR: unable to find continuous to compare to npx for '+probe)
	else: print('ERROR: Unable to find npx to compare to continuous file for '+probe)

	missing_backup_list = []
	for file in data_files:
		if file not in backup_size_dict:
			missing_backup_list.append(file)
	if missing_backup_list:
		print('ERROR: Some files are not backed up locally for '+probe+':')
		print(missing_backup_list)
	else:
		pass
		#print('all files are backed up locally for '+probe)

	mismatch_size_list = []
	for file in data_files:
		if file in acquisition_size_dict and file in backup_size_dict:
			if not(acquisition_size_dict[file]==backup_size_dict[file]) or not (acquisition_mtime_dict[file]==backup_mtime_dict[file]):
				mismatch_size_list.append(file)
	if mismatch_size_list:
		print('ERROR: Some processing files have different sizes or modification times on the backup drive and acquisition drive for '+probe)
		print(mismatch_size_list)
	else:
		pass
		#print('all files on the backup drive match the size and modification times of those on the acquisition drive for '+probe)
	sucess = False
	if not(missing_files_list) and not(mismatch_size_list) and not(missing_backup_list) and not backup_drive_error:
		if raw_size == raw_size_backup and raw_size>0:
			print("Deleting NPX files from the acquisition drive for ",probe)
			safe_delete_npx(basepath, npx_params.backup_location, session)
		delete_files = {}
		for file,file_params in data_files.items():
			if file_params.upload == False and file in acquisition_size_dict:
				delete_files[file]=file_params
		if delete_files:
			print("Deleting files not needed for day 2 upload from the acquisition drive for ",probe)
			for delete_file,delete_file_params in delete_files.items():
				relpath = relpaths[delete_file_params.relpath]
				safe_delete_file(basepath, npx_params.backup_location, session, relpath, delete_file)
			#sorted_dir = os.path.join(basepath,session+"_sorted")
			#print(sorted_dir)
			#backup_npx_dir = os.path.join(npx_params.backup_location,session+"_sorted")
			#print(backup_npx_dir)
			#for root, dirs, files in os.walk(sorted_dir):
		#		for name in files:
	#				local_path = os.path.join(root,name)
#					print(local_path)#
#					backup_path = os.path.join(backup_npx_dir,name)#
					#print(backup_path)
					#if os.path.isfile(local_path):
					#	try:
					#		if os.path.getsize(local_path)==os.path.getsize(backup_path) and not os.path.samefile(local_path,backup_path):
					#			os.remove(local_path)
					#			#print(file +" deleted")
					#		else:
					#			print(name +" not deleted, backup error")
					#	except Exception as E:
					#		print(name +" not deleted, other error")
					#		print(E)
				#for dire in dirs:
				#	try:
				#		os.rmdir(os.path.join(root,dire))
				#	except Exception as E:
				#		pass
			try:
				shutil.rmtree(os.path.join(basepath,session+"_sorted", 'logs'))
			except Exception as E:
				print('Could not delete log folder')
			print('Marking as sucess!')
			sucess = True
		else:
			pass
			#print("No files found to delete for day 2 upload")

	extra_files = []		
	for dirpath, dirnames, filenames in os.walk(local_sort_dir):
		for f in filenames:
			if f not in data_files and not(f == 'continuous.dat'):
				extra_files.append(f)
	if extra_files:
		print("ERROR: Some extra files were found for ",probe)
		print(extra_files)
	else:
		pass
		#print("No extra files were found for ", probe)

	net_raw_size_backup = 0
	net_raw_backup_path = os.path.join(network_location,session)
	if os.path.isdir(net_raw_backup_path):
		net_raw_size_backup = dir_size(net_raw_backup_path)
		if net_raw_size_backup == raw_size_backup:
			pass
			#print('The raw data is on SD4 and the size matches the backup for '+probe)
		else:
			print("ERROR: The raw data on SD4 is not the same size as the raw data on the backup drive for ", probe)
	else:
		print('ERROR: Could not find raw data on SD4 for  for '+probe+':')

	missing_net_backup_list = []
	for file in data_files:
		if file not in network_size_dict:
			missing_net_backup_list.append(file)
	if missing_net_backup_list:
		print('ERROR: Some files are not backed up on SD4 for '+probe+':')
		print(missing_net_backup_list)
	else:
		pass#print('all files are backed up on SD4 for '+probe)

	net_mismatch_size_list = []
	for file in data_files:
		if file in network_size_dict and file in backup_size_dict:
			if not(network_size_dict[file]==backup_size_dict[file]) or not(network_mtime_dict[file]==backup_mtime_dict[file]):
				net_mismatch_size_list.append(file)
	if net_mismatch_size_list:
		print('ERROR: Some processing files have different sizes or modification times on the backup drive and SD4 for '+probe)
		print(net_mismatch_size_list)
	elif not(network_size_dict):
		print('WARNING: Could not check file sizes on SD4 since they do not exist')
	else:
		pass
		#print('All files on the backup drive match the size and modification times of those on SD4 for '+probe)
	return sucess

def safe_delete_npx(base_path, backup, session):
	local_npx_dir = os.path.join(base_path,session)
	backup_npx_dir =  os.path.join(backup,session)
	for root, dirs, files in os.walk(local_npx_dir):
		for name in files:
			local_path = os.path.join(root,name)
			backup_path = os.path.join(backup_npx_dir,name)
			if os.path.isfile(local_path):
				try:
					if os.path.getsize(local_path)==os.path.getsize(backup_path) and not os.path.samefile(local_path,backup_path):
						os.remove(local_path)
						#print(file +" deleted")
					else:
						print(name +" not deleted, backup error")
				except Exception as E:
					print(name +" not deleted, other error")
					print(E)
		for dire in dirs:
			try:
				os.rmdir(os.path.join(root,dire))
			except Exception as E:
				pass
	try:
		os.rmdir(local_npx_dir)
	except Exception as E:
		print("WARNING: Raw directory not deleted, probably non-empty")

def safe_delete_file(base_path, backup, session, relpath, data_file):
	local_path = os.path.join(base_path,session+"_sorted",relpath,data_file)
	backup_path = os.path.join(backup,session+"_sorted",relpath,data_file)
	try:
		if os.path.getsize(local_path)==os.path.getsize(backup_path) and not os.path.samefile(local_path, backup_path):
			os.remove(local_path)		
			#print(data_file + " deleted")
		else: print(data_file + " not deleted, backup error")
	except Exception as E:
		print(data_file + " not deleted, other error")
		print(E)




def dir_size(dir_path):
      total_size = 0
      for dirpath, dirnames, filenames in os.walk(dir_path):
          for f in filenames:
              fp = os.path.join(dirpath, f)
              fsize = os.path.getsize(fp)
              total_size +=fsize
      return total_size
    

def make_files():
	relpaths = {
	                'lfp':r"continuous\Neuropix-3a-100.1",
	                'spikes':r"continuous\Neuropix-3a-100.0",
	                'events':r"events\Neuropix-3a-100.0\TTL_1",
	                'empty':""
	                    }
	        
	data_files = {
	      "probe_info.json":data_file_params('empty',True,'depth_estimation'),
	      "channel_states.npy":data_file_params('events',True,'extraction'),
	      "event_timestamps.npy":data_file_params('events',True,'extraction'),
	      r"continuous\Neuropix-3a-100.1\continuous.dat":data_file_params('empty',True,'extraction'),
	      "lfp_timestamps.npy":data_file_params('lfp',True,'sorting'),
	      "amplitudes.npy":data_file_params('spikes',True,'sorting'),
	      "spike_times.npy":data_file_params('spikes',True,'sorting'),
	          "mean_waveforms.npy":data_file_params('spikes',True,'mean waveforms'),
	          "spike_clusters.npy":data_file_params('spikes',True,'sorting'),
	          "spike_templates.npy":data_file_params('spikes',True,'sorting'),
	          "templates.npy":data_file_params('spikes',True,'sorting'),
	          "whitening_mat.npy":data_file_params('spikes',True,'sorting'),
	          "whitening_mat_inv.npy":data_file_params('spikes',True,'sorting'),
	          "templates_ind.npy":data_file_params('spikes',True,'sorting'),
	          "similar_templates.npy":data_file_params('spikes',True,'sorting'),
	          "metrics.csv":data_file_params('spikes',True,'metrics'),
	          "channel_positions.npy":data_file_params('spikes',True,'sorting'),
	          "cluster_group.tsv":data_file_params('spikes',True,'sorting'),
	          "channel_map.npy":data_file_params('spikes',True,'sorting'),
	          "params.py":data_file_params('spikes',True,'sorting'),
	      "probe_depth.png":data_file_params("empty",False,'depth estimation'),
	      r"continuous\Neuropix-3a-100.0\continuous.dat":data_file_params('empty',False,'extraction'),
	      "residuals.dat":data_file_params('spikes',False,'median subtraction'),
	      "pc_features.npy":data_file_params('spikes',False,'sorting'),
	      "template_features.npy":data_file_params('spikes',False,'sorting'),
	      "rez2.mat":data_file_params('spikes',False,'sorting'),
	      "rez.mat":data_file_params('spikes',False,'sorting'),
	      "pc_feature_ind.npy":data_file_params('spikes',False,'sorting'),
	      "template_feature_ind.npy":data_file_params('spikes',False,'sorting')
	      }
	return relpaths, data_files



def check_all_data(npx_directories):
	success_list = []
	for npx_directory,params in npx_directories.items():
		dir_sucess = check_data_processing(npx_directory, params)
		success_list.append(dir_sucess)
	return all(set(success_list))

def check_all_space(npx_directories):
	space_dict = {}
	for npx_dir in npx_directories:
		drive, tail = os.path.splitdrive(npx_dir)
		free_space = psutil.disk_usage(drive).free
		if  free_space < (200*(10**9)):
			space_dict[drive] = free_space
	if space_dict:
		for drive in space_dict.items():
			print("ERROR: Not enough space on ",drive,"for acquisition")
	else: print("There is enough space for acquisition on all drives")

def postprocessing(npx_directories):
	check_all_data(npx_directories)
	generate_batch_file(npx_directories)
	check_all_space(npx_directories)
	return sucess

	

if __name__ == "__main__":
	postprocessing(npx_directories)