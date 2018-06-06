from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time

import numpy as np

import matlab.engine
import matlab_file_generator

from _schemas import InputParameters, OutputParameters


def run_automerging(args):

    # load lfp band data
    
    matlab_file_generator.create_chanmap(args['kilosort_location'], args['num_channels'], StartChan = 1, Nchannels = args['num_channels'], bad_channels = [])
    matlab_file_generator.create_config(args['kilosort_location'], args['input_file_location'], Nfilt = 512, Threshold = [4, 10, 10], lam = [5, 20, 20], IntitalizeTh = -4, InitializeNfilt=10000)
    
    logging.info('Running Kilosort')
    
    start = time.time()
    
    eng = matlab.engine.start_matlab()
    eng.createChannelMapFile(nargout=0)
    eng.kilosort_config_file(nargout=0)
    eng.kilosort_master_file(nargout=0)
        
    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = run_automerging(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
