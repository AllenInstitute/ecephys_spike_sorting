from argschema import ArgSchemaParser
import os
import logging

import numpy as np
import matplotlib.pyplot as plt

from ecephys_spike_sorting.common.OEFileInfo import OEContinuousFile

from scipy.signal import welch
from scipy.ndimage.filters import gaussian_filter1d

from _schemas import InputParameters, OutputParameters

def find_range(x,a,b,option='within'):
    """Find data within range [a,b]"""
    if option=='within':
        return np.where(np.logical_and(x>=a, x<=b))[0]
    elif option=='outside':
        return np.where(np.logical_or(x < a, x > b))[0]
    else:
        raise ValueError('unrecognized option paramter: {}'.format(option))

def find_surface_channel(lfp_data, figure_location = None):
    
    # HARD-CODED PARAMETERS:
    nchannels = 384
    sample_frequency = 2500
    smoothing_amount = 5
    power_thresh = 2.0
    diff_thresh = -0.05
    freq_range = [0,10]
    channel_range = [370,380]
    n_passes = 10
    # END HARD-CODED PARAMETERS
    
    candidates = np.zeros((n_passes,))
    
    for p in range(n_passes):
        
        startPt = sample_frequency*100*p
        endPt = startPt + sample_frequency
    
        rawData = np.memmap(lfp_data, dtype='int16', mode='r')
        data = np.reshape(rawData, (int(rawData.size/nchannels), nchannels))
        
        channels = np.arange(nchannels)
        chunk = np.copy(data[startPt:endPt,channels])
        
        for channel in channels:
            chunk[:,channel] = chunk[:,channel] - np.median(chunk[:,channel])
            
        for channel in channels:
            chunk[:,channel] = chunk[:,channel] - np.median(chunk[:,channel_range[0]:channel_range[1]],1)
        
        nfft = 4096
        power = np.zeros((2049, channels.size))
    
        for channel in channels:
            sample_frequencies, Pxx_den = welch(chunk[:,channel], fs=sample_frequency, nfft=nfft)
            power[:,channel] = Pxx_den
        
        in_range = find_range(sample_frequencies, 0, 150)
        
        mask_chans = np.array([37, 76, 113, 152, 189, 228, 265, 304, 341, 380]) - 1
        
        in_range_gamma = find_range(sample_frequencies, freq_range[0],freq_range[1])
        
        values = np.log10(np.mean(power[in_range_gamma,:],0))
        values[mask_chans] = values[mask_chans-1]
        values = gaussian_filter1d(values,smoothing_amount)
                        
        try:
            surface_chan = np.max(np.where((np.diff(values) < diff_thresh) * (values[:-1] < power_thresh) )[0])
        except ValueError:
            surface_chan = 384
            
        candidates[p] = surface_chan
        
        if figure_location is not None:
            plt.figure(figsize=(10,5))
            plt.subplot(4,1,1)
            plt.imshow(np.flipud((chunk).T), aspect='auto',vmin=-1000,vmax=1000)
            
            plt.subplot(4,1,2)
            plt.imshow(np.flipud(np.log10(power[in_range,:]).T), aspect='auto')
            
            plt.subplot(4,1,3)
            plt.plot(values) 
            plt.plot([0,384],[power_thresh,power_thresh],'--k')
  
            plt.plot([surface_chan, surface_chan],[0, 6],'--r')
            
            plt.subplot(4,1,4)
            plt.plot(np.diff(values))
            plt.plot([0,384],[diff_thresh,diff_thresh],'--k')
            
            plt.plot([surface_chan, surface_chan],[-0.2, 0.07],'--r')
            plt.title(surface_chan)
            plt.savefig(figure_location, dpi=300)
            
    surface_channel = np.median(candidates)
    air_channel = np.min([surface_channel + 100, 384])
        
    return surface_channel, air_channel


def run_depth_estimation(args):

    # load lfp band data
    
    lfp_file = args['input_file']
    
    logging.info('Loading ' + lfp_file.filename)
    
    surface_channel, air_channel = find_surface_channel(lfp_file, plot_on = False)
    
    assert(surface_channel > 0)
    assert(air_channel > 0)
        
    return {"surface_channel": surface_channel,
            "air_channel": air_channel} # output manifest

def main():

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = run_depth_estimation(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
