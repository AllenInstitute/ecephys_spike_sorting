Median Subtraction
==============
Calls a binary executable that removes the DC offset and common-mode noise from a spike-band continuous file.

Running
-------
```
python -m ecephys_spike_sorting.modules.depth_estimation --input_json <path to input json> --output_json <path to output json>
```
See the schema file for detailed information about input json contents.


Input data
----------
- **ap band .dat file** : int16 binary files written by the extract_from_npx module.
- **probe_info.json** : file written by depth_estimation module.

Output data
-----------
- **ap band .dat file** : overwrites the existing file with the median-subtracted data.