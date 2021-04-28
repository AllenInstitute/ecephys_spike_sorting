import subprocess
import shutil
import os
import time
from pprint import pprint
from collections import namedtuple
import glob
import datetime
import psutil
import logging

npx_paramstup = namedtuple('npx_paramstup',['backup_location','start_module','end_module'])

backup_drive = r'Q:'
default_start = 'copy_raw_data'
default_end = 'copy_processed_data'

network_location = r"\\sd4\SD4.2"

npx_directories = {r'J:\800972939_366122_20181224_probeA':npx_paramstup(backup_drive,default_start,default_end),
                    r'K:\800972939_366122_20181224_probeB':npx_paramstup(backup_drive,default_start,default_end),
                    r'L:\800972939_366122_20181224_probeC':npx_paramstup(backup_drive,default_start,default_end)
                    }


#todo modify so it will check all backup drives?

data_file_params = namedtuple('data_file_params',['relpath','upload','sorting_step'])

def get_path(path):
    try:
        full_path = glob.glob(path)[0]
    except Exception as E:
        full_path = path
    return full_path

def check_data_processing(probe_type, npx_directory, local_sort_dir, raw_backup_1, raw_backup_2, sort_backup_1, sort_backup_2, lims_upload_location, cortex_only=False):
    #npx_dir is directory where raw data lives
    #local_sort dir is where sorted data lives
    #then set all of these up here, if is not none, then compute it for backwards compatibility

    basepath,session = os.path.split(npx_directory)
    probe = session.split("_")[-1]

    original_location, tail = os.path.splitdrive(npx_directory)
    baqckup_location, tail = os.path.splitdrive(raw_backup_1)


    relpaths, data_files = make_files(probe_type)

    backup_temp = os.path.join(baqckup_location, 'temp.txt')
    base_temp = os.path.join(original_location, 'temp.txt')
    try:
        open(backup_temp, 'a').close
    except Exception as E:
        pass
    try:
        open(base_temp, 'a').close
    except Exception as E:
        pass
    try:
        backup_drive_error = os.path.samefile(base_temp, backup_temp)
        if backup_drive_error:
            print('ERROR: the backup drive seems to be the same as the acquisition drive')
    except Exception as E:
        print('catch_specific')
        backup_drive_error = True
        print('ERROR: Backup drive test failed, backup drive could be the same as the acquisition drive')
        #raise(E)

    raw_size_backup = 0

    if os.path.isdir(raw_backup_1):
        #print('The raw data has been backed up for '+probe)
        raw_size_backup = dir_size(raw_backup_1)
    else:
        print('ERROR: Could not find raw data_backup for '+probe+':')

    raw_size = 0
    if os.path.isdir(npx_directory):
        raw_size = dir_size(npx_directory)
        if raw_size == raw_size_backup:
            pass
            #print('the raw data backup matches the acquired data for '+probe)
        else:
            print('ERROR: the raw data backup does not match the acquired data for '+probe)
    else:
        err_str = 'WARNING: could not find the acquired data at '+ str(npx_directory) + ' to compare to backup size'
        #print(err_str)


    missing_files_list = []
    acquisition_size_dict = {}
    backup_size_dict = {}
    network_size_dict = {}
    acquisition_mtime_dict = {}
    backup_mtime_dict = {}
    network_mtime_dict = {}
    for data_file,file_params in data_files.items():
        relpath = relpaths[file_params.relpath]     
        local_path = get_path(os.path.join(local_sort_dir,relpath,data_file))
        found = False
        try:
            acquisition_size_dict[data_file] = os.path.getsize(local_path)
            acquisition_mtime_dict[data_file] = os.path.getmtime(local_path)
            found = True
        except Exception as E:
            pass

        backup_path = get_path(os.path.join(sort_backup_1,relpath,data_file))
        try:
            backup_size_dict[data_file] = os.path.getsize(backup_path)
            backup_mtime_dict[data_file] = os.path.getmtime(backup_path)
            found = True        
        except Exception as E:
            pass

        network_path = get_path(os.path.join(sort_backup_2,relpath,data_file))
        try:
            network_size_dict[data_file] = os.path.getsize(network_path)
            network_mtime_dict[data_file] = os.path.getmtime(network_path)
            found = True
        except Exception as E:
            pass

        if not found:
            #putting this conditional here because sometimes (maybe certin installs? only NP2?) don't overwrite this file but the others do
            if not(data_file =="ap_timestamps.npy"):
                missing_files_list.append(data_file)

    if missing_files_list:
        print('ERROR: Some processing files were not found on any drive for '+probe)
        modules_missing = set()
        for file in missing_files_list:
            module = data_files[file].sorting_step
            modules_missing.add(module)
        print('The missing files are from the following modules:')
        print(modules_missing)
    else:
        pass
        #print('All the processing files were found on either the acquisition drive or the backup drive for '+probe)

    if raw_size_backup or raw_size:
        npx_size = max(raw_size_backup,raw_size)
        key = r"continuous\Neuropix-3a-100.0\continuous.dat"
        try:
            cont_back = backup_size_dict[key]
        except KeyError:
            cont_back = 0
        try:
            cont = acquisition_size_dict[key]
        except KeyError:
            cont = 0
        if cont or cont_back:
            continuous_size = max(cont,cont_back)
            if continuous_size > 1.2*npx_size and continuous_size < 1.3*npx_size:
                pass
                #print('The continuous size seems correct relative to the npx size for '+probe)
            else: print('ERROR: The continuous file seems too large or too small relative to the npx for '+probe)
        else:print('ERROR: unable to find continuous to compare to npx for '+probe)
    else: print('ERROR: Unable to find npx to compare to continuous file for '+probe)

    missing_backup_list = []
    for file in data_files:
        if file not in backup_size_dict:
            if not(file =="ap_timestamps.npy"):
                missing_backup_list.append(file)
    if missing_backup_list:
        print('ERROR: Some files are not backed up for '+probe+':')
        print(missing_backup_list)
    else:
        pass
        #print('all files are backed up locally for '+probe)

    mismatch_size_list = []
    for file in data_files:
        if file in acquisition_size_dict and file in backup_size_dict:
            if not(acquisition_size_dict[file]==backup_size_dict[file]) or not (acquisition_mtime_dict[file]==backup_mtime_dict[file]):
                mismatch_size_list.append(file)
    if mismatch_size_list:
        print('ERROR: Some processing files have different sizes or modification times on the backup drive and acquisition drive for '+probe)
        print(mismatch_size_list)
    else:
        pass
        #print('all files on the backup drive match the size and modification times of those on the acquisition drive for '+probe)

    sucess = False
    if not(missing_files_list) and not(mismatch_size_list) and not(missing_backup_list):
        sucess = True
        if raw_size == raw_size_backup and raw_size>0 and not(cortex_only):
            print("Deleting NPX files from the acquisition drive for ",probe)
            safe_delete_npx(npx_directory, raw_backup_1)
        lims_files = {}
        delete_files = {}
        keep_files = {}
        move_backup_files = {}
        for file,file_params in data_files.items():
            upload = False
            if file_params.upload == True and file in acquisition_size_dict:
                upload = True
                lims_files[file]=file_params
            depth = 'depth' in file_params.sorting_step
            sorting = 'sorting' in file_params.sorting_step
            if not(depth) and not(sorting and upload) and file in acquisition_size_dict:
                delete_files[file]=file_params
            else:
                keep_files[file]=file_params
            if (file_params.sorting_step in {'sorting', 'metrics', 'mean waveforms', 'depth_estimation'}) or (file in {"channel_states.npy", "event_timestamps.npy"}):
                move_backup_files[file] = file_params
        if lims_files and not(cortex_only):
            print("Copying files to the lims upload drive for ",probe)
            for lims_file,lims_file_params in lims_files.items():
                relpath = relpaths[lims_file_params.relpath]
                print('Copying lims_file: '+ str(lims_file))
                #time.sleep(3)
                copy_a_file(local_sort_dir, lims_upload_location, relpath, lims_file)
        #raise(ValueError)
        if delete_files and not(cortex_only):
            print("Deleting files not needed for phy viewing for ",probe)
            for delete_file,delete_file_params in delete_files.items():
                relpath = relpaths[delete_file_params.relpath]
                #could add copy to backup here)
                safe_delete_file(local_sort_dir, sort_backup_1, relpath, delete_file)

        if keep_files:
            print("keeping phy files local but moving to subdir ", probe)
            try:
                for keep_file, keep_file_params in keep_files.items():
                    relpath = relpaths[keep_file_params.relpath]
                    local_path = get_path(os.path.join(local_sort_dir,relpath,keep_file))
                    full_relpath, filename = os.path.split(local_path)
                    #print(local_path)
                    dirpath, dirname = os.path.split(local_sort_dir)
                    if cortex_only:
                        dirname = dirname + '_cortical_sort'
                    #print(dirname)
                    #could add copy to backup here)
                    try:
                        computer, x = os.path.splitdrive(lims_upload_location)
                        #print(computer)
                        computer = r"\\" + computer.split('\\')[2]
                        #print(computer)
                    except Exception as E:
                        computer = ''
                        logging.error('Failed to get lims upload computer, keeping local instead', exc_info=True)
                    new_dir = os.path.join(computer,'d','finalized_sorted_data',dirname, relpath)
                    #print(new_dir)
                    if not(os.path.exists(new_dir)):
                        os.makedirs(new_dir)
                    new_path = os.path.join(new_dir, filename)
                    #print(new_path)
                    copy_not_move = ('probe_depth' in keep_file) or ('probe_info' in keep_file)
                    try:
                        if copy_not_move and cortex_only:
                            shutil.copy2(local_path, new_path)
                        else:
                            shutil.move(local_path, new_path)
                    except Exception as E:
                        logging.error('Failed to move phy file '+keep_file+' to subdir', exc_info=True)
            except Exception as E:
                logging.error('Failed to move phy files to subdir', exc_info=True)

        if move_backup_files and cortex_only:
            print("moving backup of ctx only sort to subdir and deleting the copy on D drive",probe)
            try:
                for move_file, move_file_params in move_backup_files.items():
                    relpath = relpaths[move_file_params.relpath]
                    #could add copy to backup here)
                    no_delete = ('probe_depth' in move_file) or ('probe_info' in move_file) or ('channel_states' in move_file) or ('event_timestamps' in move_file)
                    if not(no_delete):
                        safe_delete_file(local_sort_dir, sort_backup_1, relpath, move_file)
                    #print('RELPATH '+relpath)
                    backup_path = get_path(os.path.join(sort_backup_1, relpath, move_file))
                    #print('backup_path '+backup_path)
                    full_relpath, filename = os.path.split(backup_path)
                    path, dirname = os.path.split(sort_backup_1)
                    new_dirname = 'cortical_sort_'+ dirname
                    new_path = os.path.join(path, new_dirname, relpath, filename)
                    os.makedirs(os.path.split(new_path)[0], exist_ok=True)
                    #print('new_path '+new_path)
                    copy_not_move = ('channel_states' in move_file) or ('event_timestamps' in move_file)
                    if copy_not_move:
                        shutil.copy2(backup_path, new_path)
                    else:
                        shutil.move(backup_path, new_path)
            except Exception as E:
                logging.error('Failed to move cortex only files to subdir', exc_info=True)
            try:
                relpath = 'logs'
                #print('RELPATH '+relpath)
                backup_path = get_path(os.path.join(sort_backup_1, relpath))
                #print('backup_path '+backup_path)
                full_relpath, filename = os.path.split(backup_path)
                path, dirname = os.path.split(sort_backup_1)
                new_dirname = 'cortical_sort_'+ dirname
                new_path = os.path.join(path, new_dirname, relpath)
                os.makedirs(os.path.split(new_path)[0], exist_ok=True)
                #print('new_path '+new_path)
                shutil.move(backup_path, new_path)
            except Exception as E:
                logging.error('Failed to move logs to cortex only subdir', exc_info=True)
        if not(cortex_only):
            #delete the logs
            try:
                print('attempting to delete the logs from the local dir')
                logs_dir = os.path.join(local_sort_dir, 'logs')
                for log_dir in os.listdir(logs_dir):
                    fullpath = os.path.join(logs_dir, log_dir)
                    for file in os.listdir(fullpath):
                        relpath = os.path.join('logs',log_dir )
                        safe_delete_file(local_sort_dir, sort_backup_1, relpath, file)
            except Exception as E:
                logging.error('Failed to delete the log dir', exc_info=True)

            #delete the empty directories 
            try:
                print('attempting to delete the empty directories from the local dir')
                for file in os.listdir(local_sort_dir):
                    fullpath = os.path.join(local_sort_dir, file)
                    if dir_size(fullpath) == 0:
                        shutil.rmtree(fullpath)
                if dir_size(local_sort_dir) == 0:
                    shutil.rmtree(local_sort_dir)
            except Exception as E:
                logging.error('Failed to delete the empty dirs', exc_info=True)

            #delete the extracted dirs
            try:
                print('attempting to delete the extracted dirs from the local drive')
                extracted_path = os.path.join(os.path.split(local_sort_dir)[0], '*extracted')
                for fullpath in glob.glob(extracted_path):
                    if dir_size(fullpath) == 0:
                        shutil.rmtree(fullpath)
            except Exception as E:
                logging.error('Failed to delete the extracted dirs', exc_info=True)


            #sorted_dir = os.path.join(basepath,session+"_sorted")
            #print(sorted_dir)
            #backup_npx_dir = os.path.join(npx_params.backup_location,session+"_sorted")
            #print(backup_npx_dir)
            #for root, dirs, files in os.walk(sorted_dir):
        #       for name in files:
    #               local_path = os.path.join(root,name)
