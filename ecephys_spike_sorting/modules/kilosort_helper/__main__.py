from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time

import numpy as np

import matlab.engine

import ecephys_spike_sorting.modules.kilosort_helper.matlab_file_generator
from ecephys_spike_sorting.common.utils import get_ap_band_continuous_file

def run_kilosort(args):

    spikes_file = get_ap_band_continuous_file(args['directories']['extracted_data_directory'])

    matlab_file_generator.create_chanmap(args['kilosort_location'], args['ephys_params']['num_channels'], StartChan = 1, Nchannels = args['ephys_params']['num_channels'], bad_channels = [])
    
    if args['kilosort_version'] == 1:
        matlab_file_generator.create_config(args['kilosort_location'], spikes_file, args['kilosort_params'])
    elif args['kilosort_version'] == 2:
        matlab_file_generator.create_config2(args['kilosort_location'], spikes_file, args['kilosort2_params'])
    else:
        return

    logging.info('Running Kilosort')
    
    start = time.time()
    
    eng = matlab.engine.start_matlab()
    eng.createChannelMapFile(nargout=0)
    eng.kilosort_config_file(nargout=0)
    eng.kilosort_master_file(nargout=0)
        
    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from _schemas import InputParameters, OutputParameters

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
