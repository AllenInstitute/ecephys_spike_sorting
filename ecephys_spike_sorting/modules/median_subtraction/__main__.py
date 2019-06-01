from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
import glob
import numpy as np

from ...common.utils import read_probe_json, get_repo_commit_date_and_hash

def run_median_subtraction(args):

    print('ecephys spike sorting: median subtraction module')

    commit_date, commit_hash = get_repo_commit_date_and_hash(args['median_subtraction_params']['median_subtraction_repo'])

    mask, offset, scaling, surface_channel, air_channel = read_probe_json(args['common_files']['probe_json'])

    logging.info('Running median subtraction')
    
    start = time.time()

    subprocess.check_call([args['median_subtraction_params']['median_subtraction_executable'], 
                           args['common_files']['probe_json'], 
                           args['ephys_params']['ap_band_file'],
                           str(int(air_channel))])
    
    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time,2)) + ' seconds')
    print()
    
    return {"median_subtraction_execution_time" : execution_time,
            "median_subtraction_commit_date" : commit_date,
            "median_subtraction_commit_hash" : commit_hash } # output manifest} # output manifest

def main():

    from ._schemas import InputParameters, OutputParameters

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
