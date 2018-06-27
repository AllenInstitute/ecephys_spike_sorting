from argschema import ArgSchemaParser
import os
import logging
import time

from ecephys_spike_sorting.modules.depth_estimation.depth_estimation import compute_offset_and_surface_channel

def run_depth_estimation(args):

    start = time.time()

    surface_channel, air_channel, probe_json = compute_offset_and_surface_channel(args['extracted_data_directory'],
                                                     save_figure = args['save_depth_estimation_figure'],
                                                     figure_location = args['depth_estimation_figure_location'])
    
    assert(surface_channel > 0)
    assert(air_channel > 0)

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
