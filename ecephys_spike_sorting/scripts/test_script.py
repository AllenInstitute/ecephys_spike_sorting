import os
import subprocess
import glob
import time
import matlab.engine
import shutil

import numpy as np

from compute_offset_and_surface_channel import compute_offset_and_surface_channel, read_probe_json
import matlab_file_generator
from postprocessing import postprocessing

ssds = ['J:\\','K:\\','L:\\','J:\\','K:\\','J:\\','K:\\','L:\\']

input_files = ['706875901_388187_20180607_probeD',
			   '706875901_388187_20180607_probeE',
			   '706875901_388187_20180607_probeF',
			   '705847873_388186_20180605_probeD',
			   '705847873_388186_20180605_probeE',
			   '704514354_380485_20180601_probeD',
			   '704514354_380485_20180601_probeE',
			   '704514354_380485_20180601_probeF'
			   ]

recordings = ['1','1','1','1','1','1','1','1']

npx_executable = r'C:\Users\svc_neuropix\Documents\GitHub\npxextractor\Release\NpxExtractor.exe'
med_sub_executable = r'C:\Users\svc_neuropix\Documents\GitHub\spikebandmediansubtraction\Builds\VisualStudio2013\Release\SpikeBandMedianSubtraction.exe'
kilosort_location = r'C:\Users\svc_neuropix\Documents\MATLAB'

for idx, input_file in enumerate(input_files):

	#try:

		if idx > 0:

			npx_file = os.path.join(ssds[idx], 
								input_file, 
								'recording' + recordings[idx] + '.npx')

			output_directory = os.path.join('C:\\data',input_file +'_sorted')
			output_directory_E = os.path.join('E:\\',input_file +'_sorted')

			if not os.path.exists(output_directory):

				os.mkdir(output_directory)

			# convert from NPX
			if idx > 1:
				subprocess.check_call([npx_executable, npx_file, output_directory])

			# compute surface channel + offsets
			compute_offset_and_surface_channel(output_directory)
			json_file = os.path.join(output_directory, 'probe_info.json')
			mask, offset, scaling, surface_channel, air_channel = read_probe_json(json_file)
			continuous_directory = os.path.join(output_directory, os.path.join('continuous','Neuropix*.0'))
			ap_directory = glob.glob(continuous_directory)[0]
			spikes_file = os.path.join(ap_directory, 'continuous.dat')

			# median subtraction
			if idx > 1:
				subprocess.check_call([med_sub_executable, json_file, spikes_file, str(int(air_channel))])
				
			if True:
				# run kilosort
				top_channel = int(surface_channel) + 15
				num_templates = top_channel * 3
				num_templates = num_templates - (num_templates % 32)

				matlab_file_generator.create_chanmap(kilosort_location, \
					                                 EndChan = int(surface_channel) + 15, \
					                                 BadChannels = np.where(mask == False)[0])
				matlab_file_generator.create_config2(kilosort_location, \
			    									ap_directory.replace('\\','/'))
			    
				start = time.time()
				eng = matlab.engine.start_matlab()
				eng.kilosort2_master_file(nargout=0)
			  
				execution_time = time.time() - start

				# automerging
				#postprocessing(ap_directory)

				print("Copying to E: drive")
				shutil.move(output_directory, output_directory_E)
				print("Finished copying.")

	#except:
#		print("Something went wrong with " + output_directory)