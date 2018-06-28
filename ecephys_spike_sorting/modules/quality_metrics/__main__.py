from argschema import ArgSchemaParser
import os
import logging
import time

import numpy as np
import pandas as pd

from ecephys_spike_sorting.modules.quality_metrics.metrics import calculate_metrics

def calculate_quality_metrics(args):

    # code goes here
    
    start = time.time()

    calculate_metrics(args['directories']['extracted_data_directory'], args['directories']['kilosort_output_directory'])
    
    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from _schemas import InputParameters, OutputParameters

    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = calculate_quality_metrics(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
