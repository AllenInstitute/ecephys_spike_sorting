#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

#from qtmodern import styles, windows
#from qtpy import QtGui, QtCore
#from qtpy.QtWidgets import *

import subprocess
import glob
import shutil
import os
import time
import psutil
from collections import namedtuple, OrderedDict
from pprint import pprint
from recordclass import recordclass
import datetime
import logging
#from qtpy import QtGui, QtCore
import multiprocessing
import json
import xml.etree.ElementTree as ET
import pandas as pd

logging.basicConfig(level = logging.INFO)


from helpers.check_data_processing import check_data_processing, check_all_space
#import helpers.processing as npxprocess
from create_input_json import createInputJson
from zro import RemoteObject, Proxy

session = '1046166369_527294_20200826'
probes_in = ['A', 'B', 'C', 'D', 'E', 'F']
probe_type = 'PXI'
class processing_session():

    def __init__(self, session_name, probes_in, probe_type = 'PXI', WSE_computer=None):
        self.session_name = session_name
        self.probe_type = probe_type
        self.WSE_computer = WSE_computer
        ### Put read config here??
        probe_params = namedtuple('probe_params',['probe_letter', 'pxi_slot', 'num_in_slot', 'session','start_module','end_module','backup1','backup2'])
        slot_params = namedtuple('slot_params',['slot_num', 'recording_dir', 'extracted_drive','backup1','backup2'])

        #self.phy_viewing_drive = 'A:' #(change this to an additional 1tb SSD when you have time and backups are taken care of)
        self.lims_upload_drive = r"\\W10dt05515\E" #Change to a Sata drive that we don't plan to remove so it stays shared. 

        default_backup1 = os.path.join(r'\\10.128.50.43\sd6.3', session_name)
        default_backup2 = os.path.join(r'\\10.128.50.43\sd6.3', session_name)
        default_start = 'extract_from_npx'
        default_end = 'cleanup'
        self.json_directory = r'C:\Users\svc_neuropix\Documents\json_files'


        session_name2 = "1046581736_527294_20200827"
        default_backup1_2 = os.path.join(r'\\10.128.50.43\sd6.3', session_name2)
        default_backup2_2 = os.path.join(r'\\10.128.50.43\sd6.3', session_name2)
        default_start_2 = 'extract_from_npx'

        session_name3 = '1028043324_498757_20200604'
        default_backup1_3 = r"I:"
        default_backup2_3 = os.path.join(r'\\10.128.50.43\sd6', session_name3)
        default_start_3 = 'kilosort_helper'
        default_end_3 = 'cleanup'

        pxi_slots = OrderedDict()
        pxi_slots['2a'] = slot_params(2, os.path.join(r'\\10.128.50.43\sd6.3', session_name2, session_name2+'_probeABC'), 'D:', default_backup1_2, default_backup2_2)
        pxi_slots['3a'] = slot_params(3, os.path.join(r'\\10.128.50.43\sd6.3', session_name2, session_name2+'_probeDEF'), 'D:', default_backup1_2, default_backup2_2)
        #pxi_slots['2b'] = slot_params(2, os.path.join('S:', session_name3+'_probeABC'), 'E:', default_backup1_3, default_backup2_3)#os.path.join(r'\\sd5\sd5.2', session_name2), os.path.join(r'\\sd5\sd5.2', session_name2))#T
        #pxi_slots['3b'] = slot_params(3, os.path.join('S:', session_name3+'_probeABC'), 'J:', default_backup1_3, default_backup2_3)#os.path.join(r'\\sd5\sd5.2', session_name2), os.path.join(r'\\sd5\sd5.2', session_name2))#T


        pxi_slots['2'] = slot_params(2, os.path.join(r'\\10.128.50.43\sd6.3', session_name, session_name+'_probeABC'), 'D:', default_backup1, default_backup2)#S
        pxi_slots['3'] = slot_params(3, os.path.join(r'\\10.128.50.43\sd6.3', session_name, session_name+'_probeDEF'), 'D:', default_backup1, default_backup2)#os.path.join(r'\\sd5\sd5.2', session_name2), os.path.join(r'\\sd5\sd5.2', session_name2))#T
        #pxi_slots['2'] = slot_params(2, os.path.join(r'\\sd5\sd5.3\914313377_468996_20190730'), 'E:', r'\\sd5\sd5.3\914313377_468996_20190730', r'\\sd5\sd5.3\914313377_468996_20190730')#S
        #pxi_slots['3'] = slot_params(3, os.path.join(r'\\sd5\sd5.3\914313377_468996_20190730'), 'F:', r'\\sd5\sd5.3\914313377_468996_20190730', r'\\sd5\sd5.3\914313377_468996_20190730')#os.path.join(r'\\sd5\sd5.2', session_name2), os.path.join(r'\\sd5\sd5.2', session_name2))#T
        self.pxi_slots = pxi_slots

        #Whether to verify that the backup exists before starting extraction
        self.skip_verify_backup = True


        probes = OrderedDict()

        if 'A' in probes_in:
            probes['probeA']=probe_params('A', '2', '1', session_name, default_start, default_end, default_backup1, default_backup2)
        if 'B' in probes_in:
            probes['probeB']=probe_params('B', '2', '2',  session_name, default_start, default_end, default_backup1, default_backup2)
        if 'C' in probes_in:
            probes['probeC']=probe_params('C', '2', '3',  session_name, default_start, default_end, default_backup1, default_backup2)
        #if 'D' in probes_in:
        #    probes['probeD']=probe_params('D', '3', '1',  session_name, default_start, default_end, default_backup1, default_backup2)
        #if 'E' in probes_in:
        #    probes['probeE']=probe_params('E', '3', '2',  session_name, default_start, default_end, default_backup1, default_backup2)
        #if 'F' in probes_in:
        #    probes['probeF']=probe_params('F', '3', '3',  session_name, default_start, default_end, default_backup1, default_backup2)


        #probes['probeA2']=probe_params('A', '2a', '1', session_name2, default_start_2, default_end, default_backup1_2, default_backup2_2)
        probes['probeB2']=probe_params('B', '2a', '2',  session_name2, default_start_2, default_end, default_backup1_2, default_backup2_2)
        #probes['probeC2']=probe_params('C', '2a', '3',  session_name2, default_start_2, default_end, default_backup1_2, default_backup2_2)
        #probes['probeD2']=probe_params('D', '3a', '1',  session_name2, 'cleanup', default_end, default_backup1_2, default_backup2_2)
        #probes['probeE2']=probe_params('E', '3a', '2',  session_name2, default_start_2, default_end, default_backup1_2, default_backup2_2)
        probes['probeF2']=probe_params('F', '3a', '3',  session_name2, default_start_2, default_end, default_backup1_2, default_backup2_2)

        