#                   print(local_path)#
#                   backup_path = os.path.join(backup_npx_dir,name)#
                    #print(backup_path)
                    #if os.path.isfile(local_path):
                    #   try:
                    #       if os.path.getsize(local_path)==os.path.getsize(backup_path) and not os.path.samefile(local_path,backup_path):
                    #           os.remove(local_path)
                    #           #print(file +" deleted")
                    #       else:
                    #           print(name +" not deleted, backup error")
                    #   except Exception as E:
                    #       print(name +" not deleted, other error")
                    #       print(E)
                #for dire in dirs:
                #   try:
                #       os.rmdir(os.path.join(root,dire))
                #   except Exception as E:
                #       pass
            try:
                pass
                #shutil.rmtree(os.path.join(local_sort_dir, 'logs'))
            except Exception as E:
                print('Could not delete log folder')
            print('Marking as sucess!')
        else:
            pass
            #print("No files found to delete for day 2 upload")

    extra_files = []        
    for dirpath, dirnames, filenames in os.walk(local_sort_dir):
        for f in filenames:
            if f not in data_files and not(f == 'continuous.dat'):
                extra_files.append(f)
    if extra_files:
        pass
        #print("ERROR: Some extra files were found for ",probe)
        #print(extra_files)
    else:
        pass
        #print("No extra files were found for ", probe)

    net_raw_size_backup = 0
    if os.path.isdir(raw_backup_2):
        net_raw_size_backup = dir_size(raw_backup_2)
        if net_raw_size_backup == raw_size_backup:
            pass
            #print('The raw data is on SD4 and the size matches the backup for '+probe)
        else:
            print("ERROR: The raw data on SD4 is not the same size as the raw data on the backup drive for ", probe)
    else:
        pass
        #print('ERROR: Could not find raw data on SD4 for  for '+probe+':')

    missing_net_backup_list = []
    for file in data_files:
        if file not in network_size_dict:
            missing_net_backup_list.append(file)
    if missing_net_backup_list:
        pass
        #print('ERROR: Some files are not backed up on SD4 for '+probe+':')
        #print(missing_net_backup_list)
    else:
        pass#print('all files are backed up on SD4 for '+probe)

    net_mismatch_size_list = []
    for file in data_files:
        if file in network_size_dict and file in backup_size_dict:
            if not(network_size_dict[file]==backup_size_dict[file]) or not(network_mtime_dict[file]==backup_mtime_dict[file]):
                net_mismatch_size_list.append(file)
    if net_mismatch_size_list:
        print('ERROR: Some processing files have different sizes or modification times on the backup drive and SD4 for '+probe)
        print(net_mismatch_size_list)
    elif not(network_size_dict):
        pass
        #print('WARNING: Could not check file sizes on SD4 since they do not exist')
    else:
        pass
        #print('All files on the backup drive match the size and modification times of those on SD4 for '+probe)
    return sucess, missing_files_list, mismatch_size_list, missing_backup_list

