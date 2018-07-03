Kilosort Helper
==============
Python wrapper for Matlab-based Kilosort spike sorting.

Running
-------
```
python -m ecephys_spike_sorting.modules.kilosort_helper --input_json <path to input json> --output_json <path to output json>
```
See the schema file for detailed information about input json contents.


Input data
----------
- **ap band .dat file** : in16 binary files written by the extract_from_npx module.

Output data
-----------
- **Kilosort output files** : .npy files containing spike times, cluster labels, templates, etc.