from argschema import ArgSchemaParser
import os
import logging
import time

from ecephys_spike_sorting.modules.depth_estimation.depth_estimation import compute_offset_and_surface_channel

def run_depth_estimation(args):

    start = time.time()

    surface_channel, air_channel, probe_json = compute_offset_and_surface_channel(args['directories']['extracted_data_directory'],
                                                     args['ephys_params'], args['depth_estimation_params'])

    execution_time = time.time() - start
        
    return {"surface_channel": surface_channel,
            "air_channel": air_channel,
            "probe_json": probe_json,
            "execution_time": execution_time} # output manifest

def main():

    from _schemas import InputParameters, OutputParameters

    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = run_depth_estimation(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
