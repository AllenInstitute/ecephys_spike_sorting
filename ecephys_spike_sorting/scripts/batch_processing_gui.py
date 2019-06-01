#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

from qtmodern import styles, windows
from qtpy import QtGui, QtCore
from qtpy.QtWidgets import *

import subprocess
import glob
import shutil
import os
import time
import psutil
from collections import namedtuple, OrderedDict
from pprint import pprint
from recordclass import recordclass
import datetime
import logging
from qtpy import QtGui, QtCore
import multiprocessing
import json
import xml.etree.ElementTree as ET

logging.basicConfig(level = logging.DEBUG)


from helpers.check_data_processing import check_data_processing, check_all_space
#import helpers.processing as npxprocess
from create_input_json import createInputJson
from zro import RemoteObject, Proxy

class RemoteInterface(RemoteObject):
	def __init__(self, rep_port, parent):
		super(RemoteInterface, self).__init__(rep_port=rep_port)
		print('Opening Remote Interface on port: '+ str(rep_port))
		self.parent = parent

	def process_npx(self, session_name, probes = []):
		print('Attempting to initiate processing from remote command')
		print('Probes = '+ str(probes))
		self.parent.set_session( session_name)
		started = self.parent.start_processing(session_name, probes)
		return started

	def ping(self):
		print("its alive")       


class Processing_Agent(QWidget):
	def __init__(self):
		super(Processing_Agent, self).__init__()

		#logging.basicConfig(level=logging.DEBUG,
		#        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		#self.config = mpeconfig.source_configuration('neuropixels')

		self.interface = RemoteInterface(rep_port=1234, parent=self)
		print('Starting Remote Interface')

		self.interfaceTimer = QtCore.QTimer()
		self.interfaceTimer.timeout.connect(self._check_sock)
		self.interfaceTimer.start(100)

		self.smallFont = QtGui.QFont()
		self.smallFont.setPointSize(8)
		self.smallFont.setBold(False)

		self.bigFont = QtGui.QFont()
		self.bigFont.setPointSize(12)
		self.bigFont.setBold(False)

		self.vLayout = QVBoxLayout()

		self.header = QLabel()
		self.header.setFont(self.bigFont)
		self.header.setText('NPX Processing Agent')
		self.header.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.vLayout.addWidget(self.header)

		self.processing_layout = QGridLayout()

		self.sessoin_label = QLabel()
		self.sessoin_label = QLabel()
		self.sessoin_label.setFont(self.smallFont)
		self.sessoin_label.setText('Full session name:')
		self.sessoin_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.session_entry = QLineEdit()
		self.session_entry.setFont(self.smallFont)
		self.processing_layout.addWidget(self.sessoin_label, 1, 0)
		self.processing_layout.addWidget(self.session_entry, 1, 1)

		self.vLayout.addLayout(self.processing_layout)

		self.processButton = QPushButton("Process Data")
		self.processButton.setStyleSheet("color: #333; border: 2px solid #555; border-radius: 11px; padding: 5px;background: qradialgradient(cx: 0.3, cy: -0.4,fx: 0.3, fy: -0.4,radius: 1.35, stop: 0 #fff, stop: 1 #388E3C);min-width: 80px;font-size:15px;")
		self.processButton.clicked.connect(self.process_button_press)
		self.vLayout.addWidget(self.processButton)


		###############################################################

		self.setLayout(self.vLayout)

	def set_session(self, session_name):
		self.session_entry.setText(session_name)

	def process_button_press(self):
		session_name = self.session_entry.text()
		reply = QMessageBox.question(self, 'Message', "Are you sure you want to process npx with session name: "+session_name+"?", QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self.start_processing(session_name)
		else:
			pass

	def closeEvent(self, event):
		reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)

		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

	def _check_sock(self):
		self.interface._check_rep()

   

