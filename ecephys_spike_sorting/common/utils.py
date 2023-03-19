import pandas as pd
import os
import numpy as np
import json
import sys
import time
import pathlib

from git import Repo


def find_range(x,a,b,option='within'):
    
    """
    Find indices of data within or outside range [a,b]

    Inputs:
    -------
    x - numpy.ndarray
        Data to search
    a - float or int
        Minimum value
    b - float or int
        Maximum value
    option - String
        'within' or 'outside'

    Output:
    -------
    inds - numpy.ndarray
        Indices of x that fall within or outside specified range

    """

    if option=='within':
        return np.where(np.logical_and(x>=a, x<=b))[0]
    elif option=='outside':
        return np.where(np.logical_or(x < a, x > b))[0]
    else:
        raise ValueError('unrecognized option paramter: {}'.format(option))


def rms(data):

    """
    Computes root-mean-squared voltage of a signal

    Input:
    -----
    data - numpy.ndarray

    Output:
    ------
    rms_value - float
    
    """

    return np.power(np.mean(np.power(data.astype('float32'),2)),0.5)

def write_probe_json(output_file, surface_channel, air_channel, vertical_pos, horizontal_pos, shank_ind):

    """
    Writes a json file containing information about one Neuropixels probe.

    Inputs:
    -------
    output_file : file path
        Location for writing the json file
    channels : numpy.ndarray (384 x 0)
        Probe channel numbers
    offset : numpy.ndarray (384 x 0)
        Offset of each channel from zero
    scaling : numpy.ndarray (384 x 0)
        Relative noise level on each channel
    mask : numpy.ndarray (384 x 0)
        1 if channel contains valid data, 0 otherwise
    surface_channel : Int
        Index of channel at brain surface
    air_channel : Int
        Index of channel at interface between saline/agar and air
    vertical_pos : numpy.ndarray (384 x 0)
        Distance (in microns) of each channel from the probe tip
    horizontal_pos : numpy.ndarray (384 x 0)
        Distance (in microns) of each channel from the probe edge

    Outputs:
    --------
    output_file.json (written to disk)

    """

    with open(output_file, 'w') as outfile:
        json.dump( 
                  {  
#                        'channel' : channels.tolist(), 
#                        'offset' : offset.tolist(), 
#                        'scaling' : scaling.tolist(), 
#                        'mask' : mask.tolist(), 
                        'surface_y' : surface_channel, 
                        'air_y' : air_channel,
                        'vertical_pos' : vertical_pos.tolist(),
                        'horizontal_pos' : horizontal_pos.tolist(),
                        'shank_index' : shank_ind.tolist()
                   },
                 
                  outfile, 
                  indent = 4, separators = (',', ': ') 
                 ) 

def read_probe_json(input_file):

    """
    Reads a json file containing information about one Neuropixels probe.

    Inputs:
    -------
    input_file : file path
        Location of file to read

    Outputs:
    --------
    mask : numpy.ndarray (384 x 0)
        1 if channel contains valid data, 0 otherwise
    offset : numpy.ndarray (384 x 0)
        Offset of each channel from zero
    scaling : numpy.ndarray (384 x 0)
        Relative noise level on each channel
    surface_channel : Int
        Index of channel at brain surface
    air_channel : Int
        Index of channel at interface between saline/agar and air

    """
    
    with open(input_file) as data_file:
        data = json.load(data_file)
    
    scaling = np.array(data['scaling'])
    mask = np.array(data['mask'])
    offset = np.array(data['offset'])
    surface_channel = data['surface_channel']
    air_channel = data['air_channel']

    return mask, offset, scaling, surface_channel, air_channel


def write_cluster_group_tsv(IDs, quality, output_directory, filename = 'cluster_group.tsv'):

    """
    Writes a tab-separated cluster_group.tsv file

    Inputs:
    -------
    IDs : list
        List of cluster IDs
    quality : list
        Quality ratings for each unit (same size as IDs)
    output_directory : String
        Location to save the file

    Outputs:
    --------
    cluster_group.tsv (written to disk)

    """
       
    df = pd.DataFrame(data={'cluster_id' : IDs, 'group': quality})
    
    print('Saving data...')
    
    df.to_csv(os.path.join(output_directory, filename), sep='\t', index=False)


