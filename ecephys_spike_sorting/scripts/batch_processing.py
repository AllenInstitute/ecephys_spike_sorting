import os
import subprocess

from create_input_json import createInputJson

sorted_directories = [						
						# r"J:\m449779\2019-10-08_11-52-16_probeB",
						# r"J:\m449779\2019-10-08_13-01-56_probeB",
						# r"K:\m449779\2019-10-08_11-52-14_probeC",
						# r"K:\m449779\2019-10-08_13-01-54_probeC",

						# r"J:\m449779\2019-10-09_09-59-40_probeB",
						# r"J:\m449779\2019-10-09_11-17-22_probeB",
						# # r"J:\m449779\2019-10-09_12-29-20_probeB",
						# r"K:\m449779\2019-10-09_09-59-38_probeC",
						# r"K:\m449779\2019-10-09_11-17-20_probeC",
						# # r"K:\m449779\2019-10-09_12-29-18_probeC",
						# r"L:\m449779\2019-10-09_09-59-41_probeE",
						# r"L:\m449779\2019-10-09_11-17-24_probeE",
						# r"L:\m449779\2019-10-09_12-29-22_probeE",

						# r"K:\m449772\Day2\2019-09-20_12-46-33_probeC",

						r"E:\estim_pilot\mouse481937\probeB",
						r"E:\estim_pilot\mouse481937\probeC",
						r"E:\estim_pilot\mouse481937\probeE"

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

	modules = [ #'extract_from_npx',
				#'depth_estimation'
				#'median_subtraction',
				#'kilosort_helper',
				#'kilosort_postprocessing'
				#'noise_templates',
				'mean_waveforms',
				'quality_metrics'
				]


	for module in modules:

		command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
		          + " --output_json " + output_json

		subprocess.check_call(command.split(' '))