#For testing session_name = 'data_test'
	def start_processing(self, session_name, probes):
		print('checking readiness for '+session_name)
		try:
			check_ready_for_processing(session_name, probes)
			print('Processing npx for '+session_name)
			p = multiprocessing.Process(target=process_npx, args=(session_name,probes))
			#time.sleep(100)
			p.start()
			started_processing = True
		except Exception as E:
			logging.exception('Failed to start processing')
			started_processing = False
		print('finished initiating processing')
		return started_processing
			

def make_constants(session_name, probes):
	npx_params = namedtuple('npx_params',['start_module','end_module','backup1','backup2'])

	default_backup1 = r'T:'
	default_backup2 = os.path.join(r'\\sd5\sd5', session_name)
	default_start = 'primary_backup_raw_data'
	default_end = 'cleanup'
	json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

	npx_directories = OrderedDict()
	if 'A' in probes:
		npx_directories[os.path.join(r'J:', session_name+'_probeA')]=npx_params(default_start,default_end,default_backup1,default_backup2)
	if 'B' in probes:
		npx_directories[os.path.join(r'K:', session_name+'_probeB')]=npx_params(default_start,default_end,default_backup1,default_backup2)
	if 'C' in probes:
		npx_directories[os.path.join(r'L:', session_name+'_probeC')]=npx_params(default_start,default_end,default_backup1,default_backup2)



	######################################################################################

	modules = [
			   'primary_backup_raw_data',
			   'extract_from_npx',
			   'depth_estimation',
			   'edit_probe_json',
			   'median_subtraction',
			   'kilosort_helper',
			   'noise_templates',
			   'mean_waveforms',
			   'quality_metrics',
			   'copy_logs',
			   'primary_backup_processed_data',
			   'secondary_backup_raw_data',
			   'secondary_backup_processed_data',
			   'cleanup'
			   ]

	copy_while_waiting_modules = [
				'copy_while_waiting_primary',
				#'copy_while_waiting_secondary_raw',
				'copy_while_waiting_secondary_processed'
				]

	no_process_modules = [
			'edit_probe_json',
			'copy_logs',
			'cleanup'
	]

	copy_modules = {
			'primary_backup_raw_data',
	   'primary_backup_processed_data',
	   'secondary_backup_raw_data',
	   'secondary_backup_processed_data',							
		'copy_while_waiting_primary',
		'copy_while_waiting_secondary_raw',
		'copy_while_waiting_secondary_processed'
		}

	return npx_directories, modules, copy_while_waiting_modules, json_directory, no_process_modules, copy_modules


