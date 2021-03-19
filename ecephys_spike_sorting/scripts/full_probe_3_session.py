
import os

from collections import namedtuple, OrderedDict

from helpers.batch_processing_common import processing_session
from helpers.batch_processing_config import get_from_config, get_from_kwargs


sessions = ['1046581736_527294_20200827', '1046651551_527294_20200827']
session_name = sessions[0]#test_2019-07-25_18-16-48' #Fill in with appropriate session name
probes_in = get_from_config('processable_probes')#['D', 'E', 'F']
cortex_only = False
start_module = 'extract_from_npx'

#default_backup1 = os.path.join(get_from_config('network_backup', kwargs), session_name)
#default_backup2 = get_from_config('disk_backup')

modules = [
   #'primary_backup_raw_data1',
   'extract_from_npx',
   'restructure_directories',
   'depth_estimation',
   'median_subtraction',
   'edit_probe_json',
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

copy_while_waiting_modules = [
    'copy_while_waiting_primary_processed', # need to name these differently because both may be run
    'secondary_backup_raw_data', #these can be the same as the main modules because only needs to run once - slot module prevents from running again
    'primary_backup_raw_data1',
    #'copy_while_waiting_secondary_processed'
]

final_copy_all_parallel = [
   'primary_backup_raw_data1',
   'primary_backup_processed_data',
   'secondary_backup_raw_data',
   #'secondary_backup_processed_data'
]

default_backup1 = os.path.join(get_from_config('network_backup'), session_name)
default_backup2 = get_from_config('disk_backup')

probe_params = get_from_config('probe_params')

slot_params = get_from_config('slot_params')

probe_config = get_from_config('probe_config')
probes = OrderedDict()
for session in sessions:
  for probe in probes_in:
      probe_key = session+'_probe'+probe #todo make this change in the common defaults as well? put this in the config as a function?
      probe_slot_params = probe_config[probe]
      probes[probe_key]=probe_params(probe, probe_slot_params['pxi_slot'], probe_slot_params['num_in_slot'], session, start_module, 'cleanup', default_backup1, default_backup2)
      print(probes[probe_key].pxi_slot)


session = '1046166369_527294_20200826'

slot_config:{
     2:{
       'acq_drive':os.path.join(r'\\W10DT05515\W', session+'probeABC'),
       'suffix': 'probeABC',
     },
     3:{
       'acq_drive':os.path.join(r'\\W10DT05515\W', session+'probeDEF'),
       'suffix': 'probeDEF',
     },
    }

for probe in probes_in:
    probe_key = session+'_probe'+probe #todo make this change in the common defaults as well? put this in the config as a function?
    probe_slot_params = probe_config[probe]
    probes[probe_key]=probe_params(probe, probe_slot_params['pxi_slot'], probe_slot_params['num_in_slot'], session, start_module, 'cleanup', default_backup1, default_backup2)
    print(probes[probe_key].pxi_slot)

if __name__ == '__main__':
	processor = processing_session(
		session_name, 
		probes_in, 
		cortex_only=cortex_only,
		modules=modules,
		copy_while_waiting_modules=copy_while_waiting_modules,
		final_copy_all_parallel=final_copy_all_parallel,
    start_module=start_module,
		probes=probes
  )
	processor.start_processing()