def safe_delete_npx(local_npx_dir, backup_npx_dir):
    for root, dirs, files in os.walk(local_npx_dir):
        for name in files:
            local_path = os.path.join(root,name)
            backup_path = os.path.join(backup_npx_dir,name)
            if os.path.isfile(local_path):
                try:
                    if os.path.getsize(local_path)==os.path.getsize(backup_path) and not os.path.samefile(local_path,backup_path):
                        os.remove(local_path)
                        #print(file +" deleted")
                    else:
                        print(name +" not deleted, backup error")
                except Exception as E:
                    print(name +" not deleted, other error")
                    print(E)
        for dire in dirs:
            try:
                os.rmdir(os.path.join(root,dire))
            except Exception as E:
                pass
    try:
        os.rmdir(local_npx_dir)
    except Exception as E:
        print("WARNING: Raw directory not deleted, probably non-empty")

def safe_delete_file(local_dir, backup_dir, relpath, data_file):
    local_path = get_path(os.path.join(local_dir,relpath,data_file))
    backup_path = get_path(os.path.join(backup_dir,relpath,data_file))
    try:
        if os.path.getsize(local_path)==os.path.getsize(backup_path) and not os.path.samefile(local_path, backup_path):
            os.remove(local_path)       
            #print(data_file + " deleted")
        else: print(data_file + " not deleted, backup error")
    except Exception as E:
        print(data_file + " not deleted, other error")
        print(E)