def check_ready_for_processing(session_name, probes):
	npx_directories, modules, copy_while_waiting_modules, json_directory, no_process_modules, copy_modules = make_constants(session_name, probes)
	#Add test of matlab engine
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
		try:
			for dirpath, dirnames, filenames in os.walk(dir_path):
				for f in filenames:
					fp = os.path.join(dirpath, f)
					total_size += os.path.getsize(fp)
		except Exception:
			total_size = 0
		return total_size

	for npx_directory,params in npx_directories.items():
		module_list = npx_module_dict[npx_directory]
		copy_raw = 'primary_backup_raw_data' in module_list
		copy_processed = 'copy_processed_data' in module_list or 'copy_while_waiting_primary' in copy_while_waiting_modules
		copy_raw2 = 'secondary_backup_raw_data' in module_list or 'copy_while_waiting_secondary_raw' in copy_while_waiting_modules
		copy_processed2 = 'secondary_backup_processed_data' in module_list or 'copy_while_waiting_secondary_processed' in copy_while_waiting_modules
		kilosort=('kilosort_helper' in module_list)
		extract = 'extract_from_npx' in module_list
		drive, dirname = os.path.split(npx_directory)
		sorted_dirname = dirname+"_sorted"
		sorted_dir = os.path.join(drive,sorted_dirname)
		backup_dir = os.path.join(params.backup1, dirname)
		sorted_backup_dir = os.path.join(params.backup1,sorted_dirname)
		backup_dir2 = os.path.join(params.backup2, dirname)
		sorted_backup_dir2 = os.path.join(params.backup2,sorted_dirname)
		if 'copy_raw_data' in npx_module_dict[npx_directory] or 'extract_from_npx' in npx_module_dict[npx_directory]:
			try:
				free_space = psutil.disk_usage(drive).free
				recording_size = sum(os.path.getsize(os.path.join(npx_directory,recording)) for recording in os.listdir(npx_directory))
				extracted_size = 1.25*recording_size

			except FileNotFoundError as E:
				print('One of the directories probably doesn\'t exist - check '+npx_directory)
				raise E
		else: 
			try:
				recording_size = 0
				free_space = psutil.disk_usage(drive).free
				if os.path.isdir(sorted_dir):
					extracted_size = dir_size(sorted_dir)
				else:
					raise FileNotFoundError
			except FileNotFoundError as E:
				print('One of the directories probably doesn\'t exist - check '+sorted_dir)
				raise E
		logging.debug("free_space"+ str(free_space))
		logging.debug("extracted_size"+ str(extracted_size))
		residual_size = extracted_size/12
		logging.debug("residual_size"+ str(residual_size))
		kilosort_size = (30*(10**9))*kilosort
		logging.debug("kilosort_size"+ str(kilosort_size))
		median_sub_size = residual_size*('median_subtraction' in module_list)
		logging.debug("median_sub_size"+ str(median_sub_size))
		processing_size = (100*(10**6))#100 megabytes for depth png, mean waveforms and metrics 
		logging.debug("processing_size"+ str(processing_size))

		current_raw_backup = dir_size(backup_dir)
		current_processed_backup = dir_size(sorted_backup_dir)
		current_raw_backup2 = dir_size(backup_dir2)
		current_processed_backup2 = dir_size(sorted_backup_dir2)

		primary_backup_space_needed = copy_raw*max(0,recording_size -current_raw_backup) + copy_processed*(processing_size+max(0,extracted_size-current_processed_backup))
		logging.debug("primary_backup_space_needed"+ str(primary_backup_space_needed))
		secondary_backup_space_needed=  copy_raw2*max(0,recording_size -current_raw_backup2) + copy_processed2*(processing_size+max(0,extracted_size-current_processed_backup2))
		logging.debug("secondary_backup_space_needed"+ str(secondary_backup_space_needed))
		c_space_needed = kilosort*extracted_size
		
		extract = ('extract_from_npx' in module_list)
		if extract and os.path.isdir(sorted_dir):
			raise ValueError(sorted_dir, " already exists. Please delete it if you would like to repeat the extraction from npx, otherwise comment out the 'extract_from_npx' module.")
		data_space_needed = extract*extracted_size + processing_size + median_sub_size + kilosort_size
		logging.debug("data_space_needed"+ str(data_space_needed))
		try:
			backup_size_dict[params.backup1] += primary_backup_space_needed
		except:
			backup_size_dict[params.backup1] = primary_backup_space_needed
		backup_location, folder = os.path.split(params.backup2)
		try:
			backup_size_dict[backup_location] += secondary_backup_space_needed
		except:
			backup_size_dict[backup_location] = secondary_backup_space_needed
		max_c_space_needed = max(c_space_needed,max_c_space_needed)
		if free_space < data_space_needed:
			print('check ' +npx_directory)
			raise ValueError('There is not enough space on one of the drives')
		print(npx_directory+' exist and there appears to be enough disk space free for processing')

	if psutil.disk_usage(r'C:').free < max_c_space_needed:
		raise ValueError('There is not enough space on the C drive for kilosort to process the largest dataset')
	else: print('There appears to be enough space on the C drive for kilosort')
	for bdrive, size_needed in backup_size_dict.items():
		print('Checking space on '+ bdrive)
		if psutil.disk_usage(bdrive).free < size_needed:
			print('Free space on ',bdrive,': ',  psutil.disk_usage(bdrive).free)
			print('Space predicted needed on ',bdrive,': ', size_needed )
			raise ValueError('There is not enough space on the backup drive for all the data')
		else: print('And there appears to be enough space on backup drive '+bdrive)
	#raise(ValueError)
	####################################################################

