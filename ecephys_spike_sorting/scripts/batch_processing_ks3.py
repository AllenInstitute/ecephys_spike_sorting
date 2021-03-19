import os
import subprocess
import glob

from create_input_json_ks3 import createInputJsonKS3

directories = glob.glob(r'G:\processed_20200323\*_*_*probe*')
file_types = ['processed', 'original']

temp_data_path = r'D:\data\kilosort'

probe_type = '3A'

json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

for directory in directories[:1]:

   for file_type in file_types[1:]:

        sorting_directory = os.path.join(directory, file_type)

        input_json = os.path.join(json_directory, os.path.basename(directory) + '-input.json')
        output_json = os.path.join(json_directory, os.path.basename(directory) + '-output.json')

        info = createInputJsonKS3(input_json, 
            extracted_data_directory=sorting_directory,
            kilosort_output_directory=sorting_directory,
            kilosort_output_tmp=temp_data_path)

        modules = ['kilosort_helper',
                    'mean_waveforms',
                    'quality_metrics']

        for module in modules:

            command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
                      + " --output_json " + output_json

            subprocess.check_call(command.split(' '))


def copy_data(src, dest):

    if not os.path.exists(os.path.dirname(destination_directory)):
        os.mkdir(os.path.dirname(destination_directory))

    command = "robocopy "+ src +" "+ dest + r" /e /xc /xn /xo"
    subprocess.check_call(command.split(' '))
    

