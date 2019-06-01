from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
import shutil

import numpy as np

import io, json, os

from .create_settings_json import create_settings_json
from ...common.utils import get_repo_commit_date_and_hash

def run_npx_extractor(args):

    print('ecephys spike sorting: npx extractor module')

    start = time.time()

    commit_date, commit_hash = get_repo_commit_date_and_hash(args['extract_from_npx_params']['npx_extractor_repo'])

    extracted_data_drive, directory = os.path.splitdrive(args['directories']['extracted_data_directory'])
    
    total, used, free = shutil.disk_usage(extracted_data_drive)
    
    filesize = os.path.getsize(args['extract_from_npx_params']['npx_directory'])
    
    assert(free > filesize * 2)
    
    if not os.path.exists(args['directories']['extracted_data_directory']):
        os.mkdir(args['directories']['extracted_data_directory'])

    subprocess.check_call([args['extract_from_npx_params']['npx_extractor_executable'], 
                           args['extract_from_npx_params']['npx_directory'], 
                           args['directories']['extracted_data_directory']])

    execution_time = time.time() - start

    #settings_json = create_settings_json(args['extract_from_npx_params']['settings_xml'])

    #with io.open(args['common_files']['settings_json'], 'w', encoding='utf-8') as f:
    #    f.write(json.dumps(settings_json, ensure_ascii=False, sort_keys=True, indent=4))

    print('total time: ' + str(np.around(execution_time,2)) + ' seconds')
    print()
    
    return {"execution_time" : execution_time,
            "npx_extractor_commit_date" : commit_date,
            "npx_extractor_commit_hash" : commit_hash } # output manifest


def main():

    from ._schemas import InputParameters, OutputParameters

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = run_npx_extractor(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