def read_cluster_group_tsv(filename):

    """
    Reads a tab-separated cluster_group.tsv file from disk

    Inputs:
    -------
    filename : String
        Full path of file

    Outputs:
    --------
    IDs : list
        List of cluster IDs
    quality : list
        Quality ratings for each unit (same size as IDs)

    """

    info = np.genfromtxt(filename, dtype='str')
    cluster_ids = info[1:,0].astype('int')
    cluster_quality = info[1:,1]

    return cluster_ids, cluster_quality

def read_cluster_amplitude_tsv(filename):
    
    """
    Reads a tab-separated cluster_Amplitude.tsv file from disk

    Inputs:
    -------
    filename : String
        Full path of file

    Outputs:
    --------
    amplitudes : array
        array of average cluster amplitudes calculated by KS2

    """
    info = np.genfromtxt(filename, dtype='str')
    # don't return cluster_ids because those are already read in or 
    # derived from the spike_clusters.npy file
    # cluster_ids = info[1:,0].astype('int')
    cluster_amplitude = info[1:,1].astype('float')


    return cluster_amplitude

def load(folder, filename):

    """
    Loads a numpy file from a folder.

    Inputs:
    -------
    folder : String
        Directory containing the file to load
    filename : String
        Name of the numpy file

    Outputs:
    --------
    data : numpy.ndarray
        File contents

    """

    return np.load(os.path.join(folder, filename))


def load_kilosort_data(folder, 
                       sample_rate = None, 
                       convert_to_seconds = True, 
                       use_master_clock = False, 
                       include_pcs = False,
                       template_zero_padding= 21):

    """
    Loads Kilosort output files from a directory

    Inputs:
    -------
    folder : String
        Location of Kilosort output directory
    sample_rate : float (optional)
        AP band sample rate in Hz
    convert_to_seconds : bool (optional)
        Flags whether to return spike times in seconds (requires sample_rate to be set)
    use_master_clock : bool (optional)
        Flags whether to load spike times that have been converted to the master clock timebase
    include_pcs : bool (optional)
        Flags whether to load spike principal components (large file)
    template_zero_padding : int (default = 21)
        Number of zeros added to the beginning of each template

    Outputs:
    --------
    spike_times : numpy.ndarray (N x 0)
        Times for N spikes
    spike_clusters : numpy.ndarray (N x 0)
        Cluster IDs for N spikes
    spike_templates : numpy.ndarray (N x 0)
        Template IDs for N spikes
    amplitudes : numpy.ndarray (N x 0)
        Amplitudes for N spikes
    unwhitened_temps : numpy.ndarray (M x samples x channels) 
        Templates for M units
    channel_map : numpy.ndarray
        Channels from original data file used for sorting
    channel_pos : numpy.ndarray (channels x 2)
        X and Z coordinates for each channel used in the sort
    cluster_ids : Python list
        Cluster IDs for M units
    cluster_quality : Python list
        Quality ratings from cluster_group.tsv file
    cluster_amplitude : Python list
        Average amplitude for each cluster from cluster_Amplitude.tsv file
    pc_features (optinal) : numpy.ndarray (N x channels x num_PCs)
        PC features for each spike
    pc_feature_ind (optional) : numpy.ndarray (M x channels)
        Channels used for PC calculation for each unit
    template_features (optional) : numpy.ndarray (N x number of features)
        projections onto template features for each spike

    """

    if use_master_clock:
        spike_times = load(folder,'spike_times_master_clock.npy')
    else:
        spike_times = load(folder,'spike_times.npy')
        
    spike_clusters = load(folder,'spike_clusters.npy')
    spike_templates = load(folder, 'spike_templates.npy')
    amplitudes = load(folder,'amplitudes.npy')
    templates = load(folder,'templates.npy')
    unwhitening_mat = load(folder,'whitening_mat_inv.npy')
    channel_map = load(folder, 'channel_map.npy')
    channel_pos = load(folder, 'channel_positions.npy')

    if include_pcs:
        pc_features = load(folder, 'pc_features.npy')
        pc_feature_ind = load(folder, 'pc_feature_ind.npy')
        template_features = load(folder, 'template_features.npy') 

                
    templates = templates[:,template_zero_padding:,:] # remove zeros
    spike_clusters = np.squeeze(spike_clusters) # fix dimensions
    spike_times = np.squeeze(spike_times)# fix dimensions

    if convert_to_seconds and sample_rate is not None:
       spike_times = spike_times / sample_rate 
                    
    unwhitened_temps = np.zeros((templates.shape))
    
    for temp_idx in range(templates.shape[0]):
        
        unwhitened_temps[temp_idx,:,:] = np.dot(np.ascontiguousarray(templates[temp_idx,:,:]),np.ascontiguousarray(unwhitening_mat))
                    
    try:
        cluster_ids, cluster_quality = read_cluster_group_tsv(os.path.join(folder, 'cluster_group.tsv'))
    except OSError:
        cluster_ids = np.unique(spike_clusters)
        cluster_quality = ['unsorted'] * cluster_ids.size
        
    cluster_amplitude = read_cluster_amplitude_tsv(os.path.join(folder, 'cluster_Amplitude.tsv'))
    
        
        

    if not include_pcs:
        return spike_times, spike_clusters, spike_templates, amplitudes, unwhitened_temps, \
               channel_map, channel_pos, cluster_ids, cluster_quality, cluster_amplitude
    else:
        return spike_times, spike_clusters, spike_templates, amplitudes, unwhitened_temps, \
               channel_map, channel_pos, cluster_ids, cluster_quality, cluster_amplitude, \
               pc_features, pc_feature_ind, template_features