def copy_a_file(local_dir, lims_upload_location, relpath, data_file):
    local_path = os.path.join(local_dir,relpath)
    session_dir = os.path.split(local_dir)[1]
    print(session_dir)
    lims_upload_path = os.path.join(lims_upload_location, session_dir, relpath)
    full_path = get_path(os.path.join(lims_upload_path, data_file))
    data_file = os.path.split(full_path)[1] #necessary to get the right probe depth filename
    command_string = "robocopy "+ local_path +" "+lims_upload_path +' '+data_file+r" /xc /xn /xo"
    try:
        subprocess.check_call(command_string)
    except Exception as E:
        logging.warning(E, exc_info=True)

def dir_size(dir_path):
      total_size = 0
      for dirpath, dirnames, filenames in os.walk(dir_path):
          for f in filenames:
              fp = os.path.join(dirpath, f)
              fsize = os.path.getsize(fp)
              total_size +=fsize
      return total_size
    

def make_files(probe_type):
    relpaths = {
                    'lfp':r"continuous\Neuropix-{}-100.1".format(probe_type),
                    'spikes':r"continuous\Neuropix-{}-100.0".format(probe_type),
                    'events':r"events\Neuropix-{}-100.0\TTL_1".format(probe_type),
                    'empty':""
                        }
            
    data_files = {
          "probe_info.json":data_file_params('empty',True,'depth_estimation'),
          "channel_states.npy":data_file_params('events',True,'extraction'),
          "event_timestamps.npy":data_file_params('events',True,'extraction'),
          "ap_timestamps.npy":data_file_params('spikes',False,'extraction'),
          #r"continuous\Neuropix-{}-100.1\continuous.dat".format(probe_type):data_file_params('empty',True,'extraction'),
          "continuous.dat":data_file_params('lfp',True,'extraction'),
          "lfp_timestamps.npy":data_file_params('lfp',True,'extraction'),
          "amplitudes.npy":data_file_params('spikes',True,'sorting'),
          "spike_times.npy":data_file_params('spikes',True,'sorting'),
              "mean_waveforms.npy":data_file_params('spikes',True,'mean waveforms'),
              "spike_clusters.npy":data_file_params('spikes',True,'sorting'),
              "spike_templates.npy":data_file_params('spikes',True,'sorting'),
              "templates.npy":data_file_params('spikes',True,'sorting'),
              "whitening_mat.npy":data_file_params('spikes',True,'sorting'),
              "whitening_mat_inv.npy":data_file_params('spikes',True,'sorting'),
              "templates_ind.npy":data_file_params('spikes',True,'sorting'),
              "similar_templates.npy":data_file_params('spikes',True,'sorting'),
              "metrics.csv":data_file_params('spikes',True,'metrics'),
              "waveform_metrics.csv":data_file_params('spikes',False,'metrics'),
              "channel_positions.npy":data_file_params('spikes',True,'sorting'),
              "cluster_group.tsv.v2":data_file_params('spikes',False,'sorting'),
              "cluster_Amplitude.tsv":data_file_params('spikes',False,'sorting'),
              "cluster_ContamPct.tsv":data_file_params('spikes',False,'sorting'),
              "cluster_KSLabel.tsv":data_file_params('spikes',False,'sorting'),
              "channel_map.npy":data_file_params('spikes',True,'sorting'),
              "params.py":data_file_params('spikes',True,'sorting'),
          "probe_depth_*.png":data_file_params("empty",True,'depth_estimation'),
          r"continuous\Neuropix-{}-100.0\continuous.dat".format(probe_type):data_file_params('empty',False,'extraction'),
          "residuals.dat":data_file_params('spikes',False,'median subtraction'),
          "pc_features.npy":data_file_params('spikes',False,'sorting'),
          "template_features.npy":data_file_params('spikes',False,'sorting'),
          "rez2.mat":data_file_params('spikes',False,'sorting'),
          "rez.mat":data_file_params('spikes',False,'sorting'),
          "pc_feature_ind.npy":data_file_params('spikes',False,'sorting'),
          "template_feature_ind.npy":data_file_params('spikes',False,'sorting')
          }
    return relpaths, data_files



def check_all_data(npx_directories):
    success_list = []
    for npx_directory,params in npx_directories.items():
        dir_sucess = check_data_processing(npx_directory, params)
        success_list.append(dir_sucess)
    return all(set(success_list))

def check_all_space(npx_directories):
    space_dict = {}
    for npx_dir in npx_directories:
        #drive, tail = os.path.splitdrive(npx_dir)
        try:
            #print(npx_dir)
            free_space = psutil.disk_usage(npx_dir).free
            if  free_space < (600*(10**9)):
                space_dict[drive] = free_space
        except Exception as E:
            npx_dir = os.path.split(npx_dir)[0]
            #print(npx_dir)
            free_space = psutil.disk_usage(npx_dir).free
            if  free_space < (600*(10**9)):
                space_dict[drive] = free_space
    if space_dict:
        for drive in space_dict.items():
            print("ERROR: Not enough space on ",drive,"for acquisition")
    else: print("There is enough space for acquisition on all drives")

def postprocessing(npx_directories):
    check_all_data(npx_directories)
    generate_batch_file(npx_directories)
    check_all_space(npx_directories)
    return sucess

    

if __name__ == "__main__":
    postprocessing(npx_directories)