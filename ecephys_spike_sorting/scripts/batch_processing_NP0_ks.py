import os
import subprocess
import glob
import shutil

from create_input_json import createInputJson

npx_directories = [r'N:\715093703_386129_20180627'
				   ]

probe_type = '3A'

json_directory = r'C:\Users\svc_neuropix\Documents\json_files'


def copy_to_local(source, destination):

	robocopy(source, destination)

def copy_to_remote(source, destination):

	if not os.path.exists(os.path.dirname(destination)):
		os.mkdir(os.path.dirname(destination))

	robocopy(source, destination)

def copy_single_file(source, destination):

	if not os.path.exists(destination):
		print('Copying ' + source + ' to ' + destination)
		shutil.copyfile(source, destination)
	else:
		print('file already exists at ' + destination)

def copy_sorted_files(source, destination):

	files_to_copy = [f for f in os.listdir(source) if f[-3:] != 'dat' and f != 'ap_timestamps.npy']

	if not os.path.exists(destination):
		os.makedirs(destination, exist_ok=True)

	for f in files_to_copy:
		shutil.copyfile(os.path.join(source, f), os.path.join(destination, f))

def robocopy(source, destination):

	print('Copying:')
	print('  Source: ' + source)
	print('  Destination: ' + destination)
	
	if os.path.isdir(source):
		command_string = "robocopy " + source + " "+ destination + r" /e /xc /xn /xo"
	else:
		command_string = "robocopy " + source + " "+ destination

	subprocess.call(command_string.split(' '))


for local_directory in npx_directories:

	remote_directory = glob.glob(os.path.join(r'\\10.128.50.151',
												'SD4',
												os.path.basename(local_directory)))[0]

	sorted_directories = glob.glob(os.path.join(remote_directory, '*_sorted'))
	sorted_directories.sort()

	for sorted_directory in sorted_directories:

		new_directories = glob.glob(os.path.join(r'\\10.128.50.77',
													'sd5.3',
													'RE-SORT',
													'*',
													os.path.basename(sorted_directory)))

		if len(new_directories) > 0:
			if os.path.exists(os.path.join(new_directories[0], 'continuous.dat')):
				sd = new_directories[0] #os.path.join(new_directories[0], 'continuous','Neuropix-3a-100.0')
			else:
				sd = sorted_directory #os.path.join(sorted_directory, 'continuous','Neuropix-3a-100.0')
		else:
			sd = sorted_directory #os.path.join(sorted_directory, 'continuous','Neuropix-3a-100.0')

		local_sorting_directory = os.path.join(local_directory, os.path.basename(sd))

		os.makedirs(local_sorting_directory, exist_ok=True)

		print('Copying data...')
		copy_single_file(os.path.join(sd, 'continuous','Neuropix-3a-100.0',  'continuous.dat'),
						os.path.join(local_sorting_directory,'continuous.dat'))

		copy_single_file(os.path.join(sd, 'probe_info.json'),
						os.path.join(local_sorting_directory,'probe_info.json'))

		session_id = os.path.basename(local_sorting_directory)

		target_directory = os.path.join(r'\\10.128.50.77',
										'sd5.3',
										'RE-SORT',
										session_id[:-7], 
										session_id, 
										'continuous', 
										'Neuropix-3a-100.0')

		input_json = os.path.join(json_directory, session_id + '_resort-input.json')
		output_json = os.path.join(json_directory, session_id + '_resort-output.json')

		info = createInputJson(input_json, kilosort_output_directory=local_sorting_directory,
											extracted_data_directory=local_sorting_directory)

		modules = [ 'kilosort_helper',
					'kilosort_postprocessing',
					'noise_templates',
					'mean_waveforms',
					'quality_metrics'] 

		for module in modules:

			command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
			          + " --output_json " + output_json

			subprocess.check_call(command.split(' '))

		copy_sorted_files(local_sorting_directory, target_directory)

		shutil.rmtree(local_sorting_directory)


