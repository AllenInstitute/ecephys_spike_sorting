# ecephys spike sorting

https://github.com/AllenInstitute/ecephys_spike_sorting

Modules for spike-sorting Allen Institute Neuropixels data. These modules take data saved by the [Open Ephys GUI](https://github.com/open-ephys/plugin-gui) and prepare it for spike sorting by [Kilosort2](https://github.com/MouseLand/Kilosort2). Following the spike-sorting step (using the [kilosort helper](ecephys_spike_sorting/modules/kilosort_helper/README.md) module), we clean up the outputs and calculate mean waveforms and quality metrics for each unit.

This code is still under development, and we welcome feedback about any step in the pipeline.

Further documentation can be found in each module's README file.


## Modules

[extract from npx](ecephys_spike_sorting/modules/extract_from_npx/README.md): Calls a binary executable that converts data from compressed NPX format into .dat files (continuous data) and .npy files (event data)

[depth estimation](ecephys_spike_sorting/modules/depth_estimation/README.md): Uses the LFP data to identify the surface channel, which is required by the median subtraction and kilosort modules.

[median subtraction](ecephys_spike_sorting/modules/median_subtraction/README.md): Calls a binary executable that removes the DC offset and common-mode noise from the AP band continuous file.

[kilosort helper](ecephys_spike_sorting/modules/kilosort_helper/README.md): Generates config files for Kilosort and launches spike sorting via the Matlab engine.

[kilosort postprocessing](ecephys_spike_sorting/modules/kilosort_postprocessing/README.md): Removes putative double-counted spikes from Kilosort output.

[noise templates](ecephys_spike_sorting/modules/noise_templates/README.md): Identifies noise units based on their waveform shape and ISI histogram.

[automerging](ecephys_spike_sorting/modules/automerging/README.md): Automatically merges templates that belong to the same unit (not currently used, but included in case it's helpful to others).

[mean waveforms](ecephys_spike_sorting/modules/mean_waveforms/README.md): Extracts mean waveforms from the raw data, given spike times and unit IDs.

[quality metrics](ecephys_spike_sorting/modules/quality_metrics/README.md): Calculate quality metrics for each unit to assess isolation and sorting quality.

## Installation and Usage

We recommend using [pipenv](https://github.com/pypa/pipenv) to run these modules. From the `ecephys_spike_sorting` top-level directory, run the following commands:

```shell
    $ pip install --user pipenv
    $ export PIPENV_VENV_IN_PROJECT=1
    $ pipenv install
    $ pipenv shell
    $ pip install .
```
At this point, you can edit one of the processing scripts found in `ecephys_spike_sorting/scripts` and run via:

```shell
    $ python ecephys_spike_sorting/scripts/batch_processing.py
```

To leave the pipenv virtual environment, simply type:

```shell
    $ exit
```

## Entry Points

Installing as a module should automagically expose the aforementioned modules using `setuptools` entry_points

-   extract from npx: `extract-from-npx`
-   depth estimation: `depth-estimation`
-   median subtraction: `median-subtraction`
-   kilosort helper: `kilosort-helper`
-   kilosort postprocessing: `kilosort-postprocessing`
-   noise templates: `noise_templates`
-   automerging: `automerging`
-   mean waveforms: `mean-waveforms`
-   quality metrics: `quality-metrics`

## Level of Support

This code is an important part of the internal Allen Institute code base and we are actively using and maintaining it. Issues are encouraged, but because this tool is so central to our mission, pull requests might not be accepted if they conflict with our existing plans.

## Terms of Use

See [Allen Institute Terms of Use](https://alleninstitute.org/legal/terms-use/)