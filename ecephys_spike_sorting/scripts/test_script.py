import os
import subprocess

ssds = ['L:\\','J:\\','J:\\','J:\\','K:\\','K:\\','K:\\','K:\\','L:\\','L:\\']

input_files = ['704514354_380485_20180601_probeF',
				'703640904_380483_20180530_probeD',
			   '703270608_380480_20180529_probeD',
			   '704166722_380486_20180531_probeD',
			   '704514354_380485_20180601_probeD',
			   '703270608_380480_20180529_probeE',
			   '703640904_380483_20180530_probeE',
			   '704166722_380486_20180531_probeE',
			   '704514354_380485_20180601_probeE',
			   '703640904_380483_20180530_probeF',
			   ]

recordings = ['1','2','1','3','1','3','1','4','1','2','2']

npx_executable = r'C:\Users\svc_neuropix\Documents\GitHub\npxextractor\Release\NpxExtractor.exe'
med_sub_executable = r'C:\Users\svc_neuropix\Documents\GitHub\spikebandmediansubtraction\Builds\VisualStudio2013\Release\SpikeBandMedianSubtraction.exe'

for idx, input_file in enumerate(input_files):

	npx_file = os.path.join(ssds[idx], 
						input_file, 
						'recording' + recordings[idx] + '.npx')

	output_directory = os.path.join('E:\\',input_file +'_sorted')

	if not os.path.exists(output_directory):

		os.mkdir(output_directory)

	subprocess.check_call([npx_executable, npx_file, output_directory, str(30)])

	stop

	# compute top channel + offsets

	# median subtraction

	# run kilosort

	# automated post-processing
