ECHO off
title Script to run sorting using copy_and_process.py and an input session name
ECHO navigating to code directory
cd C:\Users\svc_neuropix\Documents\GitHub\ecephys_spike_sorting
set /p session_name=Full session name: 
ECHO activating environment and starting ecephys_spike_sorting\scripts\copy_and_process.py
pipenv run python ecephys_spike_sorting\scripts\copy_and_process.py %session_name%
cmd \k



