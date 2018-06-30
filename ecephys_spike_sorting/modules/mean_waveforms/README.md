Mean Waveforms
==============
Extracts mean waveforms from raw data, given spike times and cluster IDs.

Computes waveforms separately for individual epochs linearly spaced throughout the experiment, as well as for the entire experiment. Waveform standard deviation is also saved.


Running
-------
```
python -m ecephys_spike_sorting.modules.mean_waveforms --input_json <path to input json> --output_json <path to output json>
```
See the schema file for detailed information about input json contents.


Input data
----------
- **continuous data file** : Raw data in 
- **Kilosort outputs** : includes spike times, spike clusters, cluster quality, etc.


Output data
-----------
- **mean_waveforms.nc** : NetCDF file containing mean waveforms for good clusters across all epochs