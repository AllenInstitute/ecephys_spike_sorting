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
from extractWaveforms import calculate_waveform

ssds = ['J:\\','K:\\','L:\\','J:\\','K:\\','L:\\']

input_files = ['706875901_388187_20180607_probeA',
			   '706875901_388187_20180607_probeB',
			   '706875901_388187_20180607_probeC',
			   '706424491_388184_20180606_probeA',
			   '706424491_388184_20180606_probeB',
			   '706424491_388184_20180606_probeC'
			   ]

recordings = ['1','1','1','1','2','2']

npx_executable = r'C:\Users\svc_neuropix\Documents\GitHub\npxextractor\Release\NpxExtractor.exe'
med_sub_executable = r'C:\Users\svc_neuropix\Documents\GitHub\spikebandmediansubtraction\Builds\VisualStudio2013\Release\SpikeBandMedianSubtraction.exe'
kilosort_location = r'C:\Users\svc_neuropix\Documents\MATLAB'

for idx, input_file in enumerate(input_files):

	#try:

	if idx == 0:

			npx_file = os.path.join(ssds[idx], 
								input_file, 
								'recording' + recordings[idx] + '.npx')

			output_directory = os.path.join('C:\\data',input_file +'_sorted')
			output_directory_E = os.path.join('E:\\',input_file +'_sorted')

			sorted_directory = glob.glob(os.path.join(output_directory_E, 'continuous', 'Neuropix*.0'))[0]

			calculate_waveform(sorted_directory, nBoots=1)

	#except:
#		print("Something went wrong with " + output_directory)