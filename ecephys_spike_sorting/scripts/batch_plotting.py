
import glob

from ecephys_spike_sorting.common.visualization import plotContinuousFile

mice = ['434494'] #,'434845','434494','434843']

probe = 'probeC'

for mouse in mice:

    output_path = r'/mnt/nvme0/continuous_file_qc/' + mouse + '_' + probe + '.png'
    raw_data_file = glob.glob(r'/mnt/sd5.3/RE-SORT/*' + mouse + '*/*' + probe + '*_2/continuous/Neuropix-3a-100.0/continuous.dat')[0]

    plotContinuousFile(raw_data_file, time_range = [5000, 5002], output_path=output_path)
