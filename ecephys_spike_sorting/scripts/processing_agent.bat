ECHO off
title Processing Agent
ECHO navigating to code directory
cd C:\Users\svc_neuropix\Documents\GitHub\ecephys_spike_sorting
ECHO activating environment and starting ecephys_spike_sorting\scripts\cortex_from_extraction.py
pipenv run python ecephys_spike_sorting\scripts\batch_processing_gui.py
cmd \k



