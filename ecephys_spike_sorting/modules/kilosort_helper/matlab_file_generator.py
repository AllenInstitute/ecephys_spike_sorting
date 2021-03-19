import os
        
def create_chanmap(kilosort_location, EndChan, StartChan = 1, probe_type = '3A', Nchannels = 384, MaskChannels = []):
    mask_string = '['
    for channel in MaskChannels:
        mask_string += str(channel+1)
        mask_string += ' '
    mask_string += ']'

    chanmap_string = make_chanmap_string(EndChan, StartChan, Nchannels, probe_type=probe_type, MaskChannels = mask_string)   
    chanmap_path = os.path.join(kilosort_location,'createChannelMapFile.m')    
    with open(chanmap_path,"w+") as f:
        f.write(chanmap_string)

def create_config(kilosort_location,forwardslash_data_file_location, data_file_name, params):
    config_string = make_config_string(forwardslash_data_file_location, data_file_name, params)   
    config_path = os.path.join(kilosort_location,'kilosort_config_file.m')    
    with open(config_path,"w+") as f:
        f.write(config_string)

def create_config2(kilosort_location,forwardslash_output_file_location,forwardslash_input_file_location, ephys_params, params):
    config_string = make_config_string2(forwardslash_output_file_location, forwardslash_input_file_location,ephys_params, params)   
    config_path = os.path.join(kilosort_location,'kilosort2_config_file.m')    
    with open(config_path,"w+") as f:
        f.write(config_string)

def create_config3(kilosort_location,forwardslash_output_file_location,forwardslash_input_file_location, ephys_params, params):
    config_string = make_config_string2(forwardslash_output_file_location, forwardslash_input_file_location,ephys_params, params)   
    config_path = os.path.join(kilosort_location,'kilosort3_config_file.m')    
    with open(config_path,"w+") as f:
        f.write(config_string)

def make_chanmap_string(EndChan = 384, StartChan = 1, Nchannels = 384, probe_type='3A', MaskChannels = '[ ]'):
    chanmap_string = "map = load('neuropixPhase""" + probe_type + "_kilosortChanMap.mat');"

    chanmap_string += """

        chanMap = map.chanMap;
        chanMap0ind = map.chanMap0ind;
        shankInd = map.shankInd;
        xcoords = map.xcoords;
        ycoords = map.ycoords;

        Nchannels = """ + str(Nchannels) + """;
        StartChan = """ + str(StartChan) + """;
        EndChan =   """ + str(EndChan) + """;
        NChannelsInRange = EndChan-(StartChan-1);
        connected = [false(StartChan-1,1);true(NChannelsInRange, 1); false(Nchannels-EndChan, 1)];
        mask_channels = """ + MaskChannels + """;    
        connected(mask_channels) = false;

        save('chanMap.mat', ...
            'chanMap','chanMap0ind','connected','shankInd', 'xcoords', 'ycoords')
         """

    return chanmap_string


def make_config_string2(forwardslash_output_file_location, 
                        forwardslash_input_file_location,
                        ephys_params, 
                        params):

    # these params need to be written first:
    config_string = "ops.rootZ = '" + forwardslash_output_file_location + "';\n"
    config_string += "ops.datafile = '" + forwardslash_input_file_location + "';\n"
    config_string += ("ops.ntbuff = " + str(params['ntbuff']) + ";\n")

    for param in params.keys():
        if param != 'ntbuff':
            config_string += ("ops." + param + " = " + str(params[param]) + ";\n")

    config_string += ("ops.Nchan = " + str(ephys_params['num_channels']) + ";\n")
    config_string += ("ops.NchanTOT = " + str(ephys_params['num_channels']) + ";\n")
    config_string += ("ops.fs = " + str(ephys_params['sample_rate']) + ";\n")

    return config_string 