def process_npx(session_name, probes):
	npx_directories, modules, copy_while_waiting_modules, json_directory, no_process_modules, copy_modules = make_constants(session_name, probes)
	pprint(npx_directories)
	#time.sleep(20)
	#raise(ValueError)
	def add_warning(npx_dir, string):
		logger_dict[npx_dir].warning(string)
		try:
			warning_dict[npx_dir].append(string)
		except KeyError as E:
			warning_dict[npx_dir]=[string]
	
	def copy_data(source, destination, npx_directory,module):
		logger_dict[npx_directory].info("{} Copying data from {} to {} ...".format(module,source,destination))
		try:
			os.mkdir(destination)
		except Exception as E:
			add_warning(npx_directory,"For "+module+" files were not copied if they already existed.")
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
		this_module_info = module_info(None,None,None,now,None, None)
		info_dict[npx_directory][next_module] = this_module_info
		failed = 0
		try:
			session_id = os.path.basename(npx_directory)
			input_json = os.path.join(json_directory, session_id + '_' + next_module + '-input.json')
			output_json = os.path.join(json_directory, session_id + '_' + next_module +'-output.json')
			info = createInputJson(input_json, npx_directory=npx_directory)
			command_string = ["python", "-m", "ecephys_spike_sorting.modules." + next_module, 
									"--input_json", input_json,
									"--output_json", output_json]
			logger_dict[npx_directory].info(command_string)
			start_module(npx_directory,next_module, command_string, info)
		except Exception as E:
			logger_dict[npx_directory].error("Error initiating " + next_module+" for " +npx_directory)
			logger_dict[npx_directory].exception(E)
			failed = E
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
			dir_sucess = check_data_processing(npx_directory,npx_directories[npx_directory])
			success_list.append(dir_sucess)
			no_returncode(npx_directory,module,  rcode_in = int(not(dir_sucess)))
		elif module == 'extract_from_npx':
			try:
				recording_size = sum(os.path.getsize(os.path.join(npx_directory,recording)) for recording in os.listdir(npx_directory))
				backup_location = os.path.join(npx_directories[npx_directory].backup1,os.path.basename(npx_directory))
				backup_size = sum(os.path.getsize(os.path.join(backup_location,recording)) for recording in os.listdir(npx_directory))
				if not recording_size == backup_size:
					raise ValueError('One of the backups failed')
				else:
					process_dict[npx_directory].append(subprocess.Popen(command_string, stdout = subprocess.PIPE,stderr = subprocess.PIPE))
			except Exception as E:
				logger_dict[npx_directory].exception("Unable to verify raw backup of "+ npx_directory+" before extracting. If verification is not needed comment out this portion of the script")
				raise(E)
		elif module == 'edit_probe_json':
			serial_number = edit_probe_json(npx_directory)
			if serial_number == None:
				add_warning(npx_directory, 'Could not find settings.xml for '+npx_directory)
			no_returncode(npx_directory, module)
		elif module == 'copy_logs':
			copy_logs(npx_directory)
			no_returncode(npx_directory, module)
		else:
			process_dict[npx_directory].append(subprocess.Popen(command_string, stdout = subprocess.PIPE,stderr = subprocess.PIPE))

	def no_returncode(npx_directory, module, rcode_in = 0):
		logger_dict[npx_directory].info('finished '+module+', no exit status to fetch')
		info_dict[npx_directory][module]._replace(rcode = rcode_in, output = None, error = None, endtime = datetime.datetime.now())

	def copy_logs(npx_directory):
		location, dirname = os.path.split(npx_directory)
		save_progess_stats(npx_directory, npx_directories,info_dict, warning_dict, failed_dict)
		log_location = os.path.join(location, dirname+'_sorted', 'logs')
		start_date_string = start.strftime("%y.%m.%d.%I.%M.%S")
		log_dir = os.path.join(log_location, start_date_string)
		try: 
			os.mkdir(log_location)
		except Exception as E: 
			pass
		os.mkdir(log_dir)
		session_name = os.path.split(npx_directory)[1]
		session_id = session_name.split('_')[0]
		probe = session_name.split('_')[-1]
		for name in os.listdir(json_directory):
			if session_id in name and probe in name:
				date_maybe = name.split('_')[1]
				if len(date_maybe) ==17:
					if date_maybe == start_date_string:
						source = os.path.join(json_directory, name)
						dest = os.path.join(log_dir, name)
						shutil.copy2(source,dest)
				else:	
					source = os.path.join(json_directory, name)
					dest = os.path.join(log_dir, name)
					shutil.copy2(source,dest)

	def get_settings_xml_value(npx_directory, element_name, attribute_name, default):
		settings_path = os.path.join(npx_directory, 'settings*.xml')
		value = default
		try:
			settings_path = glob.glob(settings_path)[0]
			#serial_number = None
			tree = ET.parse(settings_path)
			root = tree.getroot()
			for elemnt in root.iter(element_name):
				value = elemnt.attrib[attribute_name]
		except Exception as E:
			logger_dict[npx_directory].exception(E)
		return value

	def get_settings_xml_element_text(npx_directory, element_name, default):
		settings_path = os.path.join(npx_directory, 'settings*.xml')
		try:
			settings_path = glob.glob(settings_path)[0]
			#serial_number = None
			tree = ET.parse(settings_path)
			root = tree.getroot()
			for elemnt in root.iter(element_name):
				value = elemnt.text
		except Exception as E:
			logger_dict[npx_directory].exception(E)
			value = default
		return value

	def check_noise_channels(mask):
		"""Check to see if there are too many chaannels masked, and default to only masking the reference channels if so"""
		if sum(not(channel) for channel in mask)>30:
			mask = 384*[True]
			references = [36, 73, 75, 112, 151, 188, 227, 264, 303, 340, 379]
			for ref in references:
				mask[ref] = False
		return mask

	def verify_mask(probe_json):
		probe_json['original_mask'] = probe_json['mask']
		probe_json['mask'] = check_noise_channels(probe_json['mask'])
		return probe_json


	def edit_probe_json(npx_directory):
		drive, session = os.path.split(npx_directory)
		json_path = os.path.join(drive, session+'_sorted','probe_info.json')
		logger_dict[npx_directory].info('Adding the software and probe info to the probe_json at path'+json_path)
		serial_number = get_settings_xml_value(npx_directory, 'NEUROPIXELS', 'probe_serial_number', None)
		probe_json = {}
		try:
			with open(json_path, "r") as read_file:
				probe_json = json.load(read_file)
		except exception as E:
			logger_dict[npx_directory].exception('Error reading probe_json')
		try:
			probe_json = verify_mask(probe_json)
		except exception as E:
			logger_dict[npx_directory].exception('Error Verifying the mask and setting to default if too many masked')
		if not('software' in probe_json):
			probe_json["software"] =  {
				"name" : "Open Ephys GUI",
				"version" : get_settings_xml_element_text(npx_directory, 'VERSION',"0.4.4"),
				"machine" : get_settings_xml_element_text(npx_directory, 'MACHINE',os.environ['COMPUTERNAME']),
				"os" : "Windows 10"
			} 
		if not('probe' in probe_json):
			probe_json["probe"] = {
				"phase" : "3a", 
				"ap gain" : get_settings_xml_value(npx_directory, 'NEUROPIXELS', 'apGainValue',"500x"),
				"lfp gain" : get_settings_xml_value(npx_directory, 'NEUROPIXELS', 'lfpGainValue',"250x"),
				"reference channel" : get_settings_xml_value(npx_directory, 'NEUROPIXELS', 'referenceChannel',"Ext"),
				"filter cut" : get_settings_xml_value(npx_directory, 'NEUROPIXELS', 'filterCut', "300 Hz"),
				"serial number" : serial_number,
				"option" : "3",

				"subprocessors" :[
					{
						"name" : "Neuropix-3a-100.0",
						"type" : "AP band",
						"num channels" : 384,
						"sample_rate" : 30000.0,
						"bit volts" : 0.195
					},
					{
						"name" : "Neuropix-3a-100.1",
						"type" : "LFP band",
						"num channels" : 384,
						"sample_rate" : 2500.0,
						"bit volts" : 0.195
					}
				]

			}
		with open(json_path, "w") as write_file:
			json.dump(probe_json, write_file, indent=4)
		return serial_number

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
		if failed_dict[npx_directory]:
			try:
				next_module_idx =  modules.index(next_module)
			except Exception as E:
				#next is probably a kilosort wait module. If median sub has failed for some reason we shouldn't proceed with kilosort. 
				next_module_idx = 0
			alt_next_module_idx = modules.index('copy_logs')
			if next_module_idx < alt_next_module_idx:
				next_module = 'copy_logs'
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
					logger.info(str(line.rstrip())[2:-1])
					tot_read = tot_read +len(line)
		except ValueError as E:
			logger.warning('Failed to read stdout',exc_info = True)

	def log_progress(npx_directory):
		
		if info_dict[npx_directory][current_modules[idx]].rcode == None:
			p = process_dict[npx_directory][-1]
			if not(current_modules[idx]  in copy_modules) and not(current_modules[idx]  in no_process_modules): 
				out_list = log_out(p,logger_dict[npx_directory])
				#if if(out_list == None):
			#			for line in out_list: 
			#			logger_dict[npx_directory].info(line)
			if not(busy):
				logger_dict[npx_directory].info("fetching exit status and info for"+current_modules[idx]+npx_directory)
				try:
					output,error  = p.communicate()
					try:
						output = output.decode("utf-8")
					except Exception as E:
						pass
					try:
						error = error.decode("utf-8")
					except Exception as E:
						pass
					mod_start_time = info_dict[npx_directory][current_modules[idx]].starttime
					now = datetime.datetime.now()
					#startstr = mod_start_time.strftime("%y.%m.%d.%I.%M.%S")
					#endstr = now.strftime("%y.%m.%d.%I.%M.%S")
					process_time_str = (now-mod_start_time).seconds
					info_dict[npx_directory][current_modules[idx]]._replace(rcode = p.returncode, output = output, error = error, endtime = now, processtime = process_time_str)
					logger_dict[npx_directory].info("finished fetching exit status and info for "+ current_modules[idx]+" "+npx_directory)

					robocopy = current_modules[idx] in copy_modules
					#print(robocopy)
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
				print('about to save prgress stats for '+npx_directory)
				save_progess_stats(npx_directory, npx_directories,info_dict, warning_dict, failed_dict)	
						

	def create_file_handler(level_string,level_idx,limsID,probe):
		file_name = limsID+'_'+datetime.datetime.now().strftime("%y.%m.%d.%I.%M.%S")+'_'+level_string+'_'+probe+".log"
		log_file = os.path.join(json_directory,file_name)
		file_handler = logging.FileHandler(log_file)

		file_handler.setLevel(level_idx)
		file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
		return file_handler

	def create_logger(npx_directory):
		full_session_id, limsID ,probe = parse_npx_dir(npx_directory)
		name_string = '_'.join([limsID, probe])
		mylogger = logging.getLogger(name_string)
		error_file_handler = create_file_handler('error',logging.WARNING,limsID,probe)
		info_file_handler = create_file_handler('info',logging.DEBUG,limsID,probe)
		mylogger.addHandler(error_file_handler)
		mylogger.addHandler(info_file_handler)
		#stream_handler = logging.StreamHandler()
		#stream_handler.setLevel(logging.INFO)
		#mylogger.addHandler(stream_handler)
		return mylogger

	def parse_npx_dir(npx_directory):
		session_name = os.path.basename(npx_directory)
		limsID = session_name.split('_')[0]
		probe = session_name.split('_')[-1]
		return session_name, limsID, probe

	def print_progress_stats(npx_directories,info_dict, warning_dict, failed_dict):
		print("Finished processing all directories")
		try:
			for npx_directory in npx_directories:
				for module, info in info_dict[npx_directory].items():
					print(npx_directory,": ",module)
					print("Start time: ", info.starttime, " Endtime: ", info.endtime, " Processing time: ", info.processtime)
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

	def save_progess_stats(npx_dir, npx_directories,info_dict, warning_dict, failed_dict):
		print('about to save prgress stats for '+npx_dir)
		session_name, limsID ,probe = parse_npx_dir(npx_dir)
		start_string = start.strftime("%y.%m.%d.%I.%M.%S")
		json_compatible_info_dict = {}
		for npx_directory in npx_directories:
			json_compatible_info_dict[npx_directory] = {}
			for module, info in info_dict[npx_directory].items():
				json_compatible_info_dict[npx_directory][module]=info._asdict()
				#print('check for strings')
				#pprint(info._asdict())
				try:
					json_compatible_info_dict[npx_directory][module]['starttime'] = json_compatible_info_dict[npx_directory][module]['starttime'].strftime("%y.%m.%d.%I.%M.%S")
				except Exception as E:
					pass
				try:
					json_compatible_info_dict[npx_directory][module]['endtime'] = json_compatible_info_dict[npx_directory][module]['endtime'].strftime("%y.%m.%d.%I.%M.%S")
				except Exception as E:
					pass
				#json_compatible_info_dict[npx_directory][module]['Processing time seconds'] = (info.endtime-info.starttime).seconds
		path = os.path.join(json_directory, limsID+'_'+start_string+'_all-probes_all-module-info'+".json")
		with open(path, "w") as write_file:
			json.dump(json_compatible_info_dict,write_file, indent=4)
		path = os.path.join(json_directory, limsID+'_'+start_string+'_all-probes_nonzero-rcode-info'+".json")
		nonzero_returncode_dict = {}
		for npx_directory in npx_directories:
			nonzero_returncode_dict[npx_directory] = {}
			for module, info in json_compatible_info_dict[npx_directory].items():
				if info['rcode'] is not 0:
					nonzero_returncode_dict[npx_directory][module]=info
		with open(path, "w") as write_file:
			json.dump(nonzero_returncode_dict, write_file, indent=4)
		path = os.path.join(json_directory, limsID+'_'+start_string+'_all-probes_in-script-warnings'+".json")
		with open(path, "w") as write_file:
			json.dump(warning_dict, write_file, indent=4)
		path = os.path.join(json_directory, limsID+'_'+start_string+'_all-probes_in-script-errors'+".json")
		with open(path, "w") as write_file:
			json.dump(failed_dict, write_file, indent=4)

		path = os.path.join(json_directory, limsID+'_'+start_string+'_'+probe+'_all-module-info'+".json")
		with open(path, "w") as write_file:
			json.dump(json_compatible_info_dict[npx_dir], write_file, indent=4)
		path = os.path.join(json_directory, limsID+'_'+start_string+'_'+probe+'_nonzero-rcode-info'+".json")
		with open(path, "w") as write_file:
			json.dump(nonzero_returncode_dict[npx_dir], write_file, indent=4)
		path = os.path.join(json_directory, limsID+'_'+start_string+'_'+probe+'_in-script-warnings'+".json")
		try:
			with open(path, "w") as write_file:
				json.dump(warning_dict[npx_dir], write_file, indent=4)
		except KeyError as E:
			pass
		path = os.path.join(json_directory, limsID+'_'+start_string+'_'+probe+'_in-script-errors'+".json")
		with open(path, "w") as write_file:
			json.dump(failed_dict[npx_dir], write_file, indent=4)
		#TODO figure out how to make the outputs and errors print nicely again


