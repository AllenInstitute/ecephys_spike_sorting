from argschema import ArgSchemaParser
import os
import logging
import time

from ecephys_spike_sorting.modules.mean_waveforms.extract_waveforms import extract_waveforms

def calculate_mean_waveforms(args):
    
    start = time.time()

    extract_waveforms(args['extracted_data_directory'], args['kilosort_output_directory'], args['num_channels'])

    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from _schemas import InputParameters, OutputParameters

    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = calculate_mean_waveforms(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
