from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
import shutil
import fnmatch

import numpy as np

from ...common.utils import catGT_ex_params_from_str


def call_TPrime(args):

    # Run TPrime on a "standard" multiprobe + NI, using NP 1.0 or 2.0, with run
    # folder and probe folders
    # inputs:
    # full path to Tprime executable
    # parameters for "to stream" extracted edges ("to stream" = the reference stream for the data set)
    # parameters for NI sync edges
    
    # bNPY, if True, no text files of spike times will be written
    bNPY = True;
    if bNPY:
        outSuffix = '.npy'
    else:
        outSuffix = '.txt'

    print('ecephys spike sorting: TPrime helper module')
    start = time.time()
    
    # build paths to the input data for TPrime
    catGT_dest = args['directories']['extracted_data_directory']
    run_name = args['catGT_helper_params']['run_name'] + '_g' + args['catGT_helper_params']['gate_string']
    run_dir_name = 'catgt_' + run_name
    prb_dir_prefix = run_name + '_imec'
    
    run_directory = os.path.join( catGT_dest, run_dir_name ) # extracted edge files for aux data reside in run directory

    # build list of from streams
    #   all streams for which sync edges have been extracted

    toStream_params = args['tPrime_helper_params']['toStream_sync_params']
    ni_sync_params = args['tPrime_helper_params']['ni_sync_params']
    catGTcmd = args['catGT_helper_params']['cmdStr']

    exe_path = os.path.join(args['tPrime_helper_params']['tPrime_path'], 'TPrime.exe')
    sync_period = args['tPrime_helper_params']['sync_period']

    catGTcmd_parts = catGTcmd.split('-')
    # remove empty strings
    catGTcmd_parts = [idx for idx in catGTcmd_parts if len(idx) > 0]
    ni_tag = 'X'
    imec_tag = 'S'
    ni_ex_list = [idx for idx in catGTcmd_parts if idx[0].lower() == ni_tag.lower()]
    im_ex_list = [idx for idx in catGTcmd_parts if idx[0].lower() == imec_tag.lower()]

    toStream_type, toStream_prb, toStream_ex_name = catGT_ex_params_from_str(toStream_params)

    from_list = list()       # list of files of sync edges for streams to translate to reference
    events_list = list()     # list of files of event times to translate to reference
    from_stream_index = list()     # list of indicies matching event files to a from stream
    out_list = list()    # list of paths for output files, one per event file
    
    c_type, c_prb, ni_sync_ex_name = catGT_ex_params_from_str(ni_sync_params)

    if toStream_type == 'SY':
        # toStream is a probe stream  
        # build a path to it
        prb_dir = prb_dir_prefix + str(toStream_prb)
        c_name = run_name + '_tcat.imec' + str(toStream_prb) + '.' + toStream_ex_name + '.txt'
        toStream_path = os.path.join(run_directory, prb_dir, c_name)
        
        # convert events in the toStream to sec; they will not be adjusted
        ks_outdir = 'imec' + str(toStream_prb) + '_ks2'
        st_file = os.path.join(run_directory, prb_dir, ks_outdir, 'spike_times.npy')
        # convert to seconds; if bNPY = True, returned file is an npy file
        # otherwise, text.
        toStream_events_sec = spike_times_npy_to_sec(st_file, 0, bNPY)
        # if data was saved as text, also save as npy
        if not bNPY:
            spike_times_sec_to_npy(toStream_events_sec)

        # remove the toStream the list of im extraction params
        matchI = [i for i, value in enumerate(im_ex_list) if toStream_params in value]
        del im_ex_list[matchI[0]]

        # fromStreams will include all other SY + NI if present

        # loop over SY, add the sync file to the fromList
        # get extraction parameters, build name for output file

        for ex_str in im_ex_list:
            # get params
            c_type, c_prb, c_ex_name = catGT_ex_params_from_str(ex_str)          
            # build file name for this fromStream
            prb_dir = prb_dir_prefix + str(c_prb)
            c_name = run_name + '_tcat.imec' + str(c_prb) + '.' + c_ex_name + '.txt'
            from_list.append(os.path.join(run_directory, prb_dir, c_name))
            c_index = len(from_stream_index)
            # build path to spike times npy file
            ks_outdir = 'imec' + str(c_prb) + '_ks2'
            st_file = os.path.join(run_directory, prb_dir, ks_outdir, 'spike_times.npy')
            st_file_sec = spike_times_npy_to_sec(st_file, 0, bNPY)
            events_list.append(st_file_sec)
            from_stream_index.append(c_index)
            # build path for output spike times text file
            out_name = 'spike_times_sec_adj' + outSuffix
            out_file = os.path.join(run_directory, prb_dir,ks_outdir, out_name)
            out_list.append(out_file)
    
        # get index for sync channel in NI. If none or not found, no ni
        # edge files will be added to events_list
        matchI = [i for i, value in enumerate(ni_ex_list) if ni_sync_params in value]
        
        if len(matchI) == 1:
            # get params
            c_type, c_prb, c_ex_name = catGT_ex_params_from_str(ni_sync_params)
            c_name = run_name + '_tcat.nidq.' + c_ex_name + '.txt'
            from_list.append(os.path.join(run_directory, c_name))
            c_index = len(from_stream_index)
            #remove from list
            del ni_ex_list[matchI[0]]
            # loop over the remaining files of edges extracted from NI,
            # add to events_list and out_file
            for ex_str in ni_ex_list:
                # get params
                c_type, c_prb, c_ex_name = catGT_ex_params_from_str(ex_str) 
                c_name = run_name + '_tcat.nidq.' + c_ex_name + '.txt'
                events_list.append(os.path.join(run_directory, c_name))
                from_stream_index.append(c_index)
                c_output_name = run_name + '_tcat.nidq.' + c_ex_name + '.adj.txt'
                out_file = os.path.join(run_directory, c_output_name)
                out_list.append(out_file) 
        else:
            print('No NI sync channel found')

                
    else:
        # toStream is NI
        # build path to the the sync file
        c_name = run_name + '_tcat.nidq.' + toStream_ex_name + '.txt'
        toStream_path = os.path.join(run_directory, c_name)

        # build list of event files, include: 
        #   all files of spike times, except for those in a to stream
        #   no NI files, because they are already in the "toStream"

        # loop over all SY files
        for ex_str in im_ex_list:
            # get params
            c_type, c_prb, c_ex_name = catGT_ex_params_from_str(ex_str)  
            # build file name for this fromStream
            prb_dir = prb_dir_prefix + str(c_prb)
            c_name = run_name + '_tcat.imec' + str(c_prb) + '.' + c_ex_name + '.txt'
            from_list.append(os.path.join(run_directory, prb_dir, c_name))
            c_index = len(from_stream_index)
            # build path to spike times npy file
            ks_outdir = 'imec' + str(c_prb) + '_ks2'
            st_file = os.path.join(run_directory, prb_dir, ks_outdir, 'spike_times.npy')
            st_file_sec = spike_times_npy_to_sec(st_file, 0, bNPY)
            events_list.append(st_file_sec)
            from_stream_index.append(c_index)
            # build path for output spike times text file
            out_name = 'spike_times_sec_adj' + outSuffix
            out_file = os.path.join(run_directory, prb_dir, ks_outdir, out_name)
            out_list.append(out_file)

    print('toStream:')
    print(toStream_path)
    print('fromStream')
    for fp in from_list:
        print(fp)
    print('event files')
    for i, ep in enumerate(events_list):
        print('index: ' + repr(from_stream_index[i]) + ',' + ep)
    print('output files')
    for op in out_list:
        print(op)

    # Print out paths for help with debugging
    tcmd = exe_path + ' -syncperiod=' + repr(sync_period) + \
        ' -tostream=' + toStream_path

    for i, fp in enumerate(from_list):
        tcmd = tcmd + ' -fromstream=' + repr(i) + ',' + fp

    for i, ep in enumerate(events_list):
        tcmd = tcmd + ' -events=' + repr(from_stream_index[i]) + ',' + ep + ',' + out_list[i]

    # write out batch file to call TPrime
    bat_path = os.path.join(run_directory, run_name + '_TPrime.bat')
    with open(bat_path, 'w') as batfile:
        batfile.write(tcmd)

    # make the TPrime call
    subprocess.call(tcmd)

    # convert output files were text, convert to npy
    if not bNPY:
        for op in out_list:
            spike_times_sec_to_npy(op)

    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time, 2)) + ' seconds')

    return {"execution_time": execution_time}  # output manifest


