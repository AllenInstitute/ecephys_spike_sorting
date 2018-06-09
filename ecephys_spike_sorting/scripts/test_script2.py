import os

from plot_raw_data import plot_raw_data

ssds = ['J:\\','K:\\','L:\\']

input_files = ['706875901_388187_20180607_probeD',
			   '706875901_388187_20180607_probeE',
			   '706875901_388187_20180607_probeF'
			   ]

recordings = ['1','1','1']

for idx, input_file in enumerate(input_files):

	if idx == 0:

		npx_file = os.path.join(ssds[idx], 
							input_file, 
							'recording' + recordings[idx] + '.npx')

		output_directory = os.path.join('E:\\',input_file +'_sorted')

		# compute surface channel + offsets
		plot_raw_data(output_directory)