from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
import shutil

import numpy as np


from ...common.utils import read_probe_json, get_repo_commit_date_and_hash, rms

def run_CatGT(args):

    print('ecephys spike sorting: CatGT helper module')

    catGTPath = args['catGT_helper_params']['catGTPath']
    catGTexe_fullpath = catGTPath.replace('\\', '/') + "/CatGT"
    # print('path to CatGT exe: ' + catGTexe_fullpath )
    
    cmd_parts = list()
    
    cmd_parts.append(catGTexe_fullpath)
    cmd_parts.append('-dir=' + args['directories']['npx_directory'])
    cmd_parts.append('-run=' + args['catGT_helper_params']['run_name'])
    cmd_parts.append('-g=' + args['catGT_helper_params']['gate_string'])
    cmd_parts.append('-t=' + args['catGT_helper_params']['trigger_string'])
    cmd_parts.append('-prb=' + args['catGT_helper_params']['probe_string'])
    cmd_parts.append(args['catGT_helper_params']['stream_string'])
    cmd_parts.append(args['catGT_helper_params']['cmdStr'])
    cmd_parts.append('-dest=' + args['directories']['extracted_data_directory'])
    
    # print('cmd_parts')

    catGT_cmd = ' '        # use space as the separator for the command parts
    catGT_cmd = catGT_cmd.join(cmd_parts)
    
    print('CatGT command line:' + catGT_cmd)
    
    start = time.time()
    subprocess.call(catGT_cmd)

    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time,2)) + ' seconds')
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from ._schemas import InputParameters, OutputParameters

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)
    
    output = run_CatGT(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
