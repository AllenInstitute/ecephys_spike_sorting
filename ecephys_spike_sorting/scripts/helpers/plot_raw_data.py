import os
import numpy as np
import glob
import matplotlib.pyplot as plt

def plot_raw_data(dataFolder):

	f1 = os.path.join(dataFolder, os.path.join('continuous','Neuropix*.0'))
	f2 = os.path.join(dataFolder, os.path.join('continuous','Neuropix*.1'))

	ap_directory = glob.glob(f1)[0]
	lfp_directory = glob.glob(f2)[0]

	print(ap_directory)
	print(lfp_directory)

	hi_noise_thresh = 26
	lo_noise_thresh = 3

	output_file = os.path.join(dataFolder, 'probe_info.json')

	numChannels = 384

	offsets = np.zeros((numChannels,), dtype = 'int16')
	rms_noise = np.zeros((numChannels,), dtype='int16')
	lfp_power = np.zeros((numChannels,), dtype = 'float32')

	spikes_file = os.path.join(ap_directory, 'continuous.dat')
	lfp_file = os.path.join(lfp_directory, 'continuous.dat')

	# %%

	rawDataAp = np.memmap(spikes_file, dtype='int16', mode='r')
	dataAp = np.reshape(rawDataAp, (int(rawDataAp.size/numChannels), numChannels))

	mask_chans = np.array([37, 76, 113, 152, 189, 228, 265, 304, 341, 380]) - 1

	start_time = 30000*2000
	recording_time = 30000
	median_subtr = np.zeros((recording_time,numChannels))

	medians = np.zeros((384,))
	plt.figure(figsize=(10,10))

	for ch in range(0,384,10):

		d = dataAp[start_time:start_time+recording_time,ch].astype('float64') #* 1.2 / 1023 / 500.0 * 1e6
		medians[ch] = np.median(d)

		plt.plot(d + ch*100, color = 'gray', linewidth=0.5)
		plt.plot([0,5000],[ch*100,ch*100],'k',alpha=0.25)

	#plt.plot(medians)
	plt.show()