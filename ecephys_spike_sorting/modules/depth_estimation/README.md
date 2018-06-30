Depth Estimation
==============
Creates a JSON file for probe with information about the DC offset of each channel, as well as the channel closest to the brain surface.

Running
-------
```
python -m ecephys_spike_sorting.modules.depth_estimation --input_json <path to input json> --output_json <path to output json>
```
See the schema file for detailed information about input json contents.


Input data
----------
- **ap band and lfp band .dat files** : in16 binary files written by the extract_from_npx module.


Output data
-----------
- **probe_info.json** : contains information about each channel, as well as the surface and air channels for the probe