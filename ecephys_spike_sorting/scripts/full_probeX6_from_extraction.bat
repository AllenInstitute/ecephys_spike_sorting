ECHO off
title Script to run sorting using full_from_extraction_6probe.py and an input session name
ECHO navigating to code directory
ECHO THIS SCRIPT PROCESSES 6 PROBES
ECHO DO NOT START PROCESSING ON THE OTHER PROCESSING COMPUTER FOR THE SAME SESSION
cd C:\Users\svc_neuropix\Documents\GitHub\ecephys_spike_sorting
set /p session_name=Full session name from EXPERIMENT DAY 2: 
ECHO DO NOT START PROCESSING ON THE OTHER PROCESSING COMPUTER FOR THIS SESSION
ECHO activating environment and starting ecephys_spike_sorting\scripts\full_from_extraction_6probe.py
pipenv run python ecephys_spike_sorting\scripts\full_from_extraction_6probe.py %session_name%
cmd \k



