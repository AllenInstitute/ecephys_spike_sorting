import os
import subprocess
import glob
import shutil

from create_input_json import createInputJson

npx_directories = [r'J:\715093703_386129_20180627_probeD',
				   r'J:\715093703_386129_20180627_probeA']

probe_type = '3A'

json_directory = r'C:\Users\svc_neuropix\Documents\json_files'


def copy_to_local(source, destination):

	robocopy(source, destination)

def copy_to_remote(source, destination):

	if not os.path.exists(os.path.dirname(destination)):
		os.mkdir(os.path.dirname(destination))

	robocopy(source, destination)

def robocopy(source, destination):

	print('Copying:')
	print('  Source: ' + source)
	print('  Destination: ' + destination)
	
	command_string = "robocopy " + source + " "+ destination + r" /e /xc /xn /xo"

	subprocess.check_call(command_string.split(' '))



for local_directory in npx_directories:

	remote_directory = glob.glob(os.path.join(r'\\sd4','SD4','*',os.path.basename(local_directory)))[0]

	copy_to_local(remote_directory, local_directory)

	session_id = os.path.basename(local_directory)

	extracted_data_directory = local_directory + '_sorted'
	target_directory = os.path.join(r'\\sd5','sd5.3',session_id[:-7], session_id)

	print(remote_directory)
	print(local_directory)
	print(extracted_data_directory)
	print(target_directory)

	input_json = os.path.join(json_directory, session_id + '-input.json')
	output_json = os.path.join(json_directory, session_id + '-output.json')

	info = createInputJson(input_json, npx_directory=local_directory, 
                    extracted_data_directory=extracted_data_directory)

	modules = [ 'extract_from_npx',
				'depth_estimation',
				'median_subtraction'] 

	for module in modules:

		command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json

		subprocess.check_call(command.split(' '))

	copy_to_remote(extracted_data_directory, target_directory)

	shutil.rmtree(local_directory)
	shutil.rmtree(extracted_data_directory)


