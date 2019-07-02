
import glob

from ecephys_spike_sorting.common.visualization import plotContinuousFile

mouse = '433891'

probe = 'probeB'

output_path = r'/mnt/nvme0/continuous_file_qc/after_median_subtraction.png'
raw_data_file = glob.glob(r'/mnt/sd5.3/RE-SORT/*' + mouse + '*/*' + probe + '*/continuous/Neuropix-3a-100.0/continuous.dat')[0]

plotContinuousFile(raw_data_file, time_range = [10, 12], output_path=output_path)
