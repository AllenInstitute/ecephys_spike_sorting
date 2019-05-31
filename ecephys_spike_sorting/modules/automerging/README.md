Automerging
==============
Looks for clusters that likely belong to the same cell, and merges them automatically.

This is not currently part of our pipeline since switching to Kilosort2, but we're keeping the code around in case others find it useful. For example, it could be helpful for matching units across a series of chronic recordings.


Running
-------
```
python -m ecephys_spike_sorting.modules.automerging --input_json <path to input json> --output_json <path to output json>
```
See the schema file for detailed information about input json contents.


Input data
----------
- **Kilosort outputs** : includes spike times, spike clusters, cluster quality, etc.


Output data
-----------
- **spike_clusters.npy** : updated with new cluster labels
- **cluster_group.tsv** : updated with new cluster labels