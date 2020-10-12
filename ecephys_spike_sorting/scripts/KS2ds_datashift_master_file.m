% paths will get set by the pipeline
% config file created by pipeline and saved in directory with master
% channel map created by pipeline, path specified in config

clear;  %clear anything in memory
fprintf( 'running master for datashift KS2\n');

run('kilosort2_config_file.m')

% find the binary file
rootZ       = ops.rootZ
ops.fbinary = fullfile(ops.datafile);

% reset some parameters particular to the datashift algorithm
ops.minfr_goodchannels = 0.0; % do not exclude any channels so that registration works
ops.sig        = 20;  % spatial smoothness constant for registration
ops.fshigh     = 300; % high-pass more aggresively
ops.datashift  = 2;   % whether to shift the data (2 = nonrigid, 1 = rigid)
ops.trackfinal = 0;   % whether to do template tracking at the end
ops.nblocks    = 6;
iseed = 101;
% intialize random number generator, as it will be used in datashift
rng(iseed);

% print out ops 
ops

% preprocess data to create temp_wh.dat
rez = preprocessDataSub(ops);

% NEW STEP TO DO DATA REGISTRATION
rez = datashift2(rez);

% ORDER OF BATCHES IS NOW RANDOM, controlled by random number generator
% use same iseed as for datashift 
                  
% main tracking and template matching algorithm
rez = learnAndSolve8b(rez, iseed);

% final merges
rez = find_merges(rez, 1);

% final splits by SVD
rez = splitAllClusters(rez, 1);

% decide on cutoff
rez = set_cutoff(rez);
rez.good2 = get_good_units(rez);

fprintf('found %d good units \n', sum(rez.good2>0))

% write to Phy
fprintf('Saving results to Phy  \n')
rezToPhy(rez, rootZ);

%% if you want to save the results to a Matlab file...

% discard features in final rez file (too slow to save)
rez.cProj = [];
rez.cProjPC = [];

% final time sorting of spikes, for apps that use st3 directly
[~, isort]   = sortrows(rez.st3);
rez.st3      = rez.st3(isort, :);

% save final results as rez2
fprintf('Saving final results in rez2  \n')
fname = fullfile(rootZ, 'rez2.mat');
save(fname, 'rez', '-v7.3');