#       probes['probeA3']=probe_params('A', '2b', '1', session_name3, default_start_3, default_end_3, default_backup1_3, default_backup2_3)
#       probes['probeB3']=probe_params('B', '2b', '2',  session_name3, default_start_3, default_end_3, default_backup1_3, default_backup2_3)
#        probes['probeF3']=probe_params('F', '3b', '3',  session_name3, default_start_3, default_end_3, default_backup1_3, default_backup2_3)


        self.probes = probes

        self.modules = [
           #'primary_backup_raw_data1',
           'extract_from_npx',
           'restructure_directories',
           'depth_estimation',
           'edit_probe_json',
           'median_subtraction',
           'kilosort_helper',
           'noise_templates',
           'mean_waveforms',
           'quality_metrics',
           'add_noise_class_to_metrics',
           'final_copy_parallel',
           #'primary_backup_raw_data1',#combine these into one module - or allow it to kick off multiple processes without waiting?
           #'primary_backup_processed_data',#combine these into one module - or allow it to kick off multiple processes without waiting?
           #'secondary_backup_processed_data',#combine these into one module - or allow it to kick off multiple processes without waiting?
           #'secondary_backup_raw_data',#combine these into one module - or allow it to kick off multiple processes without waiting? is it really that simple?
           'copy_logs',           
           'cleanup'
           #'primary_processed_lims_only',
           #'move_processed_for_phy',
        ]

        self.copy_while_waiting_modules = [
            #'copy_while_waiting_primary_processed', # need to name these differently because both may be run
            #'secondary_backup_raw_data', #these can be the same as the main modules because only needs to run once - slot module prevents from running again
            #'primary_backup_raw_data1',
            #'copy_while_waiting_secondary_processed'
        ]

        self.final_copy_all_parallel = [
           'primary_backup_raw_data1',
           #'primary_backup_processed_data',
           'secondary_backup_raw_data',
           'secondary_backup_processed_data'
        ]


        self.no_process_modules = [
            'edit_probe_json',
            'restructure_directories',
            'add_noise_class_to_metrics',
            'copy_logs',
            'cleanup'
        ]

        self.copy_modules = {
            'copy_logs',
            'primary_backup_raw_data1',
            'primary_backup_raw_data2',
            'primary_backup_processed_data',
            'secondary_backup_raw_data',
            'secondary_backup_processed_data',                          
        }.union(set(self.copy_while_waiting_modules)).union(set(self.final_copy_all_parallel))


        self.slot_modules = {
            'primary_backup_raw_data1':{},
            'extract_from_npx':{},
            'primary_backup_raw_data2':{},
            'secondary_backup_raw_data':{},
            'copy_while_waiting_secondary_raw':{},
            'copy_while_waiting_primary_raw':{},
            'parallel_secondary_backup_raw_data':{},
            'parallel_primary_backup_raw_data':{}               
        }   

        self.network_modules = {
            'copy_while_waiting_secondary_raw',
            'copy_while_waiting_secondary_processed',          
            'secondary_backup_raw_data',
            'secondary_backup_processed_data'
        }

        self.backup_modules = {
            'primary_backup_raw_data1',
            'primary_backup_raw_data2',
            'primary_backup_processed_data',
            'copy_while_waiting_primary_raw',
            'copy_while_waiting_primary_processed'
            }   

        self.process_dict = {}
        self.warning_dict = {}
        self.logger_dict = {}
        self.success_list = []
        self.finished_list = [0]*len(self.probes)
        self.current_modules = [False]*len(self.probes)
        self.copy_while_waiting = [False]*len(self.probes)
        self.info_dict = {}
        self.failed_dict = {}
        self.last_output_dict = {}
        self.module_info = recordclass('module_info', ['rcode', 'output', 'error','starttime','endtime', 'processtime' ])


        for probe in self.probes:
            #full_session_id = os.path.basename(probe)
            #limsID = full_session_id.split('_')[0]
            #probe = full_session_id.split('_')[-1]
            self.logger_dict[probe] = self.create_logger(probe)
            self.info_dict[probe] = {}
            self.last_output_dict[probe] = {}
            self.last_output_dict[probe]['last_log_time'] = datetime.datetime.now()
            self.last_output_dict[probe]['last_log'] = ['None']
            self.failed_dict[probe] = 0
            self.process_dict[probe] = {}

        for pxi_slot in self.pxi_slots:
            for module in self.slot_modules:
                self.slot_modules[module][pxi_slot] = 'Ready'

        self.start = datetime.datetime.now()    

    def create_file_handler(self, level_string,level_idx,limsID,probe):
        file_name = limsID+'_'+datetime.datetime.now().strftime("%y.%m.%d.%I.%M.%S")+'_'+level_string+'_'+probe+".log"
        log_file = os.path.join(self.json_directory,file_name)
        file_handler = logging.FileHandler(log_file)

        file_handler.setLevel(level_idx)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        return file_handler

    def session_id(self, probe):
        full_session_id = self.probes[probe].session
        return full_session_id

    def lims_ID(self, probe):
        full_session_id = self.session_id(probe)
        lims_id = full_session_id.split('_')[0]
        return lims_id

    def create_logger(self, probe):
        limsID = self.lims_ID(probe)
        name_string = '_'.join([limsID, probe])
        mylogger = logging.getLogger(name_string)
        error_file_handler = self.create_file_handler('error',logging.WARNING,limsID,probe)
        info_file_handler = self.create_file_handler('info',logging.DEBUG,limsID,probe)
        mylogger.addHandler(error_file_handler)
        mylogger.addHandler(info_file_handler)
        #stream_handler = logging.StreamHandler()
        #stream_handler.setLevel(logging.INFO)
        #mylogger.addHandler(stream_handler)
        return mylogger

