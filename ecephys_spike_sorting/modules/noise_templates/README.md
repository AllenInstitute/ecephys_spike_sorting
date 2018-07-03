Noise Templates
==============
Identifies noise (non-neural) units in Kilosort outputs.

Running
-------
```
python -m ecephys_spike_sorting.modules.noise_templates --input_json <path to input json> --output_json <path to output json>
```
See the schema file for detailed information about input json contents.


Input data
----------
- **Kilosort outputs** : includes spike times, spike clusters, templates, etc.


Output data
-----------
- **cluster_group.tsv** : labels for each cluster in spike_clusters.npy