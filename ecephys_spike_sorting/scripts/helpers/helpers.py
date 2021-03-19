from helpers.batch_processing_config import get_from_config, get_from_kwargs
from collections import namedtuple, OrderedDict

def add_probes(session_name, **kwargs):
    key_list = ['processable_probes', 'probe_config', 'probe_params', 'start_module', 'end_module', 'network_backup', 'disk_backup']
    for key in key_list:
        kwargs[key] = get_from_kwargs(key, kwargs)

    if not('probes' in kwargs):
        kwargs['probes'] = OrderedDict()

    for probe in kwargs['processable_probes']:
        probe_key = session_name+'_probe'+probe
        probe_slot_params = kwargs['probe_config'][probe]
        slot_str = session_name+'_'+probe_slot_params['pxi_slot'] #TODO - need to get this in helpers/config as a function
        kwargs['probes'][probe_key]=kwargs['probe_params'](probe, slot_str , probe_slot_params['num_in_slot'], session_name, kwargs['start_module'], kwargs['end_module'], kwargs['network_backup'], kwargs['disk_backup'])
        #print(kwargs['probes'][probe_key])

    return kwargs['probes']