#For testing session_name = 'data_test'
    def start_processing(self):
        #session_name = '834008253_433874_20190307'
        print('checking readiness for processing')
        try:
            #time.sleep(60*60*36)
            self.check_ready_for_processing()
            print('Started processing')
            #p = multiprocessing.Process(target=self.process_npx, args=('x',))
            
            #p.start()
            self.process_npx('x')
            started_processing = True
        except Exception as E:
            logging.exception('Failed to start processing')
            started_processing = False
        print('finished initiating processing')
        return started_processing

    def slot(self, probe):
        return self.probes[probe].pxi_slot

    def slot_num(self, slot_or_probe):
        def slot_num_s(self, pxi_slot):
            slot_num = self.pxi_slots[pxi_slot].slot_num
            return slot_num
        try:
            slot_num = slot_num_s(self, slot_or_probe)
        except KeyError as E:
            slot = self.slot(slot_or_probe)
            slot_num = slot_num_s(self, slot)
        return slot_num

    def probe_letter(self, probe):
        return self.probes[probe].probe_letter

    def raw_path(self, slot_or_probe):
        def path_s(self, pxi_slot):
            dirpath = self.pxi_slots[pxi_slot].recording_dir
            return dirpath
        try:
            dirpath = path_s(self, slot_or_probe)
        except KeyError as E:
            pxi_slot = self.slot(slot_or_probe)
            dirpath = path_s(self, pxi_slot)
        return dirpath

    def settings_path(self, slot_or_probe):
        raw_path = self.raw_path(slot_or_probe)
        possible_path = os.path.join(raw_path, 'settings*.xml')
        path = glob.glob(possible_path)[0]
        return path

    def raw_dirname(self, slot_or_probe):
        path = self.raw_path(slot_or_probe)
        head, dirname = os.path.split(path)
        return dirname
        
    def sorted_dirname(self, probe):
        dirname_parts = self.raw_dirname(probe).split('_')
        session_name = ('_').join(dirname_parts[0:3])
        dirname = session_name+'_probe'+self.probe_letter(probe)+'_'+'sorted'
        return dirname

    def sorted_drive(self, slot_or_probe):
        def ex_drive_s(self, slot):
            drive = self.pxi_slots[slot].extracted_drive
            return drive
        try:
            drive = ex_drive_s(self, slot_or_probe)
        except KeyError as E:
            pxi_slot = self.slot(slot_or_probe)
            drive = ex_drive_s(self, pxi_slot)
        return drive 

    def sorted_path(self, probe):
        path = os.path.join(self.sorted_drive(probe), self.sorted_dirname(probe))
        return path

    def sorted_AP_path(self, probe):
        path = os.path.join(self.sorted_path(probe), 'continuous', 'Neuropix-'+self.probe_type+'-100.0')
        return path

    def sorted_LFP_path(self, probe):
        path = os.path.join(self.sorted_path(probe), 'continuous', 'Neuropix-'+self.probe_type+'-100.1')
        return path

    def sorted_events_path(self, probe):
        path = os.path.join(self.sorted_path(probe), 'events', 'Neuropix-'+self.probe_type+'-100.0')
        return path

    def extracted_path_head(self, probe):
        #we can make this whatever we want and pass it into the crate input_json
        slot_p = self.slot(probe)
        probe_list = self.probes_per_slot()[slot_p]
        dirname = self.raw_dirname(probe)+'_extracted'#+'_probe'+('').join(probe_list)
        path = os.path.join(self.sorted_drive(probe), dirname)
        return path

    def port(self, probe):
        return self.probes[probe].num_in_slot

    def dir_string(self, probe):
        num_in_slot = self.port(probe)
        string = 'Neuropix-'+self.probe_type+'-slot'+str(self.slot_num(probe))+'-probe'+num_in_slot
        return string

    def extracted_AP_path(self, probe):
        dirname = self.dir_string(probe)+'-AP'
        path = os.path.join(self.extracted_path_head(probe), 'continuous', dirname)
        return path

    def extracted_LFP_path(self, probe):
        dirname = self.dir_string(probe)+'-LFP'
        path = os.path.join(self.extracted_path_head(probe), 'continuous', dirname)
        return path

    def extracted_events_path(self, probe):
        dirname = self.dir_string(probe)
        path = os.path.join(self.extracted_path_head(probe), 'events', dirname)
        return path 

    def sorted_backup1(self, probe):
        drive = self.probes[probe].backup1
        path = os.path.join(drive, self.sorted_dirname(probe))
        return path

    def sorted_backup2(self, probe):
        drive = self.probes[probe].backup2
        path = os.path.join(drive, self.sorted_dirname(probe))
        return path

    def raw_backup1(self, slot_or_probe):
        dirname = self.raw_dirname(slot_or_probe)
        def backup1_s(self, pxi_slot):
            return self.pxi_slots[pxi_slot].backup1
        try:
            path = os.path.join(backup1_s(self, slot_or_probe), dirname)
        except KeyError as E:
            pxi_slot = self.slot(slot_or_probe)
            path = os.path.join(backup1_s(self, pxi_slot), dirname)
        return path

    def raw_backup2(self, slot_or_probe):
        dirname = self.raw_dirname(slot_or_probe)
        def backup2_s(self, pxi_slot):
            return self.pxi_slots[pxi_slot].backup2
        try:
            path = os.path.join(backup2_s(self, slot_or_probe), dirname)
        except KeyError as E:
            pxi_slot = self.slot(slot_or_probe)
            path = os.path.join(backup2_s(self, pxi_slot), dirname)
        return path

    def probe_letter(self, probe):
        return self.probes[probe].probe_letter

    def probes_per_slot(self):
        probes_per_slot = {}
        for probe, params in self.probes.items():
            try:
                probes_per_slot[params.pxi_slot].append(self.probe_letter(probe))
            except KeyError as E:
                probes_per_slot[params.pxi_slot] = [self.probe_letter(probe)]
        return probes_per_slot

    def probes_sharing_slot(self, slot):
        probes_sharing = len(self.probes_per_slot()[slot])
        return probes_sharing

    def check_ready_for_processing(self):
        #Add test of matlab engine
        npx_module_dict = {}
        for probe, params in self.probes.items():
            module_list = []
            start_num = self.modules.index(params.start_module)
            end_num = self.modules.index(params.end_module)
            for idx, module in enumerate(self.modules):
                if idx >= start_num and idx <= end_num:
                    module_list.append(module)
            npx_module_dict[probe] = module_list

        slot_list = []
        backup_size_dict = {}
        max_c_space_needed = 0
        def dir_size(dir_path = '.'):
            total_size = 0
            try:
                for dirpath, dirnames, filenames in os.walk(dir_path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        total_size += os.path.getsize(fp)
            except Exception:
                total_size = 0
            return total_size

        for probe in self.probes:
            module_list = npx_module_dict[probe]
            copy_raw = 'primary_backup_raw_data' in module_list
            copy_processed = 'copy_processed_data' in module_list or 'copy_while_waiting_primary' in self.copy_while_waiting_modules
            copy_raw2 = 'secondary_backup_raw_data' in module_list or 'copy_while_waiting_secondary_raw' in self.copy_while_waiting_modules
            copy_processed2 = 'secondary_backup_processed_data' in module_list or 'copy_while_waiting_secondary_processed' in self.copy_while_waiting_modules
            kilosort=('kilosort_helper' in module_list)
            extract = 'extract_from_npx' in module_list
            raw_dir = self.raw_path(probe)
            #sorted_drive = sorted_drive(probe)
            sorted_drive = self.sorted_drive(probe)
            sorted_dir = self.sorted_path(probe)
            backup_dir = self.raw_backup1(probe)
            sorted_backup_dir = self.sorted_backup1(probe)
            backup_dir2 = self.raw_backup2(probe)
            sorted_backup_dir2 = self.sorted_backup2(probe)
            if ('copy_raw_data' in npx_module_dict[probe] or 'extract_from_npx' in npx_module_dict[probe] or 'restructure_directories' in npx_module_dict[probe]):
                try:
                    print(sorted_drive)
                    free_space = psutil.disk_usage(sorted_drive).free
                    recording_size = sum(os.path.getsize(os.path.join(raw_dir,file)) for file in os.listdir(raw_dir))
                    extracted_size = 1.25*recording_size/self.probes_sharing_slot(self.slot(probe))
                    recording_size = recording_size*(not(self.slot(probe) in slot_list))
                    slot_list.append(self.slot(probe))
                except FileNotFoundError as E:
                    print('One of the directories probably doesn\'t exist - check '+probe)
                    raise E
            else: 
                try:
                    recording_size = 0
                    free_space = psutil.disk_usage(sorted_drive).free
                    if os.path.isdir(sorted_dir):
                        extracted_size = dir_size(sorted_dir)
                    else:
                        raise FileNotFoundError
                except FileNotFoundError as E:
                    print('One of the directories probably doesn\'t exist - check '+sorted_dir)
                    raise E
            logging.debug("free_space"+ str(free_space))
            logging.debug("extracted_size"+ str(extracted_size))
            residual_size = extracted_size/12
            logging.debug("residual_size"+ str(residual_size))
            kilosort_size = (30*(10**9))*kilosort
            logging.debug("kilosort_size"+ str(kilosort_size))
            median_sub_size = residual_size*('median_subtraction' in module_list)
            logging.debug("median_sub_size"+ str(median_sub_size))
            processing_size = (100*(10**6))#100 megabytes for depth png, mean waveforms and metrics 
            logging.debug("processing_size"+ str(processing_size))

            current_raw_backup = dir_size(backup_dir)
            current_processed_backup = dir_size(sorted_backup_dir)
            current_raw_backup2 = dir_size(backup_dir2)
            current_processed_backup2 = dir_size(sorted_backup_dir2)

            primary_backup_space_needed = copy_raw*max(0,recording_size -current_raw_backup) + copy_processed*(processing_size+max(0,extracted_size-current_processed_backup))
            logging.debug("primary_backup_space_needed"+ str(primary_backup_space_needed))
            secondary_backup_space_needed=  copy_raw2*max(0,recording_size -current_raw_backup2) + copy_processed2*(processing_size+max(0,extracted_size-current_processed_backup2))
            logging.debug("secondary_backup_space_needed"+ str(secondary_backup_space_needed))
            c_space_needed = kilosort*extracted_size
            
            extract = ('extract_from_npx' in module_list)
            if extract and os.path.isdir(sorted_dir):
                raise ValueError(sorted_dir, " already exists. Please delete it if you would like to repeat the extraction from npx, otherwise comment out the 'extract_from_npx' module.")
            data_space_needed = extract*extracted_size + processing_size + median_sub_size + kilosort_size
            logging.debug("data_space_needed"+ str(data_space_needed))
            try:
                backup_size_dict[params.backup1] += primary_backup_space_needed
            except:
                backup_size_dict[params.backup1] = primary_backup_space_needed
            backup_location, folder = os.path.split(params.backup2)
            try:
                backup_size_dict[backup_location] += secondary_backup_space_needed
            except:
                backup_size_dict[backup_location] = secondary_backup_space_needed
            max_c_space_needed = max(c_space_needed,max_c_space_needed)
            if free_space < data_space_needed:
                print('check ' +probe)
                raise ValueError('There is not enough space on one of the drives')
            print(probe+' exist and there appears to be enough disk space free for processing')

        if psutil.disk_usage(r'D:').free < max_c_space_needed:
            raise ValueError('There is not enough space on the D drive for kilosort to process the largest dataset')
        else: print('There appears to be enough space on the D drive for kilosort')
        for bdrive, size_needed in backup_size_dict.items():
            print('Checking space on '+ bdrive)
            if psutil.disk_usage(bdrive).free < size_needed:
                print('Free space on ',bdrive,': ',  psutil.disk_usage(bdrive).free)
                print('Space predicted needed on ',bdrive,': ', size_needed )
                raise ValueError('There is not enough space on the backup drive for all the data')
            else: print('And there appears to be enough space on backup drive '+bdrive)
        #raise(ValueError)
        ####################################################################

    def process_npx(self, x):
        pprint(self.probes)
        #time.sleep(20)
        #raise(ValueError)
        def add_warning(probe, string):
            self.logger_dict[probe].warning(string)
            try:
                self.warning_dict[probe].append(string)
            except KeyError as E:
                self.warning_dict[probe]=[string]
        
        def copy_data(source, destination, probe,module):
            self.logger_dict[probe].info("{}: Copying data from {} to {} ...".format(module,source,destination))
            try:
                os.mkdir(destination)
            except Exception as E:
                add_warning(probe,"For "+module+" files were not copied if they already existed.")
            command_string = "robocopy "+ source +" "+destination +r" /e /xc /xn /xo"
            self.logger_dict[probe].info(command_string)
            self.process_dict[probe][module] = subprocess.Popen(command_string)#,stdout = subprocess.PIPE,stderr = subprocess.PIPE))
                #shutil.copytree(extracted_data_location, new_location)

        def move_data(source, destination, probe,module):
            self.logger_dict[probe].info("{}: Moving data from {} to {} ...".format(module,source,destination))
            try:
                os.mkdir(destination)
            except Exception as E:
                add_warning(probe,"For "+module+" files were not moved if they already existed.")
            command_string = "robocopy "+ source +" "+destination +r" /e /xc /xn /xo /move"
            self.logger_dict[probe].info(command_string)
            self.process_dict[probe][module] = subprocess.Popen(command_string)#,stdout = subprocess.PIPE,stderr = subprocess.PIPE))
                #shutil.copytree(extracted_data_location, new_location)

        def get_next_copy_module(incomplete_modules_list):
            next_module = False
            other_modules = all_active_modules()
            network_busy = set(other_modules).intersection(self.network_modules)
            backup_busy = set(other_modules).intersection(self.backup_modules)
            for module in incomplete_modules_list:
                no_network_conflict = not(module in self.network_modules) or not(network_busy) 
                no_backup_conflict  = not(module in self.backup_modules) or not(backup_busy)
                no_slot_conflict = not(module in self.slot_modules) or slot_module_status(module) == 'Ready'
                #print(module,'+', no_network_conflict,'+', no_backup_conflict,'+', no_slot_conflict)
                if no_network_conflict and no_backup_conflict and no_slot_conflict:
                    next_module = module
                    break
            return next_module

        def initiate_copy_module(probe, idx, copy_module_list):
            incomplete_modules_list = incomplete_modules(copy_module_list, probe)
            #print(incomplete_modules_list)
            module_info = False
            failed = False
            next_module = get_next_copy_module(incomplete_modules_list)
            #print(next_module)
            if next_module:
                print('initiating copy module')
                next_module, module_info, failed = initiate_next_module(next_module, probe)
            else: 
                next_module = False
            return next_module, module_info, failed


        def all_active_modules():
            active_modules = []
            for probe in self.probes:
                active_modules.extend(get_active_modules(probe))
            return active_modules

        def slot_module_status(module):
            status = False
            try:
                status = self.slot_modules[module][self.slot(probe)]
            except KeyError as E:
                pass
            #print(module, status)
            return status

        def initiate_next_module(next_module, probe):
            self.logger_dict[probe].info('initiating {} for {}'.format(next_module,probe))
            now = datetime.datetime.now()
            this_module_info = self.module_info(None,None,None,now,None, None)
            self.info_dict[probe][next_module] = this_module_info
            if (next_module in self.slot_modules):
                    self.slot_modules[next_module][self.slot(probe)] = "Initiated"
            failed = 0
            try:
                session_id = self.session_id(probe)
                input_json = os.path.join(self.json_directory, session_id  + '_' + probe + '_' + next_module+ '-input.json')
                output_json = os.path.join(self.json_directory, session_id  + '_' + probe + '_' + next_module + '-output.json')
                ########################
                #directory = r'D:\test_2019-07-25_18-16-48_probeA_sorted'
                #info = createInputJson(input_json,
                #    kilosort_output_directory=os.path.join(directory, 'continuous', 'Neuropix-PXI-100.0'),
                #    extracted_data_directory=directory,
                #    probe_type=self.probe_type)



                #############################



                info = createInputJson(
                    output_file=input_json, 
                    npx_directory=self.raw_path(probe), 
                    extracted_data_directory=self.extracted_path_head(probe),
                    lfp_directory = self.sorted_LFP_path(probe),
                    kilosort_output_directory=self.sorted_AP_path(probe), 
                    probe_type=self.probe_type
                )
                command_string = "python -W ignore -m ecephys_spike_sorting.modules." + next_module + " --input_json " + input_json \
                  + " --output_json " + output_json

                # ["python", "-W", "ignore", "-m", "ecephys_spike_sorting.modules." + next_module, 
                #                        "--input_json", input_json,
                #                        "--output_json", output_json]
                self.logger_dict[probe].info(command_string)
                start_module(probe,next_module, command_string, info)
            except Exception as E:
                self.logger_dict[probe].error("Error initiating " + next_module+" for " +probe)
                self.logger_dict[probe].exception(E)
                failed = 1
            return next_module, this_module_info, failed

        def start_module(probe, module, command_string, info):
            if module == 'primary_backup_raw_data1' or module == 'primary_backup_raw_data2':
                current_location = self.raw_path(probe)
                backup_location = self.raw_backup1(probe)
                copy_data(current_location,backup_location, probe,module)
                if os.path.getsize(current_location) < 30*(10**9):
                        copy_data(current_location,backup_location, probe,module)
            elif module == 'move_processed_for_phy':
                current_location = self.sorted_path(probe)
                backup_location = self.phy_viewing_drive
                if os.path.getsize(current_location) < 30*(10**9):
                        move_data(current_location,backup_location, probe,module)
            elif module == 'primary_processed_lims_only':
                current_location = self.sorted_path(probe)
                backup_location = self.sorted_backup1(probe)
                copy_data(current_location,backup_location, probe,module)
            elif module == 'primary_backup_processed_data' or module == 'copy_while_waiting_primary_processed':
                current_location = self.sorted_path(probe)
                backup_location = self.sorted_backup1(probe)
                copy_data(current_location,backup_location, probe,module)
            elif module == 'secondary_backup_raw_data':
                current_location = self.raw_path(probe)
                backup_location = self.raw_backup2(probe)
                copy_data(current_location,backup_location, probe,module)
            elif module == 'secondary_backup_processed_data' or module == 'copy_while_waiting_secondary_processed':
                current_location = self.sorted_path(probe)
                backup_location = self.sorted_backup2(probe)
                copy_data(current_location,backup_location, probe,module)
            elif module == 'cleanup':
                dir_sucess = check_data_processing(self.probe_type, self.raw_path(probe), self.sorted_path(probe), self.raw_backup1(probe), self.raw_backup2(probe), self.sorted_backup1(probe), self.sorted_backup2(probe), self.lims_upload_drive)
                self.success_list.append(dir_sucess)
                no_returncode(probe,module,  rcode_in = int(not(dir_sucess)))
            elif module == 'extract_from_npx':
                skip_verify_backup = self.skip_verify_backup
                backup_verified = False
                try:
                    probe_raw_path = self.raw_path(probe)
                    recording_size = sum(os.path.getsize(os.path.join(probe_raw_path,recording)) for recording in os.listdir(probe_raw_path))
                    probe_backup_path = self.raw_backup1(probe)
                    backup_size = sum(os.path.getsize(os.path.join(probe_backup_path,recording)) for recording in os.listdir(probe_raw_path))
                    if not recording_size == backup_size:
                        raise ValueError('One of the backups failed')
                    else:
                        backup_verified = True
                except Exception as E:
                    if skip_verify_backup:
                        self.logger_dict[probe].warning("Unable to verify raw backup of "+ probe+" before extracting.")
                    else:
                        self.logger_dict[probe].warning("Unable to verify raw backup of "+ probe+" before extracting. If verification is not needed override this portion of the script")
                        raise(E)
                if backup_verified or skip_verify_backup:
                    self.process_dict[probe][module] = subprocess.Popen(command_string.split(' '), stdout = subprocess.PIPE,stderr = subprocess.PIPE)
            elif module == 'edit_probe_json':
                serial_number = edit_probe_json(probe)
                if serial_number == None:
                    add_warning(probe, 'Could not find settings.xml for '+probe)
                no_returncode(probe, module)
            elif module == 'copy_logs':
                copy_logs(probe)
                no_returncode(probe, module)
            elif module == 'add_noise_class_to_metrics':
                add_noise_class_to_metrics(probe)
                no_returncode(probe, module)
            elif module == 'restructure_directories':
                restructure_directories(probe)
                no_returncode(probe, module)
            else:
                self.process_dict[probe][module] = subprocess.Popen(command_string.split(' '), stdout = subprocess.PIPE,stderr = subprocess.PIPE)

        def no_returncode(probe, module, rcode_in = 0):
            self.logger_dict[probe].info('finished '+module+', no exit status to fetch')
            self.info_dict[probe][module]._replace(rcode = rcode_in, output = None, error = None, endtime = datetime.datetime.now())

        def restructure_dir(src, dest):
            sucess = False
            try:
                goal_empty = os.path.split(dest)[0]
                os.makedirs(os.path.split(dest)[0])
            except Exception as E:
                if os.path.isdir(goal_empty):
                    try:
                        os.rmdir(dest)
                        raise(ValueError)
                    except Exception as E2:
                        logging.warning(E2, exc_info=True)
                logging.warning(E, exc_info=True)
            try:
                os.rename(src, dest)
                sucess = True
            except Exception as E:
                logging.warning(E, exc_info=True)
            return sucess

        def restructure_directories(probe):
            print('Probe Type: ', self.probe_type)
            error_string = 'Unable to rename {src} to {dest}'
            sucess_string = '{src} becomes {dest}'
            if self.probe_type == 'PXI':
                self.logger_dict[probe].info('Attempting to restructure the extracted data directories')
                dirs_to_restructure = []
                dirs_to_restructure.append((self.extracted_AP_path(probe), self.sorted_AP_path(probe)))
                dirs_to_restructure.append((self.extracted_LFP_path(probe), self.sorted_LFP_path(probe)))
                dirs_to_restructure.append((self.extracted_events_path(probe), self.sorted_events_path(probe)))
                for src, dest in dirs_to_restructure:
                    sucess = restructure_dir(src, dest)
                    if sucess:
                        self.logger_dict[probe].info(sucess_string.format(src = src, dest = dest))
                    else:
                        self.logger_dict[probe].warning(error_string.format(src = src, dest = dest), exc_info=True)
            else:
                pass

        def copy_logs(probe):
            save_progess_stats(probe)
            log_location = os.path.join(self.sorted_path(probe), 'logs')
            start_date_string = self.start.strftime("%y.%m.%d.%I.%M.%S")
            log_dir = os.path.join(log_location, start_date_string)
            try: 
                os.mkdir(log_location)
            except Exception as E: 
                pass
            os.mkdir(log_dir)
            session_name = self.session_name
            session_id = session_name.split('_')[0]
            for name in os.listdir(self.json_directory):
                if session_id in name and probe in name:
                    date_maybe = name.split('_')[1]
                    if len(date_maybe) ==17:
                        if date_maybe == start_date_string:
                            source = os.path.join(self.json_directory, name)
                            dest = os.path.join(log_dir, name)
                            shutil.copy2(source,dest)
                    else:   
                        source = os.path.join(self.json_directory, name)
                        dest = os.path.join(log_dir, name)
                        shutil.copy2(source,dest)

        def add_noise_class_to_metrics(probe):
            try:
                directory = self.sorted_AP_path(probe)

                cluster_groups = pd.read_csv(os.path.join(directory, 'cluster_group.tsv.v2'), sep='\t')

                metrics = pd.read_csv(os.path.join(directory, 'metrics.csv'), index_col=0)
                
                metrics2 = metrics.merge(cluster_groups, on='cluster_id')
                
                metrics2 = metrics2.rename(columns={'group':'quality'})
                
                #num_good += np.sum(metrics2['quality'] == 'good')
                #num_noise += np.sum(metrics2['quality'] == 'noise')
                
                metrics2.to_csv(os.path.join(directory, 'metrics.csv'))
            except Exception as E:
                self.logger_dict[probe].exception('Failed to append the noise column to the metrics CSV')

        def get_settings_xml_value(probe, element_name, attribute_name, default):
            settings_path = self.settings_path(probe)
            value = default
            if self.probe_type == 'PXI':
                slot = str(self.slot_num(probe))
                port = self.port(probe)
                try:
                    tree = ET.parse(settings_path)
                    root = tree.getroot()
                    for elemnt in root.iter(element_name):
                        if elemnt.attrib['port'] == port and elemnt.attrib['slot'] == slot:
                            value = elemnt.attrib[attribute_name]
                except Exception as E:
                    self.logger_dict[probe].exception(E)
            else:
                try:
                    #serial_number = None
                    tree = ET.parse(settings_path)
                    root = tree.getroot()
                    for elemnt in root.iter(element_name):
                        value = elemnt.attrib[attribute_name]
                except Exception as E:
                    self.logger_dict[probe].exception(E)
            return value

        def get_settings_xml_element_text(probe, element_name, default):
            settings_path = self.settings_path(probe)
            value = default
            try:
                #serial_number = None
                tree = ET.parse(settings_path)
                root = tree.getroot()
                for elemnt in root.iter(element_name):
                    value = elemnt.text
            except Exception as E:
                self.logger_dict[probe].exception(E)
            return value

        def check_noise_channels(mask):
            """Check to see if there are too many chaannels masked, and default to only masking the reference channels if so"""
            if sum(not(channel) for channel in mask)>30:
                mask = 384*[True]
                references = [36, 73, 75, 112, 151, 188, 227, 264, 303, 340, 379]
                for ref in references:
                    mask[ref] = False
            return mask

        def verify_mask(probe_json):
            probe_json['original_mask'] = probe_json['mask']
            probe_json['mask'] = check_noise_channels(probe_json['mask'])
            return probe_json


        def edit_probe_json(probe):
            json_path = os.path.join(self.sorted_path(probe),'probe_info.json')
            self.logger_dict[probe].info('Adding the software and probe info to the probe_json at path'+json_path)
            probe_json = {}
            try:
                with open(json_path, "r") as read_file:
                    probe_json = json.load(read_file)
            except Exception as E:
                self.logger_dict[probe].exception('Error reading probe_json')
            try:
                probe_json = verify_mask(probe_json)
            except Exception as E:
                self.logger_dict[probe].exception('Error Verifying the mask and setting to default if too many masked')

            if self.probe_type == 'PXI':
                probe_element = 'PROBE'
            else:
                probe_element = 'NEUROPIXELS'
            serial_number = get_settings_xml_value(probe, probe_element, 'probe_serial_number', None)
            if not('software' in probe_json):
                probe_json["software"] =  {
                    "name" : "Open Ephys GUI",
                    "version" : get_settings_xml_element_text(probe, 'VERSION',"0.4.4"),
                    "machine" : get_settings_xml_element_text(probe, 'MACHINE',os.environ['COMPUTERNAME']),
                    "os" : "Windows 10"
                } 
            if not('probe' in probe_json):
                probe_json["probe"] = {
                    "phase" : "3a", 
                    "ap gain" : get_settings_xml_value(probe, probe_element, 'apGainValue',"500x"),
                    "lfp gain" : get_settings_xml_value(probe, probe_element, 'lfpGainValue',"250x"),
                    "reference channel" : get_settings_xml_value(probe, probe_element, 'referenceChannel',"Ext"),
                    "filter cut" : get_settings_xml_value(probe, probe_element, 'filterCut', "300 Hz"),
                    "serial number" : serial_number,
                    "slot": self.slot(probe),
                    "port": self.port(probe),
                    "option" : "3",

                    "subprocessors" :[
                        {
                            "name" : "Neuropix-3a-100.0",
                            "type" : "AP band",
                            "num channels" : 384,
                            "sample_rate" : 30000.0,
                            "bit volts" : 0.195
                        },
                        {
                            "name" : "Neuropix-3a-100.1",
                            "type" : "LFP band",
                            "num channels" : 384,
                            "sample_rate" : 2500.0,
                            "bit volts" : 0.195
                        }
                    ]

                }
            with open(json_path, "w") as write_file:
                json.dump(probe_json, write_file, indent=4)

            try:
                png_path = os.path.join(self.sorted_path(probe),'probe_depth.png')
                self.logger_dict[probe].info('Renaming the depth image to be probe specific'+png_path)
                new_png_path = os.path.join(self.sorted_path(probe),'probe_depth_'+self.probe_letter(probe)+'.png')
                os.rename(png_path, new_png_path)
            except Exception as E:
                self.logger_dict[probe].info('Error Renaming the depth image to be probe specific'+png_path)
            return serial_number

        def get_next_module(current_module,probe):  
            try:
                #print(current_module in self.copy_while_waiting_modules, module_ready(probe, 'kilosort_helper'))
                #print(current_module in self.final_copy_all_parallel , not(finished_final_copy(probe)) , previous_main_module_accounted_for('final_copy_parallel', probe))
                if current_module in self.copy_while_waiting_modules and module_ready(probe, 'kilosort_helper'):
                    next_module = 'kilosort_helper'
                elif current_module in self.final_copy_all_parallel and not(finished_final_copy(probe)) and previous_main_module_accounted_for('final_copy_parallel', probe):
                    next_module = 'final_copy_parallel'
                    #print(probe + 'Assigning next_module to final copy')
                else:   
                    next_module_idx = self.modules.index(current_module)+1
                    next_module =  self.modules[next_module_idx]
            except (ValueError,IndexError) as E:
                if current_module:
                    next_module = self.probes[probe].end_module
                else:
                    next_module = self.probes[probe].start_module
            if self.failed_dict[probe]:
                try:
                    next_module_idx =  self.modules.index(next_module)
                except Exception as E:
                    #next is probably a kilosort wait module. If median sub has failed for some reason we shouldn't proceed with kilosort. 
                    next_module_idx = 0
                alt_next_module_idx = self.modules.index('copy_logs')
                if next_module_idx < alt_next_module_idx:
                    next_module = 'copy_logs'
            next_module_complete = (next_module in self.slot_modules) and (slot_module_status(next_module)== "Finished")
            if next_module_complete:
                if next_module == self.probes[probe].end_module:
                    if not(self.finished_list[idx]):
                            self.finished_list[idx] = 1
                            self.logger_dict[probe].info("Finished processing "+ probe)
                else:
                    next_module = get_next_module(next_module,probe)
            return next_module

        def count_kilosort_ready():
            count = 0
            for probe in self.probes:
                # median sub needs to be finished, and not busy. It will be busy as soon as it has started another module
                if module_ready(probe, 'kilosort_helper') and not(is_busy(probe)):
                    count += 1
            return count

        def module_ready(probe, module):
            prev_accounted_for = previous_main_module_accounted_for(module, probe)
            mod_finished = module_initiated(module, probe)
            mod_scheduled = main_module_scheduled(module, probe)
            return prev_accounted_for and not(mod_finished) and mod_scheduled

        def previous_main_module_accounted_for(module, probe):
            prev_mod_index = self.modules.index(module)-1
            if prev_mod_index < 0:
                # Then the module is the start module and we should assume and prvious have been accounted for
                return True
            else:
                previous_module = self.modules[prev_mod_index]
                return main_module_accounted_for(previous_module, probe)

        def main_module_accounted_for(module, probe):
            mod_complete = module_complete(module, probe)
            mod_skipped = not(main_module_scheduled(module, probe))
            return mod_complete or mod_skipped

        def main_module_scheduled(module, probe):
            return self.modules.index(module) >= self.modules.index(self.probes[probe].start_module)


        def module_complete(module, probe):
            complete = False
            try:
                complete = self.info_dict[probe][module].rcode is not None
            except KeyError as E:
                try:
                    slot_module_status(module) == "Finished"
                except KeyError as E:
                    pass 
            return complete

        def any_probe_module_complete(module):
            complete = False
            for probe in self.probes:
                if module_complete(module, probe):
                    complete = True
            return complete

        def module_initiated(module, probe):
            initiated = False
            initiated = module in self.info_dict[probe]
            if not(initiated) and module in self.slot_modules:
                initiated = not(slot_module_status(module) == "Ready")
            return initiated
        
        def incomplete_modules(modules, probe):
            incomplete_list = []
            for module in modules:
                if not(module_initiated(module, probe)):
                    incomplete_list.append(module)
            #print(incomplete_list)
            return incomplete_list

        def finished_final_copy(probe):
            incomplete_list = incomplete_modules(self.final_copy_all_parallel, probe)
            finished = not(incomplete_list)
            return finished

        def get_active_modules(probe):
            active_list = []
            for module_name, info in self.info_dict[probe].items():
                if module_initiated(module_name, probe) and not(module_complete(module_name, probe)):
                    active_list.append(module_name)
            return active_list

        def log_out(p, logger):
            output_line_list = []
            try:
                p.stdout.seek(0,2)
                pos = p.stdout.tell()
                output = []
                if pos:
                    tot_read = 0
                    while tot_read < pos:
                        line = p.stdout.readline()
                        output_str = str(line.rstrip())[2:-1]
                        logger.info(output_str)
                        output_line_list.append(output_str)
                        tot_read = tot_read +len(line)
            except (ValueError, AttributeError) as E:
                logger.warning('Failed to read stdout',exc_info = True)
            return output_line_list

        def log_progress(probe):
            for module, info in self.info_dict[probe].items():
                if info.rcode is None:
                    try:
                        p = self.process_dict[probe][module]
                        module_finished =  p.poll() is not None
                    except KeyError as E:
                        p = None
                        module_finished = False
                    out_list = []
                    if not(module in self.copy_modules) and not(module in self.no_process_modules) and p is not None: 
                        out_list = log_out(p,self.logger_dict[probe])
                    if out_list:
                        self.last_output_dict[probe]['last_log_time'] = datetime.datetime.now()
                        self.last_output_dict[probe]['last_log'] = out_list
                    if module_finished:
                        self.logger_dict[probe].info("fetching exit status and info for"+module+' for probe '+probe)
                        try:
                            output,error  = p.communicate()
                            try:
                                output = output.decode("utf-8")
                            except Exception as E:
                                pass
                            try:
                                error = error.decode("utf-8")
                            except Exception as E:
                                pass
                            mod_start_time = self.info_dict[probe][module].starttime
                            now = datetime.datetime.now()
                            #startstr = mod_start_time.strftime("%y.%m.%d.%I.%M.%S")
                            #endstr = now.strftime("%y.%m.%d.%I.%M.%S")
                            process_time_str = (now-mod_start_time).seconds
                            self.info_dict[probe][module]._replace(rcode = p.returncode, output = output, error = error, endtime = now, processtime = process_time_str)
                            self.logger_dict[probe].info("finished fetching exit status and info for "+ module+" "+probe)

                            robocopy = module in self.copy_modules
                            #print(robocopy)
                            if not(p.returncode == 0) and not(robocopy and p.returncode < 4):
                                self.failed_dict[probe] == 1
                                self.logger_dict[probe].error("return code "+str(p.returncode)+" for "+ module+" "+probe)
                                try:
                                    for line in error.splitlines():
                                        self.logger_dict[probe].error(line)
                                except Exception as E:
                                    self.logger_dict[probe].info('No output to print')
                                self.logger_dict[probe].info("setting "+ probe+ "status to failed ")
                            if (module in self.slot_modules):
                                self.slot_modules[module][self.slot(probe)] = "Finished"
                        except IndexError as E:
                            self.logger_dict[probe].exception('There was an error fetching the exit status for '+probe)
                        print('about to save progress stats for '+probe)
                        save_progess_stats(probe)   

        def print_progress_stats():
            print("Finished processing all directories")
            try:
                for probe in self.probes:
                    for module, info in self.info_dict[probe].items():
                        print(probe,": ",module)
                        print("Start time: ", info.starttime, " Endtime: ", info.endtime, " Processing time: ", info.processtime)
            except Exception as E:
                print("Error printing processing info")
                print(E)

            try:    
                for probe in self.probes:
                    for module, info in self.info_dict[probe].items():
                        if info.rcode is not 0:
                            print("Module: ", module,",  Return Code: ", info.rcode)
                            print("Output: ", info.output)
                            print("Error: ", info.error)
            except Exception as E:
                print("Error printing nonzero returncodes")
                print(E)

            if self.warning_dict:
                pprint(self.warning_dict)
            else:
                print("No processing script warnings occurred")

            if self.failed_dict:
                pprint(self.failed_dict)
            else:
                print("No processing script failures occurred")

        def is_busy(probe):
            busy = False
            for module, p in self.process_dict[probe].items():
                if p.poll() is None:
                    busy = True
            return busy

        def save_progess_stats(probe):
            print('about to save prgress stats for '+probe)
            limsID = self.lims_ID(probe)
            start_string = self.start.strftime("%y.%m.%d.%I.%M.%S")
            json_compatible_info_dict = {}
            for a_probe in self.probes:
                json_compatible_info_dict[a_probe] = {}
                for module, info in self.info_dict[a_probe].items():
                    json_compatible_info_dict[a_probe][module]=info._asdict()
                    #print('check for strings')
                    #pprint(info._asdict())
                    try:
                        json_compatible_info_dict[a_probe][module]['starttime'] = json_compatible_info_dict[a_probe][module]['starttime'].strftime("%y.%m.%d.%I.%M.%S")
                    except Exception as E:
                        pass
                    try:
                        json_compatible_info_dict[a_probe][module]['endtime'] = json_compatible_info_dict[a_probe][module]['endtime'].strftime("%y.%m.%d.%I.%M.%S")
                    except Exception as E:
                        pass
                    #json_compatible_info_dict[probe][module]['Processing time seconds'] = (info.endtime-info.starttime).seconds
            path = os.path.join(self.json_directory, limsID+'_'+start_string+'all_probes_all-module-info'+".json")
            with open(path, "w") as write_file:
                json.dump(json_compatible_info_dict,write_file, indent=4)
            path = os.path.join(self.json_directory, limsID+'_'+start_string+'all_probes_nonzero-rcode-info'+".json")
            nonzero_returncode_dict = {}
            for a_probe in self.probes:
                nonzero_returncode_dict[a_probe] = {}
                for module, info in json_compatible_info_dict[a_probe].items():
                    if info['rcode'] is not 0:
                        nonzero_returncode_dict[a_probe][module]=info
            with open(path, "w") as write_file:
                json.dump(nonzero_returncode_dict, write_file, indent=4)
            path = os.path.join(self.json_directory, limsID+'_'+start_string+'all_probes_in-script-warnings'+".json")
            with open(path, "w") as write_file:
                json.dump(self.warning_dict, write_file, indent=4)
            path = os.path.join(self.json_directory, limsID+'_'+start_string+'all_probes_in-script-errors'+".json")
            with open(path, "w") as write_file:
                json.dump(self.failed_dict, write_file, indent=4)

            path = os.path.join(self.json_directory, limsID+'_'+start_string+'_'+probe+'_all-module-info'+".json")
            with open(path, "w") as write_file:
                json.dump(json_compatible_info_dict[probe], write_file, indent=4)
            path = os.path.join(self.json_directory, limsID+'_'+start_string+'_'+probe+'_nonzero-rcode-info'+".json")
            with open(path, "w") as write_file:
                json.dump(nonzero_returncode_dict[probe], write_file, indent=4)
            path = os.path.join(self.json_directory, limsID+'_'+start_string+'_'+probe+'_in-script-warnings'+".json")
            try:
                with open(path, "w") as write_file:
                    json.dump(self.warning_dict[probe], write_file, indent=4)
            except KeyError as E:
                pass
            path = os.path.join(self.json_directory, limsID+'_'+start_string+'_'+probe+'_in-script-errors'+".json")
            with open(path, "w") as write_file:
                json.dump(self.failed_dict[probe], write_file, indent=4)
            #TODO figure out how to make the outputs and errors print nicely again


    ################################################################

        #TODO change format so there is a process state dict to make things more self documenting? might be worse...


        while sum(self.finished_list) < len(self.probes):

            for idx, probe in enumerate(self.probes):
                #print('looping')
                busy = is_busy(probe)
                next_module = get_next_module(self.current_modules[idx],probe)

                if self.current_modules[idx] and not(self.current_modules[idx] in self.no_process_modules):
                    try:
                        log_progress(probe)
                    except Exception as E:
                        self.logger_dict[probe].exception('Failed to log progress')
                time_since_last_log =  (datetime.datetime.now()-self.last_output_dict[probe]['last_log_time']).total_seconds()
                if time_since_last_log > 300:
                    if module_complete(self.current_modules[idx], probe):
                        print('Probe {} is currently waiting to start module {}. Here is the last output:'.format(probe, next_module))
                    else:
                        print('Probe {} is currently on module {}. Here is the last output:'.format(probe, self.current_modules[idx]))
                    for out_string in self.last_output_dict[probe]['last_log']:
                        print(out_string)
                        self.last_output_dict[probe]['last_log_time'] = datetime.datetime.now()
                time_elapsed =  (datetime.datetime.now()-self.start).total_seconds()
                #print('time elapsed = ', time_elapsed)
                start_wait = next_module == 'extract_from_npx' and self.current_modules.count('extract_from_npx')>0 #and time_elapsed<1200*idx#this actually needs to be based on the index of the slot...but as long as we keep the probes in order it should work for now
                m_sub_wait = next_module == 'median_subtraction' and (any_probe_module_complete('median_subtraction') == False and not(self.current_modules.count('median_subtraction') == 0))
                #TODO edit copy wait so it waits extra long to copy down if there is another drive letter already working, and estimates the expected time instaed of just 20 minutes
                kilosort_wait = next_module == 'kilosort_helper' and 'kilosort_helper' in self.current_modules
                slot_wait = (next_module in self.slot_modules) and not(self.slot_modules[next_module][self.slot(probe)] == "Ready")
                cleanup_wait = next_module == 'cleanup' and time_elapsed<50400 and not(self.probes[probe].start_module=='cleanup') # wait 14 hours to cleanup to make sure lims1 upload can grab folders
                final_copy = next_module == 'final_copy_parallel'
                wait = kilosort_wait or start_wait or slot_wait or cleanup_wait or final_copy or m_sub_wait
                #print(wait, kilosort_wait , start_wait , slot_wait , cleanup_wait , final_copy, m_sub_wait)
                #count = count_kilosort_ready()
                #print('kilosort ready: ', count)
                #print(probe + ' next module is ' + next_module)
                if not(busy) and kilosort_wait and (count_kilosort_ready() > 1):
                    #print('attempting to initiate copy_while_waiting')
                    next_module, next_module_info, copy_failed = initiate_copy_module(probe, idx, self.copy_while_waiting_modules)
                    if next_module and not(copy_failed):
                        self.current_modules[idx] = next_module
                        #self.info_dict[probe][self.current_modules[idx]] = next_module_info
                
                if final_copy:
                    #print('attempting to initiate final copy')
                    next_module, next_module_info, copy_failed = initiate_copy_module(probe, idx, self.final_copy_all_parallel)
                    if next_module and not(copy_failed):
                            self.current_modules[idx] = next_module

                if (self.current_modules[idx] == self.probes[probe].end_module) and (self.info_dict[probe][self.current_modules[idx]].rcode is not None) and (self.finished_list[idx] == 0):
                    self.finished_list[idx] = 1
                    self.logger_dict[probe].info("Finished processing "+ probe)

                ready_for_next_module = not(busy) and not(wait) and not(self.finished_list[idx]) and (self.failed_dict[probe]==0)
                copy_after_failure = not(busy) and not(self.failed_dict[probe]==0) and (next_module in self.copy_modules)
                #print(ready_for_next_module , copy_after_failure)
                if ready_for_next_module or copy_after_failure:
                    self.current_modules[idx], next_module_info , self.failed_dict[probe] = initiate_next_module(next_module, probe)

                time.sleep(3)

        print_progress_stats()
        computer = os.environ['COMPUTERNAME']
        sucess = all(set(self.success_list))
        if sucess:
            self.set_completed(self.session_name, computer)
        else: print('processing was not verified so no signal was sent')

        self.assistant_set_session(self.session_name)

        self.make_batch_files(self.session_name)

        self.cleanup_DAQs()

        check_all_space(self.probes)
        return session_name, sucess

    def get_processing_assitant_proxy(self):
        computer = os.environ['COMPUTERNAME']
        port = '1212'
        print('Creating Proxy for device:Day2_Agent at host: '+computer+' port: '+port+' device name: Day2_Agent')
        #Create the Proxy for the dummy components
        fullport = computer+':'+port
        proxy = Proxy(fullport, serialization='json')
        ping_result = os.system('ping %s -n 1' % (computer,))
        if ping_result:
            print('Host '+computer+' Not Found')
            # LAN WAKE UP CALL GOES HERE
        else:
            print('Host '+computer+' Found')
        return proxy

    def make_batch_files(self, session_name):
        proxy = self.get_processing_assitant_proxy()
        try:
            proxy.create_bat_files(session_name)
            print('signaled assistant to create batch file sucessfully')
        except Exception as E:
            print('failed to signal assistant to create batch file')
            print(E)

    def cleanup_DAQs(self):
        proxy = self.get_processing_assitant_proxy()
        try:
            proxy.cleanup_daqs()
            print('signaled assistant to cleanup daqs sucessfully')
        except Exception as E:
            print('failed to signal assistant to cleanup daqs')
            print(E)

    def assistant_set_session(self, session_name):
        proxy = self.get_processing_assitant_proxy()
        try:
            proxy.set_session_name(session_name)
            print('signaled assistant to set session sucessfully')
        except Exception as E:
            print('failed to signal assistant to set session')
            print(E)

    def set_completed(self, session, computer):
        if self.WSE_computer is None:
            WSE_computer = 'W10DTSM18307'
        else:
            WSE_computer = self.WSE_computer
        port = '1234'
        print('Creating Proxy for device:Day2_Agent at host: '+WSE_computer+' port: '+port+' device name: Day2_Agent')
        #Create the Proxy for the dummy components
        fullport = WSE_computer+':'+port
        proxy = Proxy(fullport, serialization='json')
        ping_result = os.system('ping %s -n 1' % (WSE_computer,))
        if ping_result:
            print('Host '+WSE_computer+' Not Found')
            # LAN WAKE UP CALL GOES HERE
        else:
            print('Host '+WSE_computer+' Found')

        initiated = True
        try:    
            proxy.signal_completed(session, computer) 
            print('signaled complete sucessfully')
        except Exception as E:
            print('failed to signal complete')
            print(E)
                
if __name__ == '__main__':
    processor = processing_session(session_name, probes_in, probe_type)
    processor.start_processing()
