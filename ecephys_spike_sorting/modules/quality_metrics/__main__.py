from argschema import ArgSchemaParser
import os
import logging
import time

import numpy as np
import pandas as pd

from ecephys_spike_sorting.modules.quality_metrics.metrics import isolation, noise_overlap, isi_contamination

def calculate_quality_metrics(args):

    # code goes here
    
    start = time.time()
    
    spike_times = np.load(os.path.join(args['kilosort_output_directory'],'spike_times.npy'))
    spike_clusters = np.load(os.path.join(args['kilosort_output_directory'],'spike_clusters.npy'))

    f1 = os.path.join(args['extracted_data_directory'], os.path.join('continuous','Neuropix*.0'))
    ap_directory = glob.glob(f1)[0]
    rawDataFile = os.path.join(ap_directory, 'continuous.dat')

    iso = isolation(spike_times, spike_clusters, rawDataFile)
    noise_o = noise_overlap(spike_times, spike_clusters, rawDataFile)
    isi_con = isi_contamination(spike_times, spike_clusters, rawDataFile)

    # make a DataFrame
    # save it to disk
            
    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from _schemas import InputParameters, OutputParameters

    """Main entry point:"""
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