def call_TPrime_3A(args):

    # call TPrime for 3A data
    # assumes no nidq stream
    # uses full paths rather than building paths
    # inputs:
    # full path to Tprime executable
    # path to "to stream" sync edges ("to stream" = the reference stream for the data set)
    # paths to "from stream" sync edges and text files of events
    
    # bNPY, if True, no text files of spike times will be written
    bNPY = True
    if bNPY:
        outSuffix = '.npy'
    else:
        outSuffix = '.txt'

    print('ecephys spike sorting: TPrime helper module')
    start = time.time()

    # for twStream, get the spike events and convert to seconds
    toStream_path = args['tPrime_helper_params']['toStream_path_3A']
    toStream_parent, toStream_name = os.path.split(toStream_path)

    from_list = args['tPrime_helper_params']['fromStream_list_3A']       # list of files of sync edges for streams to translate to reference
    events_list = list()     # list of files of event times to translate to reference
    from_stream_index = list()     # list of indicies matching event files to a from stream
    out_list = list()    # list of paths for output files, one per event file

    # convert events in the toStream to sec; they will not be adjusted
    # search the directory the edges file to get the ks2 output
    fileList = os.listdir(toStream_parent)

    # get name of ks2 output dir and convert to sec
    ks_outdir = fnmatch.filter(fileList, 'imec_*_ks2')[0]
    st_file = os.path.join(toStream_parent, ks_outdir, 'spike_times.npy')
    toStream_events_sec = spike_times_npy_to_sec(st_file, 0, bNPY)
    # for later data analysis with spike times as sec, also save as npy
    if not bNPY:
        spike_times_sec_to_npy(toStream_events_sec)

    # fromStreams are just the list provided by the caller for these,
    # convert only the spike times. For 3A, other digital channels are copies
    # of those in the toStream

    for fS in from_list:
        fS_parent, fS_name = os.path.split(fS)
        fileList = os.listdir(fS_parent)
        ks_outdir = fnmatch.filter(fileList, 'imec_*_ks2')[0]
        st_file = os.path.join(fS_parent, ks_outdir, 'spike_times.npy')
        st_file_sec = spike_times_npy_to_sec(st_file, 0, bNPY)
        events_list.append(st_file_sec)
        c_index = len(from_stream_index)
        from_stream_index.append(c_index)
        # build path for output spike times text file
        out_name = 'spike_times_sec_adj' + outSuffix
        out_file = os.path.join(fS_parent, ks_outdir, out_name)
        out_list.append(out_file)

    # Print out paths for help with debugging
    print('toStream:')
    print(toStream_path)
    print('fromStream')
    for fp in from_list:
        print(fp)
    print('event files')
    for i, ep in enumerate(events_list):
        print('index: ' + repr(from_stream_index[i]) + ',' + ep)
    print('output files')
    for op in out_list:
        print(op)

    exe_path = os.path.join(args['tPrime_helper_params']['tPrime_path'], 'TPrime.exe')
    sync_period = args['tPrime_helper_params']['sync_period']

    tcmd = exe_path + ' -syncperiod=' + repr(sync_period) + \
        ' -tostream=' + toStream_path

    for i, fp in enumerate(from_list):
        tcmd = tcmd + ' -fromstream=' + repr(i) + ',' + fp

    for i, ep in enumerate(events_list):
        tcmd = tcmd + ' -events=' + repr(from_stream_index[i]) + ',' + ep + ',' + out_list[i]

    # write out batch file to call TPrime
    bat_path = os.path.join(toStream_parent, toStream_name + '_TPrime.bat')
    with open(bat_path, 'w') as batfile:
        batfile.write(tcmd)

    # make the TPrime call
    subprocess.call(tcmd)

    # convert output files to npy
    if not bNPY:
        for op in out_list:
            spike_times_sec_to_npy(op)

    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time, 2)) + ' seconds')

    return {"execution_time": execution_time}  # output manifest


