from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time

import numpy as np

from ecephys_spike_sorting.modules.noise_templates.id_noise_templates import id_noise_templates
from ecephys_spike_sorting.common.utils import write_cluster_group_tsv

def classify_noise_templates(args):

    folder = args['kilosort_output_directory']
    
    logging.info('Running noise template identification')
    
    start = time.time()
    
    spike_times = np.load(os.path.join(folder,'spike_times.npy'))
    spike_templates = np.load(os.path.join(folder,'spike_templates.npy'))
    amplitudes = np.load(os.path.join(folder,'amplitudes.npy'))
    templates = np.load(os.path.join(folder,'templates.npy'))
    unwhitening_mat = np.load(os.path.join(folder,'whitening_mat_inv.npy'))
                    
    templates = templates[:,21:,:] # remove zeros
    spike_templates = np.squeeze(spike_templates) # fix dimensions
    spike_times = np.squeeze(spike_times) / args['sample_rate'] # fix dimensions and convert to seconds
                    
    unwhitened_temps = np.zeros((templates.shape))
    
    for temp_idx in range(templates.shape[0]):
        
        unwhitened_temps[temp_idx,:,:] = np.dot(np.ascontiguousarray(templates[temp_idx,:,:]),np.ascontiguousarray(unwhitening_mat))
                    
        
     # LOTS OF HARD-CODED PARAMETERS IN HERE:
    templateIDs, is_noise = id_noise_templates(spike_templates, unwhitened_temps, spike_times)
    
    quality = np.zeros(is_noise.shape)
    quality[is_noise] = -1
    
    logging.info('Writing cluster groups file')
    write_cluster_group_tsv(templateIDs, quality, folder)
        
    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from _schemas import InputParameters, OutputParameters

    """Main entry point:"""
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
