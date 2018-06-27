import os
import ast

import pytest
import pandas as pd

from ecephys_spike_sorting.modules.extract_from_npx.__main__ import run_npx_extractor
from ecephys_spike_sorting.modules.depth_estimation.__main__ import run_depth_estimation
from ecephys_spike_sorting.modules.median_subtraction.__main__ import run_median_subtraction

DATA_DIR = r'C:\Users\joshs\Documents\GitHub\ecephys_spike_sorting\test_data'
#os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

RUN_TESTS = bool(DATA_DIR) #and MODULE_INTEGRATION_TESTS

@pytest.mark.skipif(not RUN_TESTS, reason='You must opt in to the module integration tests.')
def test_npx_extractor(tmpdir_factory):

    base_path = tmpdir_factory.mktemp('npx_extractor_integration')

    args = {
        'npx_file' : os.path.join(DATA_DIR, 'test.npx'),
        'extracted_data_directory': os.path.join(DATA_DIR, 'output'),
        'npx_extractor_executable': r'C:\Users\joshs\Documents\GitHub\NpxExtractor\Release\NpxExtractor.exe',
		'save_depth_estimation_figure': True,
		'depth_estimation_figure_location': DATA_DIR,
		'median_subtraction_executable': r'C:\Users\joshs\Documents\GitHub\spikebandmediansubtraction\Builds\VisualStudio2013\Release\SpikeBandMedianSubtraction.exe',
    }

    #output = run_npx_extractor(args)

    #args.update(output)

    output = run_depth_estimation(args)

    args.update(output)

    output = run_median_subtraction(args)

    args.update(output)

    # make sure output is correct



    #obtained = pd.read_csv(args['output_stimulus_table_path'])
    #expected = pd.read_csv(os.path.join(DATA_DIR, '706875901_stimulus_table.csv'))

    #pd.testing.assert_frame_equal( expected, obtained )