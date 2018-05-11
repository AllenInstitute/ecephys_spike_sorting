from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time

import numpy as np

from ecephys_spike_sorting.common.OEFileInfo import OEContinuousFile

from _schemas import InputParameters, OutputParameters


def run_median_subtraction(args):

    # load lfp band data
    
    free_space = os.statvfs(args['output_path'])
    
    spike_band_file = OEContinuousFile(args['oe_json_file'],0)
    
    filesize = os.path.getsize(spike_band_file.filename)
    
    assert(free_space > filesize)
    
    logging.info('Running median subtraction')
    
    start = time.time()
    subprocess.check_call([args['executable_file'], args['probe_json'], spike_band_file.filename, args['output_path'], args['surface_channel'], args['air_channel']])
    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = run_median_subtraction(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