################################################################

	#TODO change format so there is a process state dict to make things more self documenting? might be worse...
	process_dict = {}
	warning_dict = {}
	logger_dict = {}
	success_list = []
	finished_list = [0]*len(npx_directories)
	current_modules = [False]*len(npx_directories)
	copy_while_waiting = [False]*len(npx_directories)
	info_dict = {}
	failed_dict = {}
	module_info = recordclass('module_info', ['rcode', 'output', 'error','starttime','endtime', 'processtime' ])


	for npx_directory in npx_directories:
		full_session_id = os.path.basename(npx_directory)
		limsID = full_session_id.split('_')[0]
		probe = full_session_id.split('_')[-1]
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

			if current_modules[idx] and not(current_modules[idx] in no_process_modules):
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
					#info_dict[npx_directory][current_modules[idx]] = next_module_info
			
			if (current_modules[idx] == npx_directories[npx_directory].end_module) and (info_dict[npx_directory][current_modules[idx]].rcode is not None) and (finished_list[idx] == 0):	
				finished_list[idx] = 1
				logger_dict[npx_directory].info("Finished processing "+ npx_directory)

			if  (not(busy) and not(wait) and not(finished_list[idx]) and (failed_dict[npx_directory]==0)) or ((next_module in copy_modules) and not(copy_wait)):
				current_modules[idx], next_module_info , failed_dict[npx_directory] = initiate_next_module(next_module, npx_directory, json_directory)

			time.sleep(3)

	print_progress_stats(npx_directories,info_dict, warning_dict, failed_dict)
	computer = os.environ['COMPUTERNAME']
	sucess = all(set(success_list))
	if sucess:
		set_completed(session_name, computer)
	else: print('processing was not verified so no signal was sent')

	assistant_set_session(session_name)

	make_batch_files(session_name)

	cleanup_DAQs()

	check_all_space(npx_directories)
	return session_name, sucess

