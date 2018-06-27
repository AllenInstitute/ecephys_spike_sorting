import numpy as np

from ecephys_spike_sorting.common.utils import get_ap_band_continuous_file

def calculate_metrics(dataFolder, kilosortFolder)

	rawDataFile = get_ap_band_continuous_file(dataFolder)

	spike_times = np.load(os.path.join(kilosortFolder,'spike_times.npy'))
    spike_clusters = np.load(os.path.join(kilosortFolder,'spike_clusters.npy'))

    iso = isolation(spike_times, spike_clusters, rawDataFile)
    noise_o = noise_overlap(spike_times, spike_clusters, rawDataFile)
    isi_con = isi_contamination(spike_times, spike_clusters, rawDataFile)

    # make a DataFrame
    # save it to disk
            

def isolation(spike_times, spike_clusters, rawDataFile):

	# code goes here

	pass


def noise_overlap(spike_times, spike_clusters, rawDataFile):

	# code goes here

	pass


def isi_contamination(spike_times, spike_clusters, rawDataFile):

	# code goes here

	pass
