import os
import subprocess

from create_input_json import createInputJson

sorted_directories = [
						# r'D:\claustrum_pilot\427459\Day1\2019-04-04_13-11-34_probeC',
						# r'D:\claustrum_pilot\427459\Day1\2019-04-04_13-11-35_probeB',
						# r'D:\claustrum_pilot\427459\Day2\2019-04-05_10-57-02_probeC',
						# r"D:\claustrum_pilot\427459\Day2\2019-04-05_10-57-04_probeE",
						# r"D:\claustrum_pilot\430716\Day1\2019-05-16_12-49-54_probeC",
						# r"D:\claustrum_pilot\430716\Day1\2019-05-16_12-49-56_probeB",
						# r"D:\claustrum_pilot\430716\Day2\2019-05-17_11-10-44_probeC",
						
						#r"D:\claustrum_pilot\433926\Day1\2019-04-18_12-27-11_probeC",
						#r"D:\claustrum_pilot\433926\Day1\2019-04-18_12-27-14_probeB",
						#r"D:\claustrum_pilot\433926\Day1\2019-04-18_12-27-16_probeE",
						#r"D:\claustrum_pilot\433926\Day2\2019-04-19_10-24-57_probeC",
						#r"D:\claustrum_pilot\433926\Day2\2019-04-19_10-24-58_probeB",

						# r"D:\claustrum_pilot\433921\Day2\2019-06-20_09-16-51_probeC",
						# r"D:\claustrum_pilot\433921\Day2\2019-06-20_09-16-53_probeB",

						r"D:\claustrum_pilot\451749\Day2\2019-06-27_10-17-44_probeC",
						r"D:\claustrum_pilot\451749\Day2\2019-06-27_10-17-46_probeB",



]

#'/mnt/md0/data/mouse412804/766640955_412804_20181022_probeC_sorted/continuous/Neuropix-3a-100.0']
#npx_directories = [r'L:\766640955_412804_20181022_probeC']

probe_type = '3A'

json_directory = r'C:\Users\svc_neuropix\Documents\json_files'
#json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

for directory in sorted_directories:

	session_id = os.path.basename(directory)

	input_json = os.path.join(json_directory, session_id + '-input.json')
	output_json = os.path.join(json_directory, session_id + '-output.json')

	info = createInputJson(input_json, npx_directory=directory)

	modules = [ 'extract_from_npx',
				'depth_estimation',
				'median_subtraction',
				'kilosort_helper',
				'kilosort_postprocessing'
				# 'noise_templates',
				# 'mean_waveforms',
				# 'quality_metrics']
				]

	for module in modules:

		command = "python -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json

		subprocess.check_call(command.split(' '))



