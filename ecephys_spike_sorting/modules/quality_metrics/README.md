Quality Metrics
==============
Computes quality metrics for sorted units. Similar to the `mean_waveforms` module, this module can calculate metrics separately for individual epochs. If no epochs are specified, metrics are computed for the entire recording.

Included Metrics
----------------

| Metric             | Icon                     | Description                                        |    Reference     |
| ------------------ |:------------------------:| -------------------------------------------------- | -----------------|
| Firing rate        |                          | Mean spike rate in an epoch                        |                  |
| Presence ratio     |                          | Fraction of epoch in which spikes are present      |                  |
| Amplitude cutoff   |![](images/amp_cut.png)   | Estimate of miss rate based on amplitude histogram |                  |
| Isolation distance |![](images/isol_dist.png) | Distance to nearest cluster in Mahalanobis space   |                  |
| L-ratio            |                          |                                                    |                  |
| d'                 |![](images/d_prime.png)   | Classification accuracy based on LDA               |                  |
| Nearest-neighbors  |![](images/nn_overlap.png)| Non-parametric estimate of unit contamination      |                  |

A Note on Calculation
---------------------


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