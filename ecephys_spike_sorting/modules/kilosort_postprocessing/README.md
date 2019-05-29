Kilosort Post-Processing
==============
Clean-up Kilosort outputs by removing putative double-counted spikes.

Running
-------
```
python -m ecephys_spike_sorting.modules.kilosort_postprocessing --input_json <path to input json> --output_json <path to output json>
```
See the schema file for detailed information about input json contents.


Input data
----------
- **Kilosort output files** : .npy files containing spike times, cluster labels, templates, etc.

Output data
-----------
- **Updated Kilosort output files** : updated .npy files for spike times, cluster labels, amplitudes, and PC features 