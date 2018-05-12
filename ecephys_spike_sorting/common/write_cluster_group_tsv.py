#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 11 17:00:27 2018

@author: joshs
"""

import pandas as pd
import os

def write_cluster_group_tsv(IDs, quality, output_directory):

    cluster_quality = []
    cluster_index = []
    
    for idx, ID in enumerate(IDs):
        
        cluster_index.append(ID)
        
        if quality[idx] == 0:
            cluster_quality.append('unsorted')
        elif quality[idx] == 1:
            cluster_quality.append('good')
        else:
            cluster_quality.append('noise')
       
    df = pd.DataFrame(data={'cluster_id' : cluster_index, 'group': cluster_quality})
    
    print('Saving data...')
    
    df.to_csv(os.path.join(output_directory, 'cluster_group.tsv'), sep='\t', index=False)