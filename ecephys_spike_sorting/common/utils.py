#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 11 17:00:27 2018

@author: joshs
"""

import pandas as pd
import os
import numpy as np
import json

def find_range(x,a,b,option='within'):
    """Find data within range [a,b]"""
    if option=='within':
        return np.where(np.logical_and(x>=a, x<=b))[0]
    elif option=='outside':
        return np.where(np.logical_or(x < a, x > b))[0]
    else:
        raise ValueError('unrecognized option paramter: {}'.format(option))


def rms(data):
    return np.power(np.mean(np.power(data.astype('float32'),2)),0.5)

def write_probe_json(output_file, channels, offset, scaling, mask, surface_chan, air_chan):

    with open(output_file, 'w') as outfile:
        json.dump( \
                  {  \
                        'channel' : channels.tolist(), \
                        'offset' : offset.tolist(), \
                        'scaling' : scaling.tolist(), \
                        'mask' : mask.tolist(), \
                        'surface_channel' : surface_chan, \
                        'air_channel' : air_chan
                   },
                 
                  outfile, \
                  indent = 4, separators = (',', ': ') \
                 ) 

# %%

def read_probe_json(input_file):
    
    with open(input_file) as data_file:
        data = json.load(data_file)

    totalChans = 384
    maxChan = 384
    
    full_mask = np.zeros((totalChans,totalChans))
    full_mask = full_mask > 1
    
    scaling = np.array(data['scaling'])
    mask = np.array(data['mask'])
    offset = np.array(data['offset'])
    surface_channel = data['surface_channel']
    air_channel = data['air_channel']

    period = 24
        
    for ch in range(0,totalChans):
        
        neighbors = np.arange(ch%period, maxChan, period).astype('int') # 1 neighbor is better than 2
        ok_chans = np.setdiff1d(neighbors, np.where(mask == False)[0])
        
        full_mask[ok_chans,ch] = True 

    return mask, offset, scaling, surface_channel, air_channel
