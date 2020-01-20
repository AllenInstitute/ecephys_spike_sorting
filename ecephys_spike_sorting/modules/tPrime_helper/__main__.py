from argschema import ArgSchemaParser
import os
import logging
import subprocess
import time
import shutil

import numpy as np

from ...common.utils import catGT_ex_params_from_str


def create_TPrime_bat(args):

    # build a .bat file to call TPrime after manual curation
    # inputs:
    # full path to Tprime executable
    # path to "to stream" sync edges ("to stream" = the reference stream for the data set)
    # paths to "from stream" sync edges and text files of events

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
            events_list.append(st_file)
            from_stream_index.append(str(c_index))
            # build path for output spike times npy file
            out_file = os.path.join(run_directory, prb_dir,ks_outdir, 'spike_times_adj.npy')
            out_list.append(out_file)
    
        # get index for sync channel in NI. If none or not found, no ni
        # edge files will be added to events_list
        matchI = [i for i, value in enumerate(ni_ex_list) if ni_sync_params in value]
        
        if len(matchI) == 1:
            # get params
            c_type, c_prb, c_ex_name = catGT_ex_params_from_str(ni_sync_params)
            c_name = run_name + '_tcat.ni.' + c_ex_name + '.txt'
            from_list.append(os.path.join(run_directory, c_name))
            c_index = len(from_stream_index)
            #remove from list
            del ni_ex_list[matchI[0]]
            # loop over the remaining files of edges extracted from NI,
            # add to events_list and out_file
            for ex_str in ni_ex_list:
                # get params
                c_type, c_prb, c_ex_name = catGT_ex_params_from_str(ex_str) 
                c_name = run_name + '_tcat.ni.' + c_ex_name + '.txt'
                events_list.append(os.path.join(run_directory, c_name))
                from_stream_index.append(str(c_index))
                c_output_name = run_name + '_tcat.ni.' + c_ex_name + '.adj.txt'
                out_file = os.path.join(run_directory, c_output_name)
                out_list.append(out_file) 
        else:
            print('No NI sync channel found')

                
    else:
        # toStream is NI
        # build path to the the sync file
        c_name = run_name + '_tcat.ni.' + toStream_ex_name + '.txt'
        toStream_path = os.path.join(run_directory, c_name)
        
        
        
    
    # build list of event files, include:
    #   all edge files extracted from the NI stream except the one specified by ni_sync_params
    #   all files of spike times, except for those in a to stream
    
    print('toStream:')
    print(toStream_path)
    print('fromStream')
    for fp in from_list:
        print(fp)
    print('event files')
    for ep in events_list:
        print(ep)
        
    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time, 2)) + ' seconds')

    return {"execution_time": execution_time}  # output manifest


def main():

    from ._schemas import InputParameters, OutputParameters

    """Main entry point:"""
    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = create_TPrime_bat(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
