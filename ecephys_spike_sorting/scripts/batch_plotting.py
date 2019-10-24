
import glob

from ecephys_spike_sorting.common.visualization import plotContinuousFile

mouse = '72112' #, '425589', '432104', '425597'] #,'434845','434494','434843']

probes = ['probeA','probeB','probeC','probeD','probeE','probeF']

for probe in probes:

    output_path = r'/mnt/nvme0/continuous_file_qc/' + mouse + '_' + probe + '.png'
    raw_data_file = glob.glob(r'/mnt/sd5.3/RE-SORT/*' + mouse + '*/*' + probe + '*/continuous/Neuropix-3a-100.0/continuous.dat')[0]

    plotContinuousFile(raw_data_file, time_range = [5000, 5002], output_path=output_path)
