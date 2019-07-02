import os
import subprocess
import glob

from create_input_json import createInputJson

mice = ['412804']

source_path = r'\\10.128.50.151\sd4'
dest_path = r'\\10.128.50.77\sd5.3\RE-SORT'

local_data_path = r'C:\data'

probe_type = '3A'

json_directory = r'C:\Users\svc_neuropix\json_files'

for mouse in mice:

    remote_directory = glob.glob(os.path.join(source_path, '*' + mouse + '*'))[0]

    remote_probe_directories = glob.glob(os.path.join(remote_directory, '*_sorted'))

    for remote_probe_directory in remote_probe_directories:

        session_id = os.path.basename(remote_probe_directory)

        local_probe_directory = os.path.join(local_data_path, session_id)
        destination_directory = os.path.join(dest_path, os.path.basename(remote_probe_directory), session_id)
        
        if not os.path.exists(local_probe_directory):
            os.mkdir(local_probe_directory)

        continuous_file = glob.glob(os.path.join(remote_probe_directory, 'continuous','Neuropix-*-100.0','*.dat'))[0]

        if os.path.exists(continuous_file):

            input_json = os.path.join(json_directory, session_id + '-input.json')
            output_json = os.path.join(json_directory, session_id + '-output.json')

            info = createInputJson(input_json, 
                continuous_file=continuous_file,
                extracted_data_directory=remote_probe_directory,
                kilosort_output_directory=local_probe_directory)

            modules = [ #'extract_from_npx',
                        #'depth_estimation',
                        ##'median_subtraction',
                        'kilosort_helper',
                        'kilosort_postprocessing',
                        'noise_templates',
                        'mean_waveforms',
                        'quality_metrics']

            for module in modules:

                command = "python -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + input_json \
                          + " --output_json " + output_json

                subprocess.check_call(command.split(' '))

            copy_data(local_probe_directory, destination_directory)


def copy_data(src, dest):

    if not os.path.exists(os.path.dirname(destination_directory)):
        os.mkdir(os.path.dirname(destination_directory))

    command = "robocopy "+ src +" "+ dest + r" /e /xc /xn /xo"
    subprocess.check_call(command.split(' '))
    

