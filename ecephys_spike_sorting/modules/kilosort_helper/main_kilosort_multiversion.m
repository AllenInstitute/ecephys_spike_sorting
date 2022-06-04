function main_KS2_KS25( KSver, remDup, finalSplits, labelGood, saveRez )
% paths will get set by the pipeline
% config file created by pipeline and saved in directory with master
% channel map created by pipeline, path specified in config

rP.KSver = KSver;
rP.remDup = remDup;
rP.finalSplits = finalSplits;
rP.labelGood = labelGood;
rP.saveRez = saveRez;

fprintf( 'main_KS2_KS25_KS3 params: \n');
disp(rP)

if ~(strcmp(rP.KSver, '2.5') | strcmp(rP.KSver, '2.0') | strcmp(rP.KSver, '3.0') )
    fprintf('unsupported kilosort version\n');
    return;
end

run('kilosort2_config_file.m')



if strcmp(rP.KSver, '2.5')
    % main parameter changes from Kilosort2 to v2.5
    ops.sig        = 20;  % spatial smoothness constant for registration
    ops.fshigh     = 300; % high-pass more aggresively
    % random number generator is used in datashift and to set order of batches
    % set seed and initialize here.
    iseed = 1;
    rng(iseed);
elseif strcmp(rP.KSver, '3.0')
    % main parameter changes from Kilosort2 to v2.5
    ops.sig        = 20;  % spatial smoothness constant for registration
    ops.fshigh     = 300; % high-pass more aggresively
    % main parameter changes from Kilosort2.5 to v3.0
    % if using KS3, set ops.Th appropriately from the calling program
    % ops.Th       = [9, 9];

end

% find the binary file
rootZ       = ops.rootZ;
ops.fbinary = fullfile(ops.datafile);

% print out ops
ops

% preprocess data to create temp_wh.dat
rez = preprocessDataSub(ops);

if ~strcmp(rP.KSver, '3.0')
    % That is for KS2.0 and KS 2.5
    if strcmp(rP.KSver, '2.5')
        % data registration step
        rez = datashift2(rez, 1); % last input is for shifting data
        % main tracking and template matching algorithm
        rez = learnAndSolve8b(rez, iseed);
    elseif strcmp(KSver, '2.0')
        % time-reordering as a function of drift
        rez = clusterSingleBatches(rez);
        rez = learnAndSolve8b(rez);
    end            
    
    % OPTIONAL: remove double-counted spikes - solves issue in which individual spikes are assigned to multiple templates.
    % See issue 29: https://github.com/MouseLand/Kilosort/issues/29
    if rP.remDup
        rez = remove_ks2_duplicate_spikes(rez);
    end
    
    % final merges
    rez = find_merges(rez, 1);
    
    
    % final splits by SVD
    if rP.finalSplits
        rez = splitAllClusters(rez, 1);
    end
    
    % decide on cutoff
    rez = set_cutoff(rez);
    
    % eliminate widely spread waveforms (likely noise); only implemented in KS2.5 release
    if ( rP.labelGood & strcmp(rP.KSver, '2.5'))
        rez.good = get_good_units(rez);
    end
    
    fprintf('found %d good units \n', sum(rez.good>0))
    
else
    % For KS 3.0
    rez                = datashift2(rez, 1);

    [rez, st3, tF]     = extract_spikes(rez);
    
    rez                = template_learning(rez, tF, st3);

    [rez, st3, tF]     = trackAndSort(rez);

    rez                = final_clustering(rez, tF, st3);
    
    rez                = find_merges(rez, 1);
    
    rezToPhy2(rez, rootZ);
end

% write to Phy
fprintf('Saving results to Phy  \n')
rezToPhy(rez, rootZ);

if rP.saveRez
    %% if you want to save the results to a Matlab file...

    % discard features in final rez file (too slow to save)
    rez.cProj = [];
    rez.cProjPC = [];

    % final time sorting of spikes, for apps that use st3 directly
    [~, isort]   = sortrows(rez.st3);
    rez.st3      = rez.st3(isort, :);

    % Ensure all GPU arrays are transferred to CPU side before saving to .mat
    rez_fields = fieldnames(rez);
    for i = 1:numel(rez_fields)
        field_name = rez_fields{i};
        if(isa(rez.(field_name), 'gpuArray'))
            rez.(field_name) = gather(rez.(field_name));
        end
    end

    % save final results as rez2
    fprintf('Saving final results in rez2  \n')
    fname = fullfile(rootZ, 'rez2.mat');
    save(fname, 'rez', '-v7.3');
end

end