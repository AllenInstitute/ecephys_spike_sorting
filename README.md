ecephys spike sorting
===============================

https://github.com/AllenInstitute/ecephys_spike_sorting

Modules for spike-sorting Allen Insitute Neuropixels data


## Modules
[extract from npx](ecephys_spike_sorting/modules/extract_from_npx/README.md): Calls a binary executable that converts data from compressed NPX format into .dat files (continuous data) and .npy files (event data)

[depth estimation](ecephys_spike_sorting/modules/depth_estimation/README.md): Uses the LFP data to identify the surface channel, which is required by the median subtraction and kilosort modules.

[median subtraction](ecephys_spike_sorting/modules/median_subtraction/README.md): Calls a binary executable that removes the DC offset and common-mode noise from the AP band continuous file.

[kilosort helper](ecephys_spike_sorting/modules/kilosort_helper/README.md): Generates config files for Kilosort and launches spike sorting via the Matlab engine.

[noise templates](ecephys_spike_sorting/modules/noise_templates/README.md): Identifies noise units based on their waveform shape and ISI histogram.

[automerging](ecephys_spike_sorting/modules/automerging/README.md): Automatically merges templates that belong to the same unit.

[mean waveforms](ecephys_spike_sorting/modules/mean_waveforms/README.md): Extracts mean waveforms from the raw data, given spike times and unit IDs.

[quality metrics](ecephys_spike_sorting/modules/quality_metrics/README.md): Calculate quality metrics for each unit to assess isolation and sorting quality.



