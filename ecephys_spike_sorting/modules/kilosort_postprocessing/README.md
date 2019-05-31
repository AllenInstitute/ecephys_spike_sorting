Kilosort Post-Processing
==============
Clean up Kilosort outputs by removing putative double-counted spikes.

Kilosort occasionally fits a spike template to the residual of another spike. See [this discussion](https://github.com/MouseLand/Kilosort2/issues/29) for more information.

This module aims to correct for this by removing spikes from the same unit or neighboring units that occur within 5 samples (0.16 ms) of one another. This is not ideal, since it can potentially remove legitimate spike times, but on the whole it seems worth it to avoid having spurious zero-time-lag correlation between units.

We are not currently taking into account spike amplitude when removing spikes; the module just deletes one spike from an overlapping pair that occurs later in time.

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
- **Updated Kilosort output files** : overwrites .npy files for spike times, cluster labels, amplitudes, and PC features. The original outputs can be extracted from the `rez.mat` file if necessary.