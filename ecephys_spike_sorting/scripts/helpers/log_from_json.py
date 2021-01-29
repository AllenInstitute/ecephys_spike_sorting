# -*- coding: utf-8 -*-
import numpy as np
import os
import json
from datetime import datetime
from pathlib import Path
from tkinter import Tk
from tkinter import filedialog

# Fill in a predefined row of a log table
# Entries are:
# session name (run_probe); number of clusters, number of spikes,
# execution time for kilosort, KS postprocessing (duplicate removal),
# noise templates, mean waveforms, and QC calculations
#
def addEntry(modules, jsondir, session_id, logFullPath):

    log_entry = ['None'] * 9
    sep = ','

    log_entry[0] = session_id
    now = datetime.now()
    log_entry[1] = now.strftime("%m/%d/%Y, %H:%M:%S")

    if 'kilosort_helper' in modules:
        jsonName = session_id + '-kilosort_helper-output.json'
        jsonFile = os.path.join(jsondir, jsonName)
        print(jsonFile)
        with open(jsonFile) as currJson:
            modData = json.load(currJson)
        log_entry[2] = repr(modData['nTot'])
        log_entry[3] = repr(modData['nTemplate'])
        log_entry[4] = '{:.2f}'.format(modData['execution_time'])

    if 'kilosort_postprocessing' in modules:
        jsonName = session_id + '-kilosort_postprocessing-output.json'
        jsonFile = os.path.join(jsondir, jsonName)
        print(jsonFile)
        with open(jsonFile) as currJson:
            modData = json.load(currJson)
        log_entry[5] = '{:.2f}'.format(modData['execution_time'])

    if 'noise_templates' in modules:
        jsonName = session_id + '-noise_templates-output.json'
        jsonFile = os.path.join(jsondir, jsonName)
        print(jsonFile)
        with open(jsonFile) as currJson:
            modData = json.load(currJson)
        log_entry[6] = '{:.2f}'.format(modData['execution_time'])

    if 'mean_waveforms' in modules:
        jsonName = session_id + '-mean_waveforms-output.json'
        jsonFile = os.path.join(jsondir, jsonName)
        print(jsonFile)
        with open(jsonFile) as currJson:
            modData = json.load(currJson)
        log_entry[7] = '{:.2f}'.format(modData['execution_time'])

    if 'quality_metrics' in modules:
        jsonName = session_id + '-quality_metrics-output.json'
        jsonFile = os.path.join(jsondir, jsonName)
        print(jsonFile)
        with open(jsonFile) as currJson:
            modData = json.load(currJson)
        log_entry[8] = '{:.2f}'.format(modData['execution_time'])

    log_entry_str = sep.join(log_entry)
    with open(logFullPath, 'a') as log:
        log.write(log_entry_str + '\n')


# write header to file
def writeHeader(logFullPath):
    with open(logFullPath, 'w') as log:
        log.write('session_id,date_run,time_run,ntot,nTemplate,KS2_time,KS_postprocess_time,noise_template_time,mean_waveform_time,QC_time\n')


# For testing, prompt user for kilosort_helper-out.json,
# get directory and session name, parse make an output log file
#
def main():

    # Get file from user
    root = Tk()         # create the Tkinter widget
    root.withdraw()     # hide the Tkinter root window

    # Windows specific; forces the window to appear in front
    root.attributes("-topmost", True)

    fullPath = Path(filedialog.askopenfilename(title="Select kilosort_helper-output.json"))
    root.destroy()      # destroy the Tkinter widget

    jsondir, jsonName = os.path.split(fullPath)
    suffix_start = jsonName.find('-kilosort')
    session_id = jsonName[0:suffix_start]
    testLogPath = os.path.join(jsondir, 'testlog.csv')
    writeHeader(testLogPath)

    modules = ['kilosort_helper','kilosort_postprocessing','noise_templates','mean_waveforms','quality_metrics']
    addEntry(modules, jsondir, session_id, testLogPath)


if __name__ == "__main__":
    main()
