from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
import shutil

import numpy as np

import matlab.engine

from scipy.signal import butter, filtfilt, medfilt

from . import matlab_file_generator
from ...common.utils import read_probe_json, get_repo_commit_date_and_hash, rms

def run_kilosort(args):

    print('ecephys spike sorting: kilosort helper module')

    commit_date, commit_time = get_repo_commit_date_and_hash(args['kilosort_helper_params']['kilosort_repository'])

    input_file = args['ephys_params']['ap_band_file']
    input_file_forward_slash = input_file.replace('\\','/')

    output_dir = args['directories']['kilosort_output_directory']
    output_dir_forward_slash = output_dir.replace('\\','/')

    mask2, offset, scaling, surface_channel, air_channel = read_probe_json(args['common_files']['probe_json'])
    mask2 = [not i for i in mask2]

    try:
        mask = get_noise_channels(args['ephys_params']['ap_band_file'], 
                                  args['ephys_params']['sample_rate'],
                                  args['ephys_params']['bit_volts'])
    except Exception as E:
        mask = np.array(mask2)
    mask[mask2] = False

    mask[args['ephys_params']['reference_channels']] = False

    top_channel = np.min([args['ephys_params']['num_channels'], int(surface_channel) + args['kilosort_helper_params']['surface_channel_buffer']])

    matlab_file_generator.create_chanmap(args['kilosort_helper_params']['matlab_home_directory'], \
                                        EndChan = top_channel, \
                                        probe_type = args['ephys_params']['probe_type'],
                                        MaskChannels = np.where(mask == False)[0])

    if args['kilosort_helper_params']['kilosort_version'] == 1:
    
        matlab_file_generator.create_config(args['kilosort_helper_params']['matlab_home_directory'], 
                                            spike_dir_forward_slash, 
                                            os.path.basename(args['ephys_params']['ap_band_file']), 
                                            args['kilosort_helper_params']['kilosort_params'])
    
    elif args['kilosort_helper_params']['kilosort_version'] == 2:

        shutil.copyfile(os.path.join('ecephys_spike_sorting','modules','kilosort_helper','kilosort2_master_file.m'),
            os.path.join(args['kilosort_helper_params']['matlab_home_directory'],'kilosort2_master_file.m'))
    
        matlab_file_generator.create_config2(args['kilosort_helper_params']['matlab_home_directory'], 
                                             output_dir_forward_slash, 
                                             input_file_forward_slash,
                                             args['ephys_params'], 
                                             args['kilosort_helper_params']['kilosort2_params'])

    elif args['kilosort_helper_params']['kilosort_version'] == 3:

        shutil.copyfile(os.path.join('ecephys_spike_sorting','modules','kilosort_helper','main_kilosort3.m'),
            os.path.join(args['kilosort_helper_params']['matlab_home_directory'],'main_kilosort3.m'))
    
        matlab_file_generator.create_config3(args['kilosort_helper_params']['matlab_home_directory'], 
                                             output_dir_forward_slash, 
                                             input_file_forward_slash,
                                             args['ephys_params'], 
                                             args['kilosort_helper_params']['kilosort3_params'])

    else:
        return

    start = time.time()
    
    eng = matlab.engine.start_matlab()
    eng.createChannelMapFile(nargout=0)

    if args['kilosort_helper_params']['kilosort_version'] == 1:
        eng.kilosort_config_file(nargout=0)
        eng.kilosort_master_file(nargout=0)
    elif args['kilosort_helper_params']['kilosort_version'] == 2: 
        eng.kilosort2_config_file(nargout=0)
        eng.kilosort2_master_file(nargout=0)
    elif args['kilosort_helper_params']['kilosort_version'] == 3:
        eng.kilosort3_config_file(nargout=0)
        eng.main_kilosort3(nargout=0)

    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time,2)) + ' seconds')
    print()
    
    return {"execution_time" : execution_time,
            "kilosort_commit_date" : commit_date,
            "kilosort_commit_hash" : commit_time,
            'mask_channels' : np.where(mask == False)[0]} # output manifest

def get_noise_channels(raw_data_file, sample_rate, bit_volts, noise_threshold=20):

    raw_data = np.memmap(raw_data_file, dtype='int16')
    data = np.reshape(raw_data, (int(raw_data.size / 384), 384))

    start_index = int(1000 * sample_rate)
    end_index = int(1025 * sample_rate)

    b, a = butter(3, [10/(sample_rate/2), 10000/(sample_rate/2)], btype='band')

    D = data[start_index:end_index, :] * bit_volts
    D_filt = np.zeros(D.shape)

    for i in range(D.shape[1]):
        D_filt[:,i] = filtfilt(b, a, D[:,i])

    rms_values = np.apply_along_axis(rms, axis=0, arr=D_filt)

    above_median = rms_values - medfilt(rms_values,11)

    return above_median < noise_threshold


def main():

    from ._schemas import InputParameters, OutputParameters

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = run_kilosort(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
