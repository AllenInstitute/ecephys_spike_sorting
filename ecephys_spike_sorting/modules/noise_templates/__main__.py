from argschema import ArgSchemaParser
import os
import logging
import time

import numpy as np

from .id_noise_templates import id_noise_templates

from ...common.utils import write_cluster_group_tsv, load_kilosort_data


def classify_noise_templates(args):

    print('ecephys spike sorting: noise templates module')
    
    start = time.time()

    spike_times, spike_clusters, spike_templates, amplitudes, templates, channel_map, cluster_ids, cluster_quality = \
            load_kilosort_data(args['directories']['kilosort_output_directory'], \
                args['ephys_params']['sample_rate'], \
                convert_to_seconds = True)

    cluster_ids, is_noise = id_noise_templates(cluster_ids, templates, np.squeeze(channel_map), \
        args['noise_waveform_params'])

    mapping = {False: 'good', True: 'noise'}
    labels = [mapping[value] for value in is_noise]

    write_cluster_group_tsv(cluster_ids, 
                            labels, 
                            args['directories']['kilosort_output_directory'], 
                            args['ephys_params']['cluster_group_file_name'])
    
    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time,2)) + ' seconds')
    print()
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from ._schemas import InputParameters, OutputParameters

    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = classify_noise_templates(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
