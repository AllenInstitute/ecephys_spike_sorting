from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
import shutil

import numpy as np

import matlab.engine

from pathlib import Path

from scipy.signal import butter, filtfilt, medfilt

from . import matlab_file_generator
from .SGLXMetaToCoords import MetaToCoords
from ...common.utils import read_probe_json, get_repo_commit_date_and_hash, rms, getSortResults

def run_kilosort(args):

    print('ecephys spike sorting: kilosort helper module')

    commit_date, commit_time = get_repo_commit_date_and_hash(args['kilosort_helper_params']['kilosort_repository'])

    input_file = args['ephys_params']['ap_band_file']
    input_file_forward_slash = input_file.replace('\\','/')

    output_dir = args['directories']['kilosort_output_directory']
    output_dir_forward_slash = output_dir.replace('\\','/')
    

    mask = get_noise_channels(args['ephys_params']['ap_band_file'],
                              args['ephys_params']['num_channels'],
                              args['ephys_params']['sample_rate'],
                              args['ephys_params']['bit_volts'])
    
    if args['kilosort_helper_params']['spikeGLX_data']:
       # SpikeGLX data, will build KS chanMap based on the metadata file plus 
       # exclusion of noise channels found in get_noise_channels
       # metadata file must be in the same directory as the ap_band_file
       # resulting chanmap is copied to the matlab home directory, and will 
       # overwrite any existing 'chanMap.mat'
       metaName, binExt = os.path.splitext(args['ephys_params']['ap_band_file'])
       metaFullPath = Path(metaName + '.meta')

       destFullPath = os.path.join(args['kilosort_helper_params']['matlab_home_directory'], 'chanMap.mat')
       MaskChannels = np.where(mask == False)[0]      
       MetaToCoords( metaFullPath=metaFullPath, outType=1, badChan=MaskChannels, destFullPath=destFullPath)
       # end of SpikeGLX block
       
    else:
        # Open Ephys data, specifically finding the tissue surface and creating a chanMap to 
        # exclude those channels. Assumes 3A/NP1.0 site geometry, all sites in bank 0.
        _, offset, scaling, surface_channel, air_channel = read_probe_json(args['common_files']['probe_json'])
        
        mask[args['ephys_params']['reference_channels']] = False
    
        top_channel = np.min([args['ephys_params']['num_channels'], int(surface_channel) + args['kilosort_helper_params']['surface_channel_buffer']])
        
        matlab_file_generator.create_chanmap(args['kilosort_helper_params']['matlab_home_directory'], \
                                            EndChan = top_channel, \
                                            probe_type = args['ephys_params']['probe_type'],
                                            MaskChannels = np.where(mask == False)[0])
        # end of Open Ephys block    
    

# copy the msster fle to the same directory that contains the channel map and config file
    master_fullpath = os.path.join(os.path.join(args['kilosort_helper_params']['master_file_path'],args['kilosort_helper_params']['master_file_name']))
        
    shutil.copyfile(master_fullpath,
            os.path.join(args['kilosort_helper_params']['matlab_home_directory'],args['kilosort_helper_params']['master_file_name']))
    
# will cd to home directory before calling, so call is master_file_name without extension    
    master_call = os.path.splitext(args['kilosort_helper_params']['master_file_name'])[0]
        
    
    if args['kilosort_helper_params']['kilosort_version'] == 1:
    
        matlab_file_generator.create_config(args['kilosort_helper_params']['matlab_home_directory'], 
                                            input_file_forward_slash, 
                                            os.path.basename(args['ephys_params']['ap_band_file']), 
                                            args['kilosort_helper_params']['kilosort_params'])
    
    elif args['kilosort_helper_params']['kilosort_version'] == 2:
    
        matlab_file_generator.create_config2(args['kilosort_helper_params']['matlab_home_directory'], 
                                             output_dir_forward_slash, 
                                             input_file_forward_slash,
                                             args['ephys_params'], 
                                             args['kilosort_helper_params']['kilosort2_params'])
    else:
        print('unknown kilosort version')
        return

    start = time.time()
    
    eng = matlab.engine.start_matlab()
    
#    if ~args['kilosort_helper_params']['spikeGLX_data']:
#        # Create channel map from Open Ephys parameters through a matlab call
#        eng.createChannelMapFile(nargout=0)

