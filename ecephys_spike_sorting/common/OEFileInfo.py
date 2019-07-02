import json
import os
import numpy as np

class OEContinuousFile:
    
    """ 
    
    Stores information about an Open Ephys .dat file, including:
    - the number of channels
    - the sample rate
    - the bit volts value for each channel. 

    """
    
    def __init__(self, json_file, file_num = 0):
        
        info = json.load(open(json_file))
        
        if os.path.isabs(json_file):
            basepath = os.path.dirname(json_file)
        else:
            basepath = ""
        
        self.datafile = os.path.join(basepath, 'continuous', info['continuous'][file_num]['folder_name'], 'continuous.dat')
        self.tsfile = os.path.join(basepath, 'continuous', info['continuous'][file_num]['folder_name'], 'timestamps.npy')
        self.num_channels = info['continuous'][file_num]['num_channels']
        self.sample_rate = info['continuous'][file_num]['sample_rate']
        self.bit_volts = [0] * self.num_channels
        
        if info['continuous'][0]['folder_name'].find('3b') > -1:
            self.refs = np.array([191])
        else:
            self.refs = np.array([36, 75, 112, 151, 188, 190, 227, 264, 303, 340, 379])
        
        for i in range(self.num_channels):
            self.bit_volts[i] = info['continuous'][file_num]['channels'][i]['bit_volts']
            
    def check_size(self):
        
        num_bytes = os.path.getsize(self.datafile)
        
        if num_bytes % (self.num_channels * 2) == 0:
            
            return True
        else:
            return False
        
    def load(self):
        
        rawData = np.memmap(self.datafile, dtype='int16', mode='r')
        data = np.reshape(rawData, (int(rawData.size/self.num_channels),self. num_channels)) * self.bit_volts[0]
        
        return data
    


def get_lfp_channel_order():

    """
    Returns the channel ordering for LFP data extracted from NPX files.

    Parameters:
    ----------
    None

    Returns:
    ---------
    channel_order : numpy.ndarray
        Contains the actual channel ordering.
    """

    remapping_pattern = np.array([0, 12, 1, 13, 2, 14, 3, 15, 4, 16, 5, 17, 6, 18, 7, 19, 
          8, 20, 9, 21, 10, 22, 11, 23, 24, 36, 25, 37, 26, 38,
          27, 39, 28, 40, 29, 41, 30, 42, 31, 43, 32, 44, 33, 45, 34, 46, 35, 47])

    channel_order = np.concatenate([remapping_pattern + 48*i for i in range(0,8)])

    return channel_order