# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 16:15:30 2020
ad hoc function to remove waveform_metrics columns from metrics.csv file
to allow rerunning of mean_waveforms module
@author: colonellj
"""

import os
import pandas as pd


def DelColumns(kilosort_output_dir):
    qmetric_file = os.path.join(kilosort_output_dir, 'metrics.csv')
    # If the file exists, load and check for the waveform_metrics columns
    if os.path.exists(qmetric_file):
        qmetrics = pd.read_csv(qmetric_file)
        colList = qmetrics.columns
        nCol = len(colList)
        if nCol > 15:
            # file has extra columns
            # to delete columns beyond index 14, need to get column labels
            # and pass that list to the drop command
            colList = colList[15:]
            qmetrics = qmetrics.drop(colList, axis='columns')
        print("Re-saving new cluster metrics file after deleting columns ...")
        qmetrics.to_csv(qmetric_file)
    return
