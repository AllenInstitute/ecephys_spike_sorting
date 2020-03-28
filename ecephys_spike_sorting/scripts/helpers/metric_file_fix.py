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
            # when resaving, eliminate the unnamed column 0
            # to delete columns beyond index 14, need to get column labels
            # and pass that list to the drop command
            dropList = colList[15:]
            qmetrics = qmetrics.drop(dropList, axis='columns')
            dropList = colList[0]
            qmetrics = qmetrics.drop(dropList, axis='columns')

            # rename the epoch_name column label, which will have _quality_metrics appended
            colList = qmetrics.columns
            ec = [col for col in colList if 'epoch_name_quality_metrics' in col]
            if len(ec) > 0:
                print('renaming column')
                qmetrics = qmetrics.rename(columns={'epoch_name_quality_metrics':'epoch_name'})

            print("Re-saving new cluster metrics file after deleting columns ...")
            qmetrics.to_csv(qmetric_file)
    return
