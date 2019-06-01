from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
import shutil

import numpy as np

import matlab.engine

from . import matlab_file_generator
from ...common.utils import read_probe_json, get_repo_commit_date_and_hash

def run_kilosort(args):

    print('ecephys spike sorting: kilosort helper module')

    commit_date, commit_time = get_repo_commit_date_and_hash(args['kilosort_helper_params']['kilosort_repository'])

    spikes_dir = os.path.dirname(args['ephys_params']['ap_band_file'])
    spike_dir_forward_slash = spikes_dir.replace('\\','/')

    mask, offset, scaling, surface_channel, air_channel = read_probe_json(args['common_files']['probe_json'])

    top_channel = np.min([args['ephys_params']['num_channels'], int(surface_channel) + args['kilosort_helper_params']['surface_channel_buffer']])

    shutil.copyfile(os.path.join('ecephys_spike_sorting','modules','kilosort_helper','kilosort2_master_file.m'),
        os.path.join(args['kilosort_helper_params']['matlab_home_directory'],'kilosort2_master_file.m'))

    matlab_file_generator.create_chanmap(args['kilosort_helper_params']['matlab_home_directory'], \
                                        EndChan = top_channel, \
                                        probe_type = args['ephys_params']['probe_type'],
                                        MaskChannels = np.where(mask == False)[0])
    if args['kilosort_helper_params']['kilosort_version'] == 1:
        matlab_file_generator.create_config(args['kilosort_helper_params']['matlab_home_directory'], 
                                            spike_dir_forward_slash, 
                                            os.path.basename(args['ephys_params']['ap_band_file']), 
                                            args['kilosort_helper_params']['kilosort_params'])
    elif args['kilosort_version'] == 2:
        matlab_file_generator.create_config2(args['kilosort_helper_params']['matlab_home_directory'], 
                                             spike_dir_forward_slash, 
                                             args['ephys_params'], 
                                             args['kilosort_helper_params']['kilosort2_params'])
    else:
        return

    start = time.time()
    
    eng = matlab.engine.start_matlab()
    eng.createChannelMapFile(nargout=0)

    if args['kilosort_helper_params']['kilosort_version'] == 1:
        eng.kilosort_config_file(nargout=0)
        eng.kilosort_master_file(nargout=0)
    else:
        eng.kilosort2_config_file(nargout=0)
        eng.kilosort2_master_file(nargout=0)

    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time,2)) + ' seconds')
    print()
    
    return {"execution_time" : execution_time,
            "kilosort_commit_date" : commit_date,
            "kilosort_commit_hash" : commit_time} # output manifest


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