def get_processing_assitant_proxy():
	computer = os.environ['COMPUTERNAME']
	port = '1212'
	print('Creating Proxy for device:Day2_Agent at host: '+computer+' port: '+port+' device name: Day2_Agent')
	#Create the Proxy for the dummy components
	fullport = computer+':'+port
	proxy = Proxy(fullport, serialization='json')
	ping_result = os.system('ping %s -n 1' % (computer,))
	if ping_result:
		print('Host '+computer+' Not Found')
		# LAN WAKE UP CALL GOES HERE
	else:
		print('Host '+computer+' Found')
	return proxy

def make_batch_files(session_name):
	proxy = get_processing_assitant_proxy()
	try:
		proxy.create_bat_files(session_name)
		print('signaled assistant to create batch file sucessfully')
	except Exception as E:
		print('failed to signal assistant to create batch file')
		print(E)

def cleanup_DAQs():
	proxy = get_processing_assitant_proxy()
	try:
		proxy.cleanup_daqs()
		print('signaled assistant to cleanup daqs sucessfully')
	except Exception as E:
		print('failed to signal assistant to cleanup daqs')
		print(E)

def assistant_set_session(session_name):
	proxy = get_processing_assitant_proxy()
	try:
		proxy.set_session_name(session_name)
		print('signaled assistant to set session sucessfully')
	except Exception as E:
		print('failed to signal assistant to set session')
		print(E)

def set_completed(session, computer):
	WSE_computer = 'W10DTSM18306'
	port = '1234'
	print('Creating Proxy for device:Day2_Agent at host: '+WSE_computer+' port: '+port+' device name: Day2_Agent')
	#Create the Proxy for the dummy components
	fullport = WSE_computer+':'+port
	proxy = Proxy(fullport, serialization='json')
	ping_result = os.system('ping %s -n 1' % (WSE_computer,))
	if ping_result:
		print('Host '+WSE_computer+' Not Found')
		# LAN WAKE UP CALL GOES HERE
	else:
		print('Host '+WSE_computer+' Found')

	initiated = True
	try:	
		proxy.signal_completed(session, computer) 
		print('signaled complete sucessfully')
	except Exception as E:
		print('failed to signal complete')
		print(E)
				
def main():
	app = QApplication([])
	styles.dark(app)

	g = windows.ModernWindow(Processing_Agent())
	# g.resize(350,100)
	g.move(50,270)
	g.setWindowTitle('Neuropixels Surgery/Experiment Notes')
	g.show()
	app.exec_()
	
if __name__ == '__main__':
	main()