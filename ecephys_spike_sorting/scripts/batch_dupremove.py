import os
import subprocess

from create_input_json import createInputJson

# batch file to run only the kilosort_postprocessing module, which removes 
# putative double spikes. To run:
#       set sorted_directories path to one or more directores of phy data to process
#       set the probe type: NP1, NP24, NP21
#       set the json_directory to your local directory of json files
#
# To change the parameters for duplicate removal, edit create_input_json.py
# 
# Note that the data in the phy output will be overwritten! If you want to compare
# sorting with and without duplicate removal, or see the effect of different params,
# make a copy of the phy output and run kilosort_postprocessing on that directory.
# To avoid confusion in opening the altered dataset in phy, first delete the .phy
# directory and phy.log file in the phy output directory.

# to understand what spikes are eliminated as duplicates, the output includes a 
# csv file called "overlap_summary.csv", which has five columns:
#   cluster label
#   #spikes after removing duplicates
#   #"within cluster" spikes
#   #"between cluster" spikes, summed over all clusters containing duplicates
#   cluster label of the partner containing the most duplicates


 
sorted_directories = [												
						r"D:\ecephys_fork\test_data\t20"

]


probe_type = 'NP1'

json_directory = r'D:\ecephys_fork\json_files'

for directory in sorted_directories:

	session_id = os.path.basename(directory)

	input_json = os.path.join(json_directory, session_id + '-input.json')
	output_json = os.path.join(json_directory, session_id + '-output.json')

	info = createInputJson(input_json, npx_directory=None, 
	                                   continuous_file = None,
									   kilosort_output_directory=directory,
									   kilosort_output_tmp=directory,
									   probe_type=probe_type)

	modules = [
				'kilosort_postprocessing'
				]


	for module in modules:

		command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json

		subprocess.check_call(command.split(' '))



