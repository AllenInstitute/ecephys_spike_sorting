from argschema import ArgSchemaParser
import os
import logging
import time

import numpy as np

from _schemas import InputParameters, OutputParameters


def compute_metrics(args):

    # code goes here
    
    start = time.time()
    
        
    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = compute_metrics(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