def get_spike_depths(spike_clusters, unit_template_ids, first_pc_sq, pc_feature_ind, channel_pos):

    """
    Calculates the distance (in microns) of individual spikes from the probe tip

    This implementation is based on Matlab code from github.com/cortex-lab/spikes
    
    Needs to be called for a subset of spikes extracted with the majority template 
    This is true for all spikes in data which has not been curated.
    Manual merges create clusters that derive from multiple templats, but this
    algorthim examines features from a single template -- so we select spikes
    for each cluster that were extracted with the majority template before calling 
    in metrics.py

    Input:
    -----
    spike_clusters : numpy.ndarray (N x 0)
        Cluster IDs for N spikes
    unit_template_ids : numpy.ndearray (Nclusters x 0)
        majority template assignment for each cluster ID
        before any manual curation, unit_template_ids = cluster_ids
    first_pc_sq : numpy.ndarray (N x template channels)
        square of first pc on each site for each spike
    pc_feature_ind  : numpy.ndarray (M x channels)
        Channels used for PC calculation for each unit
    channel_pos : (channels x 2)
        X and Y/depth position of each channel, in um

    Output:
    ------
    spike_depths : numpy.ndarray (N x 0)
        Distance (in microns) from each spike waveform from the probe tip

    """
    
    # Need to make a copy of pc_features (which can be up to 20G for a very long run)
    # to avoid changing the original (python passes by reference)
    # to help with memory use:
    # make copy only of the portion of the pc_features array that is used
    # take the element-wise power in place to avoid making a 2nd copy

    # get values of the 1st pc for each template site for each spike
#    pc_power = np.copy(pc_features[:,0,:])
#
#    # zero out negtaive elements
#    pc_power[pc_power < 0] = 0
#
#    pc_power = pow(pc_power, 2) # element by element square
  
    spike_feat_ind = pc_feature_ind[unit_template_ids[spike_clusters], :]
    spike_feat_ycoord = channel_pos[spike_feat_ind, 1]
    spike_depths = np.sum(spike_feat_ycoord * first_pc_sq, 1) / np.sum(first_pc_sq,1)

    return spike_depths


def get_spike_amplitudes(spike_templates, templates, amplitudes):

    """
    Calculates the amplitude of individual spikes, based on the original template
    plus a scaling factor

    This implementation is based on Matlab code from github.com/cortex-lab/spikes

    Inputs:
    -------
    spike_templates : numpy.ndarray (N x 0)
        Template IDs for N spikes
    templates : numpy.ndarray (M x samples x channels) 
        Unwhitened templates for M units
    amplitudes : numpy.ndarray (N x 0)
        Amplitudes for N spikes

    Outputs:
    --------
    spike_amplitudes : numpy.ndarray (N x 0)
        Amplitudes for N spikes

    """

    template_amplitudes = np.max(np.max(templates,1) - np.min(templates,1),1)

    spike_amplitudes = template_amplitudes[spike_templates] * amplitudes

    return np.squeeze(spike_amplitudes)



