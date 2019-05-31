from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
import shutil

from git import Repo

import numpy as np

import io, json, os

from .create_settings_json import create_settings_json

def run_npx_extractor(args):

    print('ecephys spike sorting: npx extractor module')

    repo = Repo(args['npx_extractor_repo'])
    headcommit = repo.head.commit

    extracted_data_drive, directory = os.path.splitdrive(args['directories']['extracted_data_directory'])
    
    total, used, free = shutil.disk_usage(extracted_data_drive)
    
    filesize = os.path.getsize(args['npx_file'])
    
    assert(free > filesize * 2)
    
    if not os.path.exists(args['directories']['extracted_data_directory']):
        os.mkdir(args['directories']['extracted_data_directory'])

    #settings_json = create_settings_json(args['settings_xml'])
    
    output_file = os.path.join(args['directories']['extracted_data_directory'], 'open-ephys.json')

    start = time.time()
    subprocess.check_call([args['npx_extractor_executable'], args['npx_file'], args['directories']['extracted_data_directory']])
    execution_time = time.time() - start

    #with io.open(output_file, 'w', encoding='utf-8') as f:
    #    f.write(json.dumps(settings_json, ensure_ascii=False, sort_keys=True, indent=4))

    print('total time: ' + str(execution_time) + ' seconds')
    print( )
    
    return {"execution_time" : execution_time,
           # "settings_json" : settings_json,
            "npx_extractor_commit_date" : time.strftime("%a, %d %b %Y %H:%M", time.gmtime(headcommit.committed_date)),
            "npx_extractor_commit_hash" : headcommit.hexsha } # output manifest


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
