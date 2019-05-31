Quality Metrics
==============
Computes quality metrics for sorted units. Similar to the `mean_waveforms` module, this module can calculate metrics separately for individual epochs. If no epochs are specified, metrics are computed for the entire recording.

Included Metrics
----------------

| Metric             | Icon                     | Description                                        |    Reference     |
| ------------------ |:------------------------:| -------------------------------------------------- | -----------------|
| Firing rate        |                          | Mean spike rate in an epoch                        |                  |
| Presence ratio     |                          | Fraction of epoch in which spikes are present      |                  |
| ISI violations     |![](images/isi_viol.png)  | Rate of refractory-period violations               |                  |
| Amplitude cutoff   |![](images/amp_cut.png)   | Estimate of miss rate based on amplitude histogram |                  |
| Isolation distance |![](images/isol_dist.png) | Distance to nearest cluster in Mahalanobis space   | Schmitzer-Torbert et al. (2005) _Neuroscience_ **131**, 1-11 |
| L-ratio            |                          |                                                    |         "         |
| _d'_               |![](images/d_prime.png)   | Classification accuracy based on LDA               | Hill et al. (2011) _J Neurosci_ **31**, 8699-9705 |
| Nearest-neighbors  |![](images/nn_overlap.png)| Non-parametric estimate of unit contamination      | Chung et al. (2017) _Neuron_ **95**, 1381-1394 |


A Note on Calculations
---------------------
For metrics based on waveform principal components (isolation distance, L-ratio, _d'_, and nearest neighbors hit rate and false alarm rate), it is typical to compute the metrics for all pairs of units and report the "worst-case" value. We have found that this tends to over-estimate the degree of contamination for units with low firing rates. Instead, we compute metrics by sub-selecting spikes from _all_ other units on the same set of channels, which seems to give a more accurate picture of isolation quality. We would appreciate feedback on whether this approach makes sense.


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