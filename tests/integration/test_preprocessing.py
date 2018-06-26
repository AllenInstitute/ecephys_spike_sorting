import os
import ast

import pytest
import pandas as pd

from ecephys_spike_sorting.modules.extract_from_npx.__main__ import run_npx_extractor


#MODULE_INTEGRATION_TESTS = ast.literal_eval(os.environ.get('ECEPHYS_PIPELINE_MODULE_INTEGRATION_TESTS', False))
DATA_DIR = os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

# this one is actually pretty fast
RUN_TESTS = bool(DATA_DIR) #and MODULE_INTEGRATION_TESTS


@pytest.mark.skipif(not RUN_TESTS, reason='You must opt in to the module integration tests.')
def test_npx_extractor(tmpdir_factory):

    base_path = tmpdir_factory.mktemp('npx_extractor_integration')

    args = {
        'stimulus_pkl_path': os.path.join(DATA_DIR, '706875901_388187_20180607.stim.pkl'),
        'sync_h5_path': os.path.join(DATA_DIR, '706875901_388187_20180607.sync'),
        'output_stimulus_table_path': os.path.join(str(base_path), '706875901_stimulus_table.csv')
    }

    run_npx_extractor(args)

    obtained = pd.read_csv(args['output_stimulus_table_path'])
    expected = pd.read_csv(os.path.join(DATA_DIR, '706875901_stimulus_table.csv'))

    pd.testing.assert_frame_equal( expected, obtained )