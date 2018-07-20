
addpath(genpath('C:\Users\svc_neuropix\Documents\GitHub\kilosort2')) % path to kilosort folder
addpath(genpath('C:\Users\svc_neuropix\Documents\GitHub\npy-matlab')) % path to npy-matlab scripts

pathToYourConfigFile = 'C:\Users\svc_neuropix\Documents\MATLAB'; % take from Github folder and put it somewhere else (together with the master_file)
run(fullfile(pathToYourConfigFile, 'kilosort2_config_file.m'))

%%

% preprocess data to create temp_wh.dat
rez = preprocessDataSub(ops);

% pre-clustering to re-order batches by depth
fname = fullfile(ops.rootZ, 'rez.mat');    
if exist(fname, 'file')
    % just load the file if we already did this
    dr = load(fname);
    rez.iorig = dr.rez.iorig;
    rez.ccb = dr.rez.ccb;
    rez.ccbsort = dr.rez.ccbsort;
else
    rez = clusterSingleBatches(rez);
    save(fname, 'rez', '-v7.3');
end

%%
% main optimization
rez = learnAndSolve8b(rez);

% final splits
rez = splitAllClusters(rez);

%%
% this saves to Phy
rezToPhy(rez, ops.rootZ);

% discard features in final rez file (too slow to save)
rez.cProj = [];
rez.cProjPC = [];

% save final results as rez2 
fname = fullfile(ops.rootZ, 'rez2.mat');
save(fname, 'rez', '-v7.3');