
from helpers.batch_processing_common import processing_session
from helpers.batch_processing_config import get_from_config, get_from_kwargs
import sys


session_name = '2053709239_532246_20200930'#test_2019-07-25_18-16-48' #Fill in with appropriate session name
probes_in = get_from_config('processable_probes')#['D', 'E', 'F']
cortex_only = False

start_module = 'extract_from_npx'
end_module = 'cleanup'

#default_backup1 = os.path.join(get_from_config('network_backup', kwargs), session_name)
#default_backup2 = get_from_config('disk_backup')

modules = [
   #'copy_back_primary_raw_data',
   #'copy_back_secondary_raw_data',
   #'primary_backup_raw_data1',
   'extract_from_npx',
   'restructure_directories',
   'depth_estimation',
   'median_subtraction',
   'kilosort_helper',
   'noise_templates',
   'mean_waveforms',
   'quality_metrics',
   'add_noise_class_to_metrics',
   'copy_logs', 
   'final_copy_parallel',
   #'primary_backup_raw_data1',#combine these into one module - or allow it to kick off multiple processes without waiting?
   #'primary_backup_processed_data',#combine these into one module - or allow it to kick off multiple processes without waiting?
   #'secondary_backup_processed_data',#combine these into one module - or allow it to kick off multiple processes without waiting?
   #'secondary_backup_raw_data',#combine these into one module - or allow it to kick off multiple processes without waiting? is it really that simple?
   'cleanup'
   #'primary_processed_lims_only',
   #'move_processed_for_phy',
]


copy_while_waiting_modules = [
    'cww_primary_backup_raw_data',
    #'cww_primary_backup_processed', # need to name these differently because both may be run
    'cww_secondary_backup_raw_data', #these can be the same as the main modules because only needs to run once - slot module prevents from running again
    #'cww_secondary_backup_processed'
]

final_copy_all_parallel = [
    'final_primary_backup_raw_data',
    'final_primary_backup_processed', # need to name these differently because both may be run
    'final_secondary_backup_raw_data', #these can be the same as the main modules because only needs to run once - slot module prevents from running again
    #'final_secondary_backup_processed'
]
#slot_config:{
#     2:{
#       'acq_drive':os.path.join(get_from_kwargs('network_backup', kwargs), session_name, session_name+'probeABC'),
#       'suffix': 'probeABC',
#     },
#     3:{
#       'acq_drive':os.path.join(get_from_kwargs('network_backup', kwargs), session_name, session_name+'probeDEF'),
#       'suffix': 'probeDEF',
#     },
#    }


if __name__ == '__main__':
  try:
    session_name = sys.argv[1]
  except exception as E:
    print('No arguments found in sys call, using session name from py file instead')
  processor = processing_session(
    session_name, 
    probes_in, 
    cortex_only=cortex_only,
    modules=modules,
    copy_while_waiting_modules=copy_while_waiting_modules,
    final_copy_all_parallel=final_copy_all_parallel,
    start_module = start_module,
    end_module = end_module
    )
  processor.start_processing()