# jic -- remove call to config file, should be called from kilsort_master
# jic -- add paths to kilosort repo and matlab home directory
#
#  
    KS_dir = args['kilosort_helper_params']['kilosort_repository'].replace('\\','/')
    NPY_dir = args['kilosort_helper_params']['npy_matlab_repository'].replace('\\','/')
    home_dir = args['kilosort_helper_params']['matlab_home_directory'].replace('\\','/')
    

            
    if args['kilosort_helper_params']['kilosort_version'] == 1:    
        eng.addpath(eng.genpath(KS_dir))
        eng.addpath(eng.genpath(NPY_dir))
        eng.addpath(home_dir)
        eng.kilosort_master_file(nargout=0)
    else:
        eng.addpath(eng.genpath(KS_dir))
        eng.addpath(eng.genpath(NPY_dir))
        eng.addpath(home_dir)
        eng.run(master_call, nargout=0)

    # if the phy output directory is different from the data directory, change
    # the default dat_path in params.py to be the relative path from the phy
    # output to the binary file
    dat_dir, dat_name = os.path.split(input_file)

    fix_phy_params(output_dir, dat_dir, args['ephys_params']['sample_rate'])

    # make a copy of the channel map to the data directory
    # see above: destFullPath specifiee destination for chanMap.mat
    shutil.copy(destFullPath, os.path.join(dat_dir, 'chanMap.mat'))

    if args['kilosort_helper_params']['ks_make_copy']:
        # get the kilsort output directory name
        pPath, phyName = os.path.split(output_dir)
        # build a name for the copy
        copy_dir = os.path.join(pPath, phyName + '_orig')
        # check for whether the directory is already there; if so, delete it
        if os.path.exists(copy_dir):
            shutil.rmtree(copy_dir)
        # make a copy of output_dir
        shutil.copytree(output_dir, copy_dir)

    execution_time = time.time() - start

    print('kilsort run time: ' + str(np.around(execution_time, 2)) + ' seconds')
    print()
    
    # get nTot and nTemplate from phy output; write out table of clusters 
    # which will be used by C_waves

    nTemplate, nTot = getSortResults(output_dir)
    
    return {"execution_time" : execution_time,
            "kilosort_commit_date" : commit_date,
            "kilosort_commit_hash" : commit_time,
            "mask_channels" : np.where(mask == False)[0],
            "nTemplate" : nTemplate,
            "nTot" : nTot } # output manifest

def get_noise_channels(raw_data_file, num_channels, sample_rate, bit_volts, noise_threshold=20):

    noise_delay = 5            #in seconds
    noise_interval = 10         #in seconds
    
    raw_data = np.memmap(raw_data_file, dtype='int16')
    
    num_samples = int(raw_data.size/num_channels)
      
    data = np.reshape(raw_data, (num_samples, num_channels))
   
    start_index = int(noise_delay * sample_rate)
    end_index = int((noise_delay + noise_interval) * sample_rate)
    
    if end_index > num_samples:
        print('noise interval larger than total number of samples')
        end_index = num_samples
    
    b, a = butter(3, [10/(sample_rate/2), 10000/(sample_rate/2)], btype='band')

    D = data[start_index:end_index, :] * bit_volts
    
    D_filt = np.zeros(D.shape)

    for i in range(D.shape[1]):
        D_filt[:,i] = filtfilt(b, a, D[:,i])

    rms_values = np.apply_along_axis(rms, axis=0, arr=D_filt)

    above_median = rms_values - medfilt(rms_values,11)
    
    print('number of noise channels: ' + repr(sum(above_median > noise_threshold)))

    return above_median < noise_threshold

def fix_phy_params(output_dir, dat_path, sample_rate):
    # write a new params.py file with the relative path to the binary file
    # first make a copy of the original
    shutil.copy(os.path.join(output_dir,'params.py'), os.path.join(output_dir,'old_params.py'))
    
    relPath = os.path.relpath(dat_path, output_dir)
    paramLines = list()
    
    with open(os.path.join(output_dir,'old_params.py'), 'r') as f:
        currLine = f.readline()
        
        while currLine != '':  # The EOF char is an empty string
            if 'dat_path' in currLine:
                dat_path = currLine.split()[2]
                lp = int(len(dat_path))
                dat_path = dat_path[1:lp-1]     #trim off quotes
                new_path = os.path.join(relPath,dat_path)
                new_path = new_path.replace('\\','/')
                currLine = "dat_path = '" + new_path + "'\n"
            elif 'sample_rate' in currLine:
                currLine = (f'sample_rate = {sample_rate:.12f}\n')
            paramLines.append(currLine)           
            currLine = f.readline()
            
    with open(os.path.join(output_dir,'params.py'), 'w') as fout:
        for line in paramLines:
            fout.write(line)

def main():

    from ._schemas import InputParameters, OutputParameters

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = run_kilosort(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
