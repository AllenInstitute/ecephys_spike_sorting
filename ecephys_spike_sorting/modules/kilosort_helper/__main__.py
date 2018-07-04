from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
from git import Repo

import numpy as np

import matlab.engine

import ecephys_spike_sorting.modules.kilosort_helper.matlab_file_generator as matlab_file_generator
from ecephys_spike_sorting.common.utils import read_probe_json, get_ap_band_continuous_file

def run_kilosort(args):

    repo = Repo(args['kilosort_repo'])
    headcommit = repo.head.commit

    spikes_file = get_ap_band_continuous_file(args['directories']['extracted_data_directory'])
    spikes_dir = os.path.dirname(spikes_file)
    spike_dir_forward_slash = spikes_dir.replace('\\','/')

    mask, offset, scaling, surface_channel, air_channel = read_probe_json(args['probe_json'])

    top_channel = np.min([args['ephys_params']['num_channels'], int(surface_channel) + args['surface_channel_buffer']])

    matlab_file_generator.create_chanmap(args['kilosort_location'], \
                                        EndChan = top_channel, \
                                        MaskChannels = np.where(mask == False)[0])
    if args['kilosort_version'] == 1:
        matlab_file_generator.create_config(args['kilosort_location'], spike_dir_forward_slash, 'continuous.dat', args['kilosort_params'])
    elif args['kilosort_version'] == 2:
        matlab_file_generator.create_config2(args['kilosort_location'], spike_dir_forward_slash, args['ephys_params'], args['kilosort2_params'])
    else:
        return

    logging.info('Running Kilosort')
    
    start = time.time()
    
    eng = matlab.engine.start_matlab()
    eng.createChannelMapFile(nargout=0)

    if args['kilosort_version'] == 1:
        eng.kilosort_config_file(nargout=0)
        eng.kilosort_master_file(nargout=0)
    else:
        eng.kilosort2_config_file(nargout=0)
        eng.kilosort2_master_file(nargout=0)

    execution_time = time.time() - start
    
    return {"execution_time" : execution_time,
            "kilosort_commit_date" : time.strftime("%a, %d %b %Y %H:%M", time.gmtime(headcommit.committed_date)),
            "kilosort_commit_hash" : headcommit.hexsha } # output manifest


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
