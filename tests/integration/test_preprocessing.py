import os
import ast

import pytest
import pandas as pd

from ecephys_spike_sorting.modules.extract_from_npx.__main__ import run_npx_extractor

DATA_DIR = r'C:\Users\joshs\Documents\GitHub\ecephys_spike_sorting\test_data'
#os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

RUN_TESTS = bool(DATA_DIR) #and MODULE_INTEGRATION_TESTS

@pytest.mark.skipif(not RUN_TESTS, reason='You must opt in to the module integration tests.')
def test_npx_extractor(tmpdir_factory):

    base_path = tmpdir_factory.mktemp('npx_extractor_integration')

    args = {
        'npx_file_location' : os.path.join(DATA_DIR, 'test.npx'),
        'output_file_location': os.path.join(DATA_DIR, 'output'),
        'executable_file': os.path.join(r'C:\Users\joshs\Documents\GitHub\NpxExtractor\Release\NpxExtractor.exe'),
    }

    output = run_npx_extractor(args)

    # make sure output is correct

    

    #obtained = pd.read_csv(args['output_stimulus_table_path'])
    #expected = pd.read_csv(os.path.join(DATA_DIR, '706875901_stimulus_table.csv'))

    #pd.testing.assert_frame_equal( expected, obtained )