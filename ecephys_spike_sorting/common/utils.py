import pandas as pd
import os
import numpy as np
import json
import glob

def get_lfp_band_continuous_file(base_directory):

    f1 = os.path.join(base_directory, os.path.join('continuous','Neuropix*.1'))
    ap_directory = glob.glob(f1)[0]
    return os.path.join(ap_directory, 'continuous.dat')

def get_ap_band_continuous_file(base_directory):
    
    f1 = os.path.join(base_directory, os.path.join('continuous','Neuropix*.0'))
    ap_directory = glob.glob(f1)[0]
    return os.path.join(ap_directory, 'continuous.dat')


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


def read_cluster_group_tsv(filename):

    info = np.genfromtxt(filename, dtype='str')
    cluster_ids = info[1:,0].astype('int')
    cluster_quality = info[1:,1]

    return cluster_ids, cluster_quality

def load(folder, filename):

    return np.load(os.path.join(folder, filename))

def load_kilosort_data(folder, sample_rate, convert_to_seconds = True):

    spike_times = load(folder,'spike_times.npy')
    spike_clusters = load(folder,'spike_clusters.npy')
    amplitudes = load(folder,'amplitudes.npy')
    templates = load(folder,'templates.npy')
    unwhitening_mat = load(folder,'whitening_mat_inv.npy')
    channel_map = load(folder, 'channel_map.npy')
                
    templates = templates[:,21:,:] # remove zeros
    spike_clusters = np.squeeze(spike_clusters) # fix dimensions
    spike_times = np.squeeze(spike_times)# fix dimensions
    if convert_to_seconds:
       spike_times = spike_times / sample_rate # convert to seconds
                    
    unwhitened_temps = np.zeros((templates.shape))
    
    for temp_idx in range(templates.shape[0]):
        
        unwhitened_temps[temp_idx,:,:] = np.dot(np.ascontiguousarray(templates[temp_idx,:,:]),np.ascontiguousarray(unwhitening_mat))
                    
    cluster_ids, cluster_quality = read_cluster_group_tsv(os.path.join(folder, 'cluster_group.tsv'))

    return spike_times, spike_clusters, amplitudes, unwhitened_temps, channel_map, cluster_ids, cluster_quality