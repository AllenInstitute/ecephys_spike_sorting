Mean Waveforms
==============
Extracts mean waveforms from raw data, given Kilosort spike times and cluster IDs.

Computes waveforms separately for individual epochs, as well as for the entire experiment. If no epochs are specified, waveforms are selected randomly from the entire recording. Waveform standard deviation is currently computed, but not saved.

Metrics are computed for every waveform, and include SNR as well as features of the 1D peak-channel waveform and the 2D waveform centered on the soma location.

![1D features](images/1d_waveform_features "1D waveform features")

Source: [Jia et al. (2019) J Neurophys](https://doi.org/10.1152/jn.00680.2018)


Running
-------
```
python -m ecephys_spike_sorting.modules.mean_waveforms --input_json <path to input json> --output_json <path to output json>
```
See the schema file for detailed information about input json contents.


Input data
----------
- **continuous data file** : Raw data in int16 binary format
- **Kilosort outputs** : includes spike times, spike clusters, cluster quality, etc.


Output data
-----------
- **mean_waveforms.npy** : numpy file containing mean waveforms for clusters across all epochs
- **waveform_metrics.csv** : CSV file containing metrics for each waveform