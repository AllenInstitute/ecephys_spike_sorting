from collections import OrderedDict
from xmljson import gdata
from xml.etree.ElementTree import fromstring
import io, json, os

def create_settings_json(input_file, output_directory):

    with open (input_file, "r") as file:
        file_string = file.read()

    a = gdata.data(fromstring(file_string))    

    info_dict = { }

    info_dict['software'] = 'Open Ephys GUI'
    info_dict['version'] = a['SETTINGS']['INFO']['VERSION']['$t']
    info_dict['machine'] = a['SETTINGS']['INFO']['MACHINE']['$t']
    info_dict['os'] = a['SETTINGS']['INFO']['OS']['$t']
    info_dict['date'] = a['SETTINGS']['INFO']['DATE']['$t']

    neuropix = { }

    for processor in a['SETTINGS']['SIGNALCHAIN']['PROCESSOR']:
        
        if str.find(processor['name'], 'Neuropix') > -1:
            
            neuropix['phase'] = processor['name'][-2:]
            settings = processor['EDITOR']['NEUROPIXELS']
            hardware_info = [info.split(': ') for info in settings['info'].split('\n')[::2]]
            
            neuropix['ap gain'] = settings['apGainValue']
            neuropix['lfp gain'] = settings['lfpGainValue']
            neuropix['reference channel'] = settings['referenceChannel']
            neuropix['filter cut'] = settings['filterCut']
            
            for info in hardware_info:
                neuropix[str.lower(info[0])] = info[1]
            
            sp0 = {}
            sp0['name'] = 'Neuropix-3a-100.0'
            sp0['type'] = 'AP band'
            sp0['num_channels'] = 384
            sp0['sample_rate'] = 30000.0
            sp0['bit_volts'] = 0.195
            
            sp1 = {}
            sp1['name'] = 'Neuropix-3a-100.1'
            sp1['type'] = 'LFP band'
            sp1['num_channels'] = 384
            sp1['sample_rate'] = 2500.0
            sp1['bit_volts'] = 0.195
            
            neuropix['subprocessors'] = [sp0, sp1]
            
    oe_json = { }
    oe_json['info'] = info_dict
    oe_json['neuropix'] = neuropix

    output_file = os.path.join(output_directory, 'open-ephys.json')

    with io.open(output_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(oe_json, ensure_ascii=False, sort_keys=True, indent=4))