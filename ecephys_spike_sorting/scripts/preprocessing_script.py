import os
import subprocess
import glob
import time
import matlab.engine
import shutil

import numpy as np

from ecephys_spike_sorting.modules.extract_from_npx.__main__ import run_npx_extractor
from ecephys_spike_sorting.modules.depth_estimation.__main__ import run_depth_estimation
from ecephys_spike_sorting.modules.median_subtraction.__main__ import run_median_subtraction
from ecephys_spike_sorting.modules.kilosort_helper.__main__ import run_kilosort

DATA_DIR = r'C:\Users\joshs\Documents\GitHub\ecephys_spike_sorting\test_data'

args = {
    'npx_file' : os.path.join(DATA_DIR, 'test.npx'),
    'extracted_data_directory': os.path.join(DATA_DIR, 'output'),
    'npx_extractor_executable': r'C:\Users\joshs\Documents\GitHub\NpxExtractor\Release\NpxExtractor.exe',
	'save_depth_estimation_figure': True,
	'depth_estimation_figure_location': DATA_DIR,
	'median_subtraction_executable': r'C:\Users\joshs\Documents\GitHub\spikebandmediansubtraction\Builds\VisualStudio2013\Release\SpikeBandMedianSubtraction.exe',
}

npx_file = os.path.join(ssds[idx], 
								input_file, 
								'recording' + recordings[idx] + '.npx')

output_directory = os.path.join('C:\\data',input_file +'_sorted')
output_directory_E = os.path.join('E:\\',input_file +'_sorted')

if not os.path.exists(output_directory):

	os.mkdir(output_directory)

output = run_npx_extractor(args)

args.update(output)

output = run_depth_estimation(args)

args.update(output)

output = run_median_subtraction(args)

args.update(output)

output = run_kilosort(args)

args.update(output)

print("Copying to E: drive")
shutil.move(output_directory, output_directory_E)
print("Finished copying.")