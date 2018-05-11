from argschema import ArgSchemaParser
import os
import logging

import numpy as np

from ecephys_spike_sorting.common.OEFileInfo import OEContinuousFile

from _schemas import InputParameters, OutputParameters


def run_depth_estimation(args):

    # load lfp band data
    
    lfp_file = OEContinuousFile(args['oe_json_file'],1)
    
    logging.info('Loading ' + lfp_file.filename)
    data = lfp_file.load()
        
    #-- estimate channels in brain
    #-- estimate channels in air
    
        
    return {"surface_channel": surface_channel,
            "air_channel": air_channel} # output manifest


def main():

    """Main entry point:"""
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
