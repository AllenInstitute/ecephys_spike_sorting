from argschema import ArgSchemaParser
import os
import logging
import time

import numpy as np
import pandas as pd

from ecephys_spike_sorting.common.utils import get_ap_band_continuous_file
from ecephys_spike_sorting.common.utils import load_kilosort_data
from ecephys_spike_sorting.common.epoch import get_epochs_from_nwb_file

from ecephys_spike_sorting.modules.quality_metrics.metrics import calculate_metrics


def calculate_quality_metrics(args):

    print("Calculating quality metrics...")

    start = time.time()

    print("Loading data...")

    spike_times, spike_clusters, amplitudes, templates, channel_map, clusterIDs, cluster_quality, pc_features, pc_feature_ind = \
            load_kilosort_data(args['directories']['kilosort_output_directory'], \
                args['ephys_params']['sample_rate'], \
                use_master_clock = True,
                include_pcs = True)

    epochs = get_epochs_from_nwb_file(args['nwb_file'])

    metrics = calculate_metrics(spike_times, spike_clusters, amplitudes, channel_map, pc_features, pc_feature_ind, args['quality_metrics_params'], epochs)
    
    output_file = args['quality_metrics_params']['quality_metrics_output_file']

    #waveform_metrics = np.load(args['waveforms_metrics_file'])
    # join waveform metrics and quality metrics dataframes

    print("Saving data")
    metrics.to_csv(output_file)

    execution_time = time.time() - start
    
    return {"execution_time" : execution_time,
            "quality_metrics_output_file" : output_file} # output manifest


def main():

    from ._schemas import InputParameters, OutputParameters

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
