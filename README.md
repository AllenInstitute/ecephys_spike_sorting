# ecephys spike sorting

![ecephys_spike_sorting_icon](icon.png)

https://github.com/AllenInstitute/ecephys_spike_sorting

Modules for processing **e**xtra**c**ellular **e**lectro**phys**iology data from Neuropixels probes.

![python versions](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue.svg)


## Overview

This repository contains code for running spike sorting pipelines for the **Allen Brain Observatory.** Public datasets that have been processed with `ecephys_spike_sorting` include [**Visual Coding - Neuropixels**](https://allensdk.readthedocs.io/en/latest/visual_coding_neuropixels.html) and [**Visual Behavior - Neuropixels**](https://allensdk.readthedocs.io/en/latest/visual_behavior_neuropixels.html). Electrophysiology that was spike sorted with this code has appeared in a number of publications, including:

- Siegle, Jia et al. (2021) [Survey of spiking in the mouse visual system reveals functional hierarchy.](https://doi.org/10.1038/s41586-020-03171-x)

- Siegle, Ledochowitsch et al. (2021) [Reconciling functional differences in populations of neurons recorded with two-photon imaging and electrophysiology.](https://doi.org/10.7554/eLife.69068)

- Jia et al. (2022) [Multi-regional module-based signal transmission in mouse visual cortex.](https://doi.org/10.1016/j.neuron.2022.01.027)

## Compatibility

This code is designed to ingest data collected with the [Open Ephys GUI](https://open-ephys.org/gui). [@jenniferColonell](https://github.com/jenniferColonell) from HHMI Janelia Research Campus [maintains a fork](https://github.com/jenniferColonell/ecephys_spike_sorting) that is compatible with data recorded by [SpikeGLX](https://billkarsh.github.io/SpikeGLX/). For the spike sorting step, both versions rely on Kilosort 2 or 2.5.  For more information on Kilosort, please read through the [GitHub wiki](https://github.com/MouseLand/Kilosort/wiki).


## Level of Support

This repository is **no longer under development**, and we recommend that new users base their spike sorting pipelines on [SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/) instead. We believe that even existing `ecephys_spike_sorting` users would benefit from migrating to SpikeInterface. The Allen Institute has already converted its spike sorting workflows to use SpikeInterface, which is actively maintained, works with a range of modern spike sorters, and includes up-to-date implementations of the most important pre- and post-processing methods. The SpikeInterface syntax needed to reproduce the functionality of `ecephys_spike_sorting` can be found in each module's README file.

To get started with SpikeInterface, we recommend reading through [this tutorial on analyzing Neuropixels data](https://spikeinterface.readthedocs.io/en/latest/how_to/analyse_neuropixels.html).

## Modules

The first three modules take data saved by the [Open Ephys GUI](https://github.com/open-ephys/plugin-gui) and prepare it for spike sorting by [Kilosort2](https://github.com/MouseLand/Kilosort2). Following the spike-sorting step (using the [kilosort_helper](ecephys_spike_sorting/modules/kilosort_helper/README.md) module), we clean up the outputs and calculate mean waveforms and quality metrics for each unit.

1. [extract_from_npx](ecephys_spike_sorting/modules/extract_from_npx/README.md) (*deprecated*): Calls a binary executable that converts data from compressed NPX format into .dat files (continuous data) and .npy files (event data). The NPX format is no longer used by Open Ephys (or any other software), so this module can be skipped.

2. [depth_estimation](ecephys_spike_sorting/modules/depth_estimation/README.md): Uses the LFP data to identify the surface channel, which is required by the median subtraction and kilosort modules.

3. [median_subtraction](ecephys_spike_sorting/modules/median_subtraction/README.md): Calls a binary executable that removes the DC offset and common-mode noise from the AP band continuous file.

4. [kilosort_helper](ecephys_spike_sorting/modules/kilosort_helper/README.md): Generates config files for Kilosort and launches spike sorting via the Matlab engine.

5. [kilosort_postprocessing](ecephys_spike_sorting/modules/kilosort_postprocessing/README.md): Removes putative double-counted spikes from Kilosort output.

6. [noise_templates](ecephys_spike_sorting/modules/noise_templates/README.md): Identifies noise units based on their waveform shape and ISI histogram.

7. [mean_waveforms](ecephys_spike_sorting/modules/mean_waveforms/README.md): Extracts mean waveforms from the raw data, given spike times and unit IDs. Also calculates metrics for each waveform.

8. [quality_metrics](ecephys_spike_sorting/modules/quality_metrics/README.md): Calculates quality metrics for each unit to assess isolation and sorting quality.

(Not used) [automerging](ecephys_spike_sorting/modules/automerging/README.md): Automatically merges templates that belong to the same unit (included in case it's helpful to others).


## Installation and Usage

These modules require **Python 3.5+**, and have been tested with Python 3.5, 3.6, and 3.7.

Three of the modules (`extract_from_npx`, `median_subtraction`, and `kilosort_helper`) have non-Python dependencies that will need to be installed prior to use.

We recommend using [pipenv](https://github.com/pypa/pipenv) to run these modules. From the `ecephys_spike_sorting` top-level directory, run the following commands from a terminal:

### Linux

```shell
    $ pip install --user pipenv
    $ export PIPENV_VENV_IN_PROJECT=1
    $ pipenv install
    $ pipenv shell
    (ecephys_spike_sorting) $ pip install .
```
You can now edit one of the processing scripts found in `ecephys_spike_sorting/scripts` and run via:

```shell
    (ecephys_spike_sorting) $ python ecephys_spike_sorting/scripts/batch_processing.py
```
See the scripts [README](ecephys_spike_sorting/scripts/README.md) file for more information on their usage.

To leave the pipenv virtual environment, simply type:

```shell
    (ecephys_spike_sorting) $ exit
```

### macOS

If you don't have it already, install [homebrew](https://brew.sh/). Then, type:

```shell
    $ brew install pipenv
    $ export PIPENV_VENV_IN_PROJECT=1
    $ pipenv install
    $ pipenv shell
    (ecephys_spike_sorting) $ pip install .
```
You can now edit one of the processing scripts found in `ecephys_spike_sorting/scripts` and run via:

```shell
    (ecephys_spike_sorting) $ python ecephys_spike_sorting/scripts/batch_processing.py
```
See the scripts [README](ecephys_spike_sorting/scripts/README.md) file for more information on their usage.

To leave the pipenv virtual environment, simply type:

```shell
    (ecephys_spike_sorting) $ exit
```

### Windows

```shell
    $ pip install --user pipenv
    $ set PIPENV_VENV_IN_PROJECT=1
    $ pipenv install
    $ pipenv shell
    (.venv) $ pip install .
```
**Note:** This will work in the standard Command Prompt, but the [cmder console emulator](https://cmder.net/) has better compatibility with Python virtual environments.

You can now edit one of the processing scripts found in `ecephys_spike_sorting\scripts` and run via:

```shell
    (.venv) $ python ecephys_spike_sorting\scripts\batch_processing.py
```
See the scripts [README](ecephys_spike_sorting/scripts/README.md) file for more information on their usage.

To leave the pipenv virtual environment, simply type:

```shell
    (.venv) $ exit
```


## Terms of Use

See [Allen Institute Terms of Use](https://alleninstitute.org/legal/terms-use/)


© 2019 Allen Institute for Brain Science
