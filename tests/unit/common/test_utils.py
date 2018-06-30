import pytest
import numpy as np
import os

import ecephys_spike_sorting.common.utils as utils

DATA_DIR = os.environ.get('ECEPHYS_SPIKE_SORTING_DATA', False)

def test_read_cluster_group_tsv():

	filename = os.path.join(DATA_DIR, 'cluster_group.tsv')

	cluster_ids, cluster_quality = utils.read_cluster_group_tsv(filename)

	assert(len(cluster_ids) == len(cluster_quality))