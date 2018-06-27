from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time

import numpy as np

from automerging import automerging

def run_automerging(args):

    logging.info('Running automerging')
    
    start = time.time()
    
    automerging(args['kilosort_location'], args['sample_rate'])

    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from _schemas import InputParameters, OutputParameters

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
