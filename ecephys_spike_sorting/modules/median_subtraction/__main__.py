from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
import glob

from git import Repo

import numpy as np

from ...common.utils import read_probe_json
from ...common.utils import get_ap_band_continuous_file

def run_median_subtraction(args):

    repo = Repo(args['median_subtraction_repo'])
    headcommit = repo.head.commit

    mask, offset, scaling, surface_channel, air_channel = read_probe_json(args['probe_json'])

    spikes_file = get_ap_band_continuous_file(args['directories']['extracted_data_directory'])
    
    logging.info('Running median subtraction')
    
    start = time.time()

    subprocess.check_call([args['median_subtraction_executable'], args['probe_json'], spikes_file, str(int(air_channel))])
    
    execution_time = time.time() - start
    
    return {"median_subtraction_execution_time" : execution_time,
            "median_subtraction_commit_date" : time.strftime("%a, %d %b %Y %H:%M", time.gmtime(headcommit.committed_date)),
            "median_subtraction_commit_hash" : headcommit.hexsha } # output manifest} # output manifest

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
