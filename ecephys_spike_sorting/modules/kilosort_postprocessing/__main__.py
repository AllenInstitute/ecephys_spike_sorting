from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time

import numpy as np

from ...common.utils import load_kilosort_data, getSortResults

from .postprocessing import remove_double_counted_spikes
from .postprocessing import align_spike_times

def run_postprocessing(args):

    print('ecephys spike sorting: kilosort postprocessing module')

    print("Loading data...")

    #print(args.keys())
    #print(args['directories'].keys())

    start = time.time()
    
    include_pcs = args['ks_postprocessing_params']['include_pcs']
    
    if include_pcs:
        spike_times, spike_clusters, spike_templates, amplitudes, templates, channel_map, \
        channel_pos, clusterIDs, cluster_quality, cluster_amplitude, pc_features, pc_feature_ind, template_features = \
                    load_kilosort_data(args['directories']['kilosort_output_directory'], \
                        args['ephys_params']['sample_rate'], \
                        convert_to_seconds = False, \
                        use_master_clock = False, \
                        include_pcs = include_pcs )
    else:
        spike_times, spike_clusters, spike_templates, amplitudes, templates, channel_map, \
        channel_pos, clusterIDs, cluster_quality, cluster_amplitude = \
                    load_kilosort_data(args['directories']['kilosort_output_directory'], \
                        args['ephys_params']['sample_rate'], \
                        convert_to_seconds = False, \
                        use_master_clock = False, \
                        include_pcs = include_pcs )
        # empty arrays to stand in for the missing variables
        pc_features = []
        pc_feature_ind = []
        template_features = []
        
    if args['ks_postprocessing_params']['align_avg_waveform']: 
        spike_times = align_spike_times(spike_times,
                                        spike_clusters,
                                        args['ephys_params']['ap_band_file'], 
                                        args['directories']['kilosort_output_directory'], 
                                        args['ks_postprocessing_params']['cWaves_path'])
        
    if args['ks_postprocessing_params']['remove_duplicates']:
        spike_times, spike_clusters, spike_templates, amplitudes, pc_features, \
        template_features, overlap_matrix, overlap_summary = \
            remove_double_counted_spikes(spike_times, 
                                         spike_clusters,
                                         spike_templates, 
                                         amplitudes, 
                                         channel_map,
                                         channel_pos,
                                         templates, 
                                         pc_features, 
                                         pc_feature_ind, 
                                         template_features,
                                         cluster_amplitude,
                                         args['ephys_params']['sample_rate'],
                                         args['ks_postprocessing_params'])


    print("Saving data...")

    # save data -- it's fine to overwrite existing files, because the original outputs are stored in rez.mat
    output_dir = args['directories']['kilosort_output_directory']
    np.save(os.path.join(output_dir, 'spike_times.npy'), spike_times)
    np.save(os.path.join(output_dir, 'amplitudes.npy'), amplitudes)
    np.save(os.path.join(output_dir, 'spike_clusters.npy'), spike_clusters)
    np.save(os.path.join(output_dir, 'spike_templates.npy'), spike_templates)
    
    if args['ks_postprocessing_params']['include_pcs']:
        np.save(os.path.join(output_dir, 'pc_features.npy'), pc_features)
        np.save(os.path.join(output_dir, 'template_features.npy'), template_features)
    
    if args['ks_postprocessing_params']['remove_duplicates']:
        np.save(os.path.join(output_dir, 'overlap_matrix.npy'), overlap_matrix)
        np.save(os.path.join(output_dir, 'overlap_summary.npy'), overlap_summary)
        # save the overlap_summary as a text file -- allows user to easily understand what happened
        np.savetxt(os.path.join(output_dir, 'overlap_summary.csv'), overlap_summary, fmt = '%d', delimiter = ',')

    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time,2)) + ' seconds')
    print( )
    
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
