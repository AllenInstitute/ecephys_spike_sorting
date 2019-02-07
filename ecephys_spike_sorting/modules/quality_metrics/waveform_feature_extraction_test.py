# -*- coding: utf-8 -*-
"""
Created on Tue Feb 5 15:05:21 2019

@author: Xiaoxuan Jia
"""
# example code to extract waveform features with library waveform_feature_extraction.py


import numpy as np
import pandas as pd
import ecephys_spike_sorting.modules.quality_metrics.waveform_feature_extraction as wf

def get_waveforms(input_waveforms, peak_ch):
    waveforms=[]
    waveforms_2D=[]
    for index in range(input_waveforms.shape[0]):
        tmp = input_waveforms[index,:,:]
        #peak_ch = int(get_peak_ch(tmp))
        #print(peak_ch)
        if peak_ch>15:
            tmp=tmp[:,peak_ch-15:peak_ch+15]
            waveforms.append(tmp[:60,15])
            waveforms_2D.append(tmp[:60, 0::2].T)
    waveforms=np.array(waveforms)
    waveforms_2D=np.array(waveforms_2D)
    return waveforms, waveforms_2D


def test(w, peak_ch):
	"""
	W is waveforms of unit id(spike id)*time(82)*channels(384)
	"""
	waveforms, waveforms_2D = get_waveforms(w, peak_ch)

	duration, PTratio, repolarizationslop, recoveryslop = wf.get_1d_features(np.array(waveforms))
	Spread, Amplitude, Velo = wf.get_2d_features(np.rollaxis(waveforms_2D, 2,1), site_range=7, plot=False)
