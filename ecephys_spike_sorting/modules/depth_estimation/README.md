# Depth Estimation

Creates a JSON file with information about the DC offset of each channel, as well as the channel closest to the brain surface. This information is needed to perform the median subtraction step.

### SpikeInterface implementation

`detect_bad_channels()` can be used to detect which channels are outside the brain, as well as channels that have abnormally high levels of noise.

This function returns both the `bad_channel_ids` and `channel_labels`, which can be `good`, `noise`, `dead`, or `out` (outside of the brain). These can then be removed from the recording so they are ignored by the spike sorter:

```python
from spikeinterface.preprocessing import detect_bad_channels

# detect noisy, dead, and out-of-brain channels
bad_channel_ids, channel_labels = detect_bad_channels(recording)
rec_clean = recording.remove_channels(remove_channel_ids=bad_channel_ids)

```

More information can be found in the documentation for the [Preprocessing module](https://spikeinterface.readthedocs.io/en/latest/modules/preprocessing.html).

## Method

![Depth estimation](images/probe_depth.png "Surface estimation method")

This module uses the sharp increase in low-frequency LFP band power to estimate the brain surface location.

## Running

```
python -m ecephys_spike_sorting.modules.depth_estimation --input_json <path to input json> --output_json <path to output json>
```
Two arguments must be included:
1. The location of an existing file in JSON format containing a list of paths and parameters.
2. The location to write a file in JSON format containing information generated by the module while it was run.

See the `_schemas.py` file for detailed information about the contents of the input JSON.

## Input data

- **AP band and LFP band .dat or .bin files** : int16 binary files written by [Open Ephys](https://github.com/open-ephys/plugin-GUI), [SpikeGLX](https://github.com/billkarsh/spikeglx), or the `extract_from_npx` module.


## Output data

- **probe_info.json** : contains information about each channel, as well as the surface channel for the probe
- **probe_depth.png** : image showing the estimated surface channel location