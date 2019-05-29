from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time

import numpy as np

from .postprocessing import remove_double_counted_spikes

def run_postprocessing(args):

    spike_times, spike_clusters, amplitudes, templates, channel_map, clusterIDs, cluster_quality, pc_features, pc_feature_ind = \
                load_kilosort_data(args['directories']['kilosort_output_directory'], \
                    args['ephys_params']['sample_rate'], \
                    convert_to_seconds = False,
                    use_master_clock = False,
                    include_pcs = True)

    spike_times, spike_clusters, amplitudes, pc_features, overlap_matrix = \
        remove_double_counted_spikes(spike_times, 
                                     spike_clusters, 
                                     amplitudes, 
                                     channel_map,
                                     templates, 
                                     pc_features, 
                                     pc_feature_ind, 
                                     args['ephys_params']['sample_rate'],
                                     args['ks_postprocessing_params'])

    # save data -- it's fine to overwrite existing files, because the original outputs are stored in rez.mat
    np.save(os.path.join(args['directories']['kilosort_output_directory'], 'spike_times.npy'), spike_times)
    np.save(os.path.join(args['directories']['kilosort_output_directory'], 'amplitudes.npy'), amplitudes)
    np.save(os.path.join(args['directories']['kilosort_output_directory'], 'spike_clusters.npy'), spike_clusters)
    np.save(os.path.join(args['directories']['kilosort_output_directory'], 'pc_features.npy'), pc_features)
    np.save(os.path.join(args['directories']['kilosort_output_directory'], 'overlap_matrix.npy'), overlap_matrix)

    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from ._schemas import InputParameters, OutputParameters

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = run_postprocessing(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
