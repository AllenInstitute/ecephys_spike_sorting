ECHO off
title Script to run sorting using full_from_kilosort.py and an input session name
ECHO navigating to code directory
cd C:\Users\svc_neuropix\Documents\GitHub\ecephys_spike_sorting
ECHO THIS SCRIPT PROCESSES 3 PROBES, YOU MUST ALSO START PROCESSING ON THE OTHER PROCESSING COMPUTER
set /p session_name=Full session name from EXPERIMENT DAY 1: 
ECHO activating environment and starting ecephys_spike_sorting\scripts\full_from_kilosort.py
pipenv run python ecephys_spike_sorting\scripts\full_from_kilosort.py %session_name%
cmd \k



