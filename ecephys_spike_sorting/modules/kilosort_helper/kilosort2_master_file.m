%paths will be addded to the matlab path using calls in python
%addpath(genpath('Z:\workstation_backup\full_080119\Documents\KS2_current')) % path to kilosort folder
%addpath(genpath('Z:\workstation_backup\full_080119\Documents\npy-matlab-master')) % path to npy-matlab scripts

%path to the config file will also be added to the matlab path using call in python
%pathToYourConfigFile = 'D:\kilosort_datatemp'; % take from Github folder and put it somewhere else (together with the master_file)
clear;  %clear anything in memory
run('kilosort2_config_file.m')

% find the binary file
rootZ       = ops.rootZ
ops.fbinary = fullfile(ops.datafile)

% preprocess data to create temp_wh.dat
rez = preprocessDataSub(ops);

% time-reordering as a function of drift
rez = clusterSingleBatches(rez);
save(fullfile(rootZ, 'rez.mat'), 'rez', '-v7.3');

% main tracking and template matching algorithm
rez = learnAndSolve8b(rez);

% final merges
rez = find_merges(rez, 1);

% sort before running splitAll, for deterministic calculation
[~, isort]   = sort(rez.st3(:,1), 'ascend');
rez.st3      = rez.st3(isort, :);
rez.st2      = rez.st2(isort, :);
rez.cProj    = rez.cProj(isort, :);
rez.cProjPC  = rez.cProjPC(isort, :, :);

% final splits by SVD
rez = splitAllClusters(rez, 1);

% final splits by amplitudes
rez = splitAllClusters(rez, 0);

% decide on cutoff
rez = set_cutoff(rez);

fprintf('found %d good units \n', sum(rez.good>0))

% write to Phy
fprintf('Saving results to Phy  \n')
rezToPhy(rez, rootZ);

%% if you want to save the results to a Matlab file... 

% discard features in final rez file (too slow to save)
rez.cProj = [];
rez.cProjPC = [];

% save final results as rez2
fprintf('Saving final results in rez2  \n')
fname = fullfile(rootZ, 'rez2.mat');
save(fname, 'rez', '-v7.3');