def get_repo_commit_date_and_hash(repo_location):

    """
    Finds the date and hash of the latest commit in a git repository

    Input:
    ------
    repo_location - String
        Local directory containing the git repository

    Outputs:
    --------
    commit_date - String
        Date string of the latest commit
    commit_hash - String
        Hash of the latest commit

    """

    if os.path.exists(repo_location):
        try:
            repo = Repo(repo_location)
            headcommit = repo.head.commit
            commit_date = time.strftime("%a, %d %b %Y %H:%M", time.gmtime(headcommit.committed_date))
            commit_hash = headcommit.hexsha
        except:
            commit_date = 'repository not available'
            commit_hash = 'repository not available'
    else:
        print('Invalid path to kilosort.')

    return commit_date, commit_hash


def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 0, length = 40, fill = '▒'):
    
    """
    Call in a loop to create terminal progress bar

    Code from https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

    Inputs:
    -------
    iteration - Int
        Current iteration
    total - Int
        Total iterations
    prefix - Str (optional)
        Prefix string
    suffix - Str (optional)
        Suffix string
    decimals - Int (optional)
        Positive number of decimals in percent complete
    length - Int (optional)
        Character length of bar
    fill - Str (optional)
        Bar fill character

    Outputs:
    --------
    None
    
    """
    
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '░' * (length - filledLength)
    sys.stdout.write('\r%s %s %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()

    if iteration == total: 
        print()
  
def catGT_ex_params_from_str(ex_str):
    # starting from the comma delimeted CatGT string, return extraction
    # parameters.
    # Note that CatGT does  not allow the option string to contain spaces
    # For NI aux channels the file of extracted edges will be named:
    # <run name>_g<gate index>_tcat.nidq.<ex_name_str>.txt
    # for imec SY channels, the file of of extracted edges will be named:
    # <run name>_g<gate index>_tcat.imec<probe index>.txt
    
    # CatGT does not allow any spaces wihtin options, but there can be 
    # spaces between options in the command string, and these are
    # appended to the comma delimited string parsed here. 
    # Remove spaces before parsing
    ex_str = ex_str.replace(' ','') #replace any spare spaces with commas
    
    eq_pos = ex_str.find('=')
    ex_type = ex_str[0:eq_pos]    # stream type (SY, iSY, XD, iXD, i)
    ex_parts = ex_str[eq_pos+1:].split(',')
    
    if 'x' in ex_type:
        # CatGT 3.0 or later
        stream_index = int(ex_parts[0])
        prb_index = int(ex_parts[1])
        if 'd' in ex_type:
            # name string = x(i)d_<word>_<bit>_<pulse length>
            # if the pulse length includes a decimal, reformat
            ex_parts[4] = ex_parts[4].replace('.', 'p')
            # if word = -1, replace with wildcard character
            if ex_parts[2] == '-1':
                ex_parts[2] = '*'
            ex_name_str = ex_type + '_' + ex_parts[2] + '_' + ex_parts[3] + '_' + ex_parts[4]
        else:
            # edges from analog, xa or xia
            # name string = x(i)_word_<pulse_length>
            ex_parts[3] = ex_parts[5].replace('.', 'p')
            ex_name_str = ex_type + '_' + ex_parts[2] + '_' + ex_parts[5]
    else:
        # CatGT 2.5-like
        prb_index = 0      # for NI 
        if ex_type == 'SY' or ex_type == 'iSY':
            # name string = SY_<word>_<bit>_<pulse length>
            # if the pulse length includes a decimal, reformat
            stream_index = 2
            prb_index = int(ex_parts[0])
            ex_parts[3] = ex_parts[3].replace('.', 'p')
            # if word = -1, replace with wildcard character
            if ex_parts[1] == '-1':
                ex_parts[1] = '*'
            ex_name_str = ex_type + '_' + ex_parts[1] + '_' + ex_parts[2] + '_' + ex_parts[3]
        elif ex_type == 'XD' or ex_type == 'iXD':
            # name string = XD_<word>_<bit>_<pulse length>
            # if the pulse length includes a decimal, reformat
            ex_parts[2] = ex_parts[2].replace('.', 'p')
            # if word = -1, replace with wildcard character
            if ex_parts[0] == '-1':
                ex_parts[0] = '*'
            ex_name_str = ex_type + '_' + ex_parts[0] + '_' + ex_parts[1] + '_' + ex_parts[2]
        else:
            # XA or iXA
            # name string = XA_<word>_<pulse length>
            # if the pulse length includes a decimal, reformat
            ex_parts[3] = ex_parts[3].replace('.', 'p')
            ex_name_str = ex_type + '_' + ex_parts[0] + '_' + ex_parts[3]

    return ex_type, stream_index, prb_index, ex_name_str

def getSortResults(output_dir, clu_version):
    # load results from phy for run logging and creation of the table for C_Waves

    cluLabel = np.load(os.path.join(output_dir, 'spike_clusters.npy'))
    spkTemplate = np.load(os.path.join(output_dir,'spike_templates.npy'))
    cluLabel = np.squeeze(cluLabel)
    spkTemplate = np.squeeze(spkTemplate)

    unqLabel, labelCounts = np.unique(cluLabel, return_counts = True)
    nTot = cluLabel.shape[0]
    nLabel = unqLabel.shape[0]
    maxLabel = np.max(unqLabel)

    templates = np.load(os.path.join(output_dir, 'templates.npy'))
    channel_map = np.load(os.path.join(output_dir, 'channel_map.npy'))
    channel_map = np.squeeze(channel_map)
    
    # read in inverse of whitening matrix
    w_inv = np.load((os.path.join(output_dir, 'whitening_mat_inv.npy')))
    nTemplate = templates.shape[0]
    
    # initialize peak_channels array
    peak_channels = np.zeros([nLabel,],'uint32')
    
   
    # After manual splits or merges, some labels will have spikes found with
    # different templats.
    # for each label in the list unqLabel, get the most common template
    # For that template (nt x nchan), multiply the the transpose (nchan x nt) by inverse of 
    # the whitening matrix (nchan x nchan); get max and min along tthe time axis (1)
    # to find the peak channel
    for i in np.arange(0,nLabel):
        curr_spkTemplate = spkTemplate[np.where(cluLabel==unqLabel[i])]
        template_mode = np.argmax(np.bincount(curr_spkTemplate))
        currT = templates[template_mode,:].T
        curr_unwh = np.matmul(w_inv, currT)
        currdiff = np.max(curr_unwh,1) - np.min(curr_unwh,1)
        peak_channels[i] = channel_map[np.argmax(currdiff)]

    clus_Table = np.zeros((maxLabel+1, 2), dtype='uint32')
    clus_Table[unqLabel, 0] = labelCounts
    clus_Table[unqLabel, 1] = peak_channels

    if clu_version == 0:
        np.save(os.path.join(output_dir, 'clus_Table.npy'), clus_Table)
    else:
        clu_Name = 'clus_Table_' + repr(clu_version) + '.npy'
        np.save(os.path.join(output_dir, clu_Name), clus_Table)
 
    return nTemplate, nTot

def getFileVersion(input_filePath):
    
    # arting from the base path name givin in the parameters
    # also return name for next file in series = next_file
    # If no file exists yet, return curr_file = 'none', new_file = input
    
    next_version = 0;
    next_file = input_filePath
    
    if os.path.exists(next_file):
        # loop over up to 20 versions with an added _1, _2 ...etc
        outPath = pathlib.Path(input_filePath).parent
        outName = pathlib.Path(input_filePath).stem
        outExt = pathlib.Path(input_filePath).suffix
        for version_idx in range(1,21):
            nextName = outName + '_' + repr(version_idx) + outExt
            next_file = os.path.join(outPath, nextName)
            if os.path.exists(next_file) is False:
                #break out of loop 
                next_version = version_idx
                break
    

    return next_file, next_version