def spike_times_npy_to_sec(sp_fullPath, sample_rate, bNPY):
    # convert spike_times.npy to text of times in sec
    # return path to the new file. Can take sample_rate as a
    # parameter, or set to 0 to read from param file

    # get file name and create path to new file
    sp_path, sp_fileName = os.path.split(sp_fullPath)
    baseName, bExt = os.path.splitext(sp_fileName)
    if bNPY:
        new_fileName = baseName + '_sec.npy'
    else:
        new_fileName = baseName + '_sec.txt'
        
    new_fullPath = os.path.join(sp_path, new_fileName)

    # load spike_times.npy; returns numpy array (Nspike,) as uint64
    spike_times = np.load(sp_fullPath)

    if sample_rate == 0:
        # get sample rate from params.py file, assuming sp_path is a full set
        # of phy output
        with open(os.path.join(sp_path, 'params.py'), 'r') as f:
            currLine = f.readline()
            while currLine != '':  # The EOF char is an empty string
                if 'sample_rate' in currLine:
                    sample_rate = float(currLine.split('=')[1])
                    print(f'sample_rate read from params.py: {sample_rate:.10f}')
                currLine = f.readline()

            if sample_rate == 0:
                print('failed to read in sample rate\n')
                sample_rate = 30000

    spike_times_sec = spike_times/sample_rate   # spike_times_sec dtype = float

    if bNPY:
        # write out npy file
        np.save(new_fullPath, spike_times_sec)
    else:
        # write out single column text file
        nSpike = len(spike_times_sec)
        with open(new_fullPath, 'w') as outfile:
            for i in range(0, nSpike-1):
                outfile.write(f'{spike_times_sec[i]:.6f}\n')
            outfile.write(f'{spike_times_sec[nSpike-1]:.6f}')

    return new_fullPath


def spike_times_sec_to_npy(spa_fullPath):
    # convert a text file of spike times in seconds to an npy file of
    # python floats, with shape (Nspike,)
    # spa => spikes, adjusted

    # get file name and create path to new file
    spa_path, spa_fileName = os.path.split(spa_fullPath)
    baseName, bExt = os.path.splitext(spa_fileName)
    new_fileName = baseName + '.npy'
    new_fullPath = os.path.join(spa_path, new_fileName)

    # count lines in file to size array
    lineCount = 0
    with open(os.path.join(spa_fullPath), 'r') as f:
        for line in f:
            lineCount = lineCount + 1

    times = np.zeros((lineCount,), dtype='float')
    # read in text file, single column of floats
    i = 0
    with open(os.path.join(spa_fullPath), 'r') as f:
        for line in f:
            times[i] = float(line)
            i = i + 1

    np.save(new_fullPath, times)


def main():

    from ._schemas import InputParameters, OutputParameters

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    if mod.args['ephys_params']['probe_type'] == '3A':
        output = call_TPrime_3A(mod.args)
    else:
        output = call_TPrime(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
