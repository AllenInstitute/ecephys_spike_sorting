from ecephys_spike_sorting.common.visualization import plotContinuousFile

output_path = r'C:\Users\svc_neuropix\Documents\Images\after_median_subtraction.png'
raw_data_file = r'G:\715093703_386129_20180627_probeD_sorted\continuous\Neuropix-3a-100.0\continuous.dat'

plotContinuousFile(raw_data_file, time_range = [10, 12], output_path=output_path)
