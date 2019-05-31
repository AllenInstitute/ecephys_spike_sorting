Depth Estimation
==============
Creates a JSON file with information about the DC offset of each channel, as well as the channel closest to the brain surface. This information is needed to perform the median subtraction step.

Implementation
--------------
![Depth estimation](images/probe_depth.png "Surface estimation method")
This module uses the sharp increase in low-frequency LFP band power to estimate the brain surface location.

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
- **probe_info.json** : contains information about each channel, as well as the surface channel for the probe
- **probe_depth.png** : image showing the estimated surface channel location