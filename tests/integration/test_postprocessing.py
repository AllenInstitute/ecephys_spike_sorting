import os
import ast

import pytest
import pandas as pd

from ecephys_spike_sorting.modules.noise_templates.__main__ import classify_noise_templates
from ecephys_spike_sorting.modules.automerging.__main__ import run_automerging
from ecephys_spike_sorting.modules.mean_waveforms.__main__ import calculate_mean_waveforms
from ecephys_spike_sorting.modules.quality_metrics.__main__ import calculate_quality_metrics

DATA_DIR = r'C:\Users\joshs\Documents\GitHub\ecephys_spike_sorting\test_data'
#os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

RUN_TESTS = bool(DATA_DIR) #and MODULE_INTEGRATION_TESTS

@pytest.mark.skipif(not RUN_TESTS, reason='You must opt in to the module integration tests.')
def test_postprocessing(tmpdir_factory):

    #base_path = tmpdir_factory.mktemp('npx_extractor_integration')

    args = {
        'extracted_data_directory': os.path.join(DATA_DIR, 'output'),
        'kilosort_output_directory': os.path.join(DATA_DIR, 'kilosort'),
        'num_channels': 384,
        'sample_rate': 30000.0
    }

    output = classify_noise_templates(args)

    args.update(output)

    output = run_automerging(args)

    args.update(output)

    output = calculate_mean_waveforms(args)

    args.update(output)

    output = calculate_quality_metrics(args)

    # make sure output is correct



    #obtained = pd.read_csv(args['output_stimulus_table_path'])
    #expected = pd.read_csv(os.path.join(DATA_DIR, '706875901_stimulus_table.csv'))

    #pd.testing.assert_frame_equal( expected, obtained )