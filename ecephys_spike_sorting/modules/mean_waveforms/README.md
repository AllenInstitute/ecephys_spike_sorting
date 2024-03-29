# Mean Waveforms

Extracts mean waveforms from raw data, given spike times and cluster IDs.

Computes waveforms separately for individual epochs, as well as for the entire experiment. If no epochs are specified, waveforms are selected randomly from the entire recording. Waveform standard deviation is currently computed, but not saved.

Metrics are computed for every waveform, and include features of the 1D peak-channel waveform and the 2D waveform centered on the soma location.

![1D features](images/1d_waveform_features.png "1D waveform features")

**1D waveform features**: Waveform duration, peak-trough ratio, repolarization slope, and recovery slope.

![2D waveform](images/2d_waveform.png "2D waveform")

**Example 2D waveform**: Signals from channels along one edge of the probe are smoothed with a moving average to create the 2D waveform. Green dots indicate the location of the waveform trough on each channel.

![2D features](images/2d_waveform_features.png "2D waveform features")

**2D waveform features**: Waveform spread, velocity above the soma, and velocity below the soma.

Source: [Jia et al. (2019) "High-density extracellular probes reveal dendritic backpropagation and facilitate neuron classification." _J Neurophys_ **121**: 1831-1847](https://doi.org/10.1152/jn.00680.2018)

### SpikeInterface implementation

SpikeInterface uses a `WaveformExtractor` object to pull spike waveforms out of the raw data and compute metrics on their shape.

Extracting the mean waveforms from a sorting and computing a variety of waveform metrics only requires two lines of code:

```python
import spikeinterface.full as si

from spikeinterface.postprocessing import compute_template_metrics

waveform_extractor = si.extract_waveforms(recording=recording, 
                                          sorting=sorting, 
                                          folder='waveforms')

template_metrics = compute_template_metrics(waveform_extractor)
display(template_metrics)

```

More information can be found in the documentation for the [Postprocessing module](https://spikeinterface.readthedocs.io/en/latest/modules/postprocessing.html).


## Running

```
python -m ecephys_spike_sorting.modules.mean_waveforms --input_json <path to input json> --output_json <path to output json>
```
Two arguments must be included:
1. The location of an existing file in JSON format containing a list of paths and parameters.
2. The location to write a file in JSON format containing information generated by the module while it was run.

See the `_schemas.py` file for detailed information about the contents of the input JSON.

## Input data

- **AP band .dat or .bin file** : int16 binary files written by [Open Ephys](https://github.com/open-ephys/plugin-GUI), [SpikeGLX](https://github.com/billkarsh/spikeglx), or the `extract_from_npx` module.
- **Kilosort outputs** : includes spike times, spike clusters, cluster quality, etc.


## Output data

- **mean_waveforms.npy** : numpy file containing mean waveforms for clusters across all epochs
- **waveform_metrics.csv** : CSV file containing metrics for each waveform