def make_config_string(forwardslash_data_file_location, data_file_name, Nfilt = 512, Threshold = [4, 10, 10], lam = [5, 20, 20], IntitalizeTh = -4, InitializeNfilt=10000):
    config_string = """createChannelMapFile; 

        ops.GPU                 = 1; % whether to run this code on an Nvidia GPU (much faster, mexGPUall first)     
        ops.parfor              = 0; % whether to use parfor to accelerate some parts of the algorithm      
        ops.verbose             = 1; % whether to print command line progress       
        ops.showfigures         = 1; % whether to plot figures during optimization      
                
        ops.datatype            = 'dat';  % binary ('dat', 'bin') or 'openEphys'
        ops.root                = '"""+forwardslash_data_file_location+"""'; % 'openEphys' only: where raw files are
        ops.fbinary             = fullfile(ops.root, '"""+data_file_name+"""'); % will be created for 'openEphys'       
        ops.fproc               = 'D:/data/kilosort/temp_wh.dat'; % residual from RAM of preprocessed data      
        
        ops.fs                  = 30000;        % sampling rate        (omit if already in chanMap file)
        ops.NchanTOT            = Nchannels;           % total number of channels (omit if already in chanMap file)
        ops.Nchan               = NChannelsToSort;           % number of active channels (omit if already in chanMap file)
        ops.Nfilt               = """+str(params['Nfilt'])+""";           % number of clusters to use (2-4 times more than Nchan, should be a multiple of 32)             
        ops.nNeighPC            = 12; % visualization only (Phy): number of channnels to mask the PCs, leave empty to skip (12)     
        ops.nNeigh              = 16; % visualization only (Phy): number of neighboring templates to retain projections of (16)     
                
        % options for channel whitening     
        ops.whitening           = 'full'; % type of whitening (default 'full', for 'noSpikes' set options for spike detection below)        
        ops.nSkipCov            = 1; % compute whitening matrix from every N-th batch (1)       
        ops.whiteningRange      = 32; % how many channels to whiten together (Inf for whole probe whitening, should be fine if Nchan<=32)       
                
        % define the channel map as a filename (string) or simply an array      
        ops.chanMap             = 'chanMap.mat'; % make this file using createChannelMapFile.m      
        ops.criterionNoiseChannels = 0.2; % fraction of "noise" templates allowed to span all channel groups (see createChannelMapFile for more info).      
        % ops.chanMap = 1:ops.Nchan; % treated as linear probe if a chanMap file        
                
        % other options for controlling the model and optimization      
        ops.Nrank               = 3;    % matrix rank of spike template model (3)       
        ops.nfullpasses         = 6;    % number of complete passes through data during optimization (6)        
        ops.maxFR               = 20000;  % maximum number of spikes to extract per batch (20000)       
        ops.fshigh              = 300;   % frequency for high pass filtering        
        % ops.fslow             = 2000;   % frequency for low pass filtering (optional)
        ops.ntbuff              = 64;    % samples of symmetrical buffer for whitening and spike detection      
        ops.scaleproc           = 200;   % int16 scaling of whitened data       
        ops.NT                  = 32*1024+ ops.ntbuff;% this is the batch size (try decreasing if out of memory)        
        % for GPU should be multiple of 32 + ntbuff     
                
        % the following options can improve/deteriorate results.        
        % when multiple values are provided for an option, the first two are beginning and ending anneal values,        
        % the third is the value used in the final pass.        
        ops.Th               = """+params['Threshold']+""";    % threshold for detecting spikes on template-filtered data ([6 12 12])        
        ops.lam              = """+params['lam']+""";   % large means amplitudes are forced around the mean ([10 30 30])     
        ops.nannealpasses    = 4;            % should be less than nfullpasses (4)      
        ops.momentum         = 1./[20 400];  % start with high momentum and anneal (1./[20 1000])       
        ops.shuffle_clusters = 1;            % allow merges and splits during optimization (1)      
        ops.mergeT           = .01;           % upper threshold for merging (.1)        
        ops.splitT           = .01;           % lower threshold for splitting (.1)      
                
        % options for initializing spikes from data     
        ops.initialize      = 'fromData'; %'fromData' or 'no'       
        ops.spkTh           = """+str(params['IntitalizeTh'])+""";      % spike threshold in standard deviations (4)      
        ops.loc_range       = [3  1];  % ranges to detect peaks; plus/minus in time and channel ([3 1])     
        ops.long_range      = [30  6]; % ranges to detect isolated peaks ([30 6])       
        ops.maskMaxChannels = 5;       % how many channels to mask up/down ([5])        
        ops.crit            = .65;     % upper criterion for discarding spike repeates (0.65)       
        ops.nFiltMax        = """+str(params['InitializeNfilt'])+""";   % maximum "unique" spikes to consider (10000)     
                
        % load predefined principal components (visualization only (Phy): used for features)        
        dd                  = load('PCspikes2.mat'); % you might want to recompute this from your own data      
        ops.wPCA            = dd.Wi(:,1:7);   % PCs         
                
        % options for posthoc merges (under construction)       
        ops.fracse  = 0.1; % binning step along discriminant axis for posthoc merges (in units of sd)       
        ops.epu     = Inf;      
                
        ops.ForceMaxRAMforDat   = 20e9; % maximum RAM the algorithm will try to use; on Windows it will autodetect.
        """
    return config_string

