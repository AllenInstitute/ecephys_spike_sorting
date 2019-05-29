import numpy as np
import matplotlib.pyplot as plt

fnames = [r'J:\turn_on_2018-09-05_15-28-09_probeA_sorted\continuous\Neuropix-3a-100.0\continuous.dat',
          r'J:\adc_cal_2018-09-05_15-28-57_probeA_sorted\continuous\Neuropix-3a-100.0\continuous.dat',
          r'J:\reconnect_2018-09-05_15-29-44_probeA_sorted\continuous\Neuropix-3a-100.0\continuous.dat']

for fidx, fname in enumerate(fnames):
	numChannels = 384
	rawDataAp = np.memmap(fname, dtype='int16', mode='r')
	dataAp = np.reshape(rawDataAp, (int(rawDataAp.size/numChannels), numChannels))

	plt.figure(10)
	plt.subplot(1,3,fidx+1)
	plt.hist(dataAp[:100000,10]*0.195,bins=np.linspace(-200,0,200))


plt.show()

