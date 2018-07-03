Quality Metrics
==============
Computes quality metrics for sorted spikes


Running
-------
```
python -m ecephys_spike_sorting.modules.quality_metrics --input_json <path to input json> --output_json <path to output json>
```
See the schema file for detailed information about input json contents.


Input data
----------
- **continuous data file** : Raw data in int16 binary format
- **Kilosort outputs** : includes spike times, spike clusters, cluster quality, etc.


Output data
-----------
- **metrics.csv** : CSV containing metrics for all units