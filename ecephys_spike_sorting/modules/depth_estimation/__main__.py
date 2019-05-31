from argschema import ArgSchemaParser
import os
import logging
import time

import numpy as np

from .depth_estimation import compute_offset_and_surface_channel
from ...common.utils import get_ap_band_continuous_file, get_lfp_band_continuous_file, write_probe_json


def run_depth_estimation(args):

    print('ecephys spike sorting: depth estimation module')

    start = time.time()

    numChannels = args['ephys_params']['num_channels']

    output_file = os.path.join(args['directories']['extracted_data_directory'], 'probe_info.json')
    spikes_file = get_ap_band_continuous_file(args['directories']['extracted_data_directory'])
    lfp_file = get_lfp_band_continuous_file(args['directories']['extracted_data_directory'])

    rawDataAp = np.memmap(spikes_file, dtype='int16', mode='r')
    dataAp = np.reshape(rawDataAp, (int(rawDataAp.size/numChannels), numChannels))

    rawDataLfp = np.memmap(lfp_file, dtype='int16', mode='r')
    dataLfp = np.reshape(rawDataLfp, (int(rawDataLfp.size/numChannels), numChannels))

    info = compute_offset_and_surface_channel(dataAp, dataLfp, \
                args['ephys_params'], args['depth_estimation_params'])

    write_probe_json(output_file, info['channels'], info['offsets'], \
        info['scaling'], info['mask'], info['surface_channel'], info['air_channel'], info['vertical_pos'], info['horizontal_pos'])


    execution_time = time.time() - start

    print('total time: ' + str(execution_time) + ' seconds')
    print( )
        
    return {"surface_channel": info['surface_channel'],
            "air_channel": info['air_channel'],
            "probe_json": output_file,
            "execution_time": execution_time} # output manifest

def main():

    from ._schemas import InputParameters, OutputParameters

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
