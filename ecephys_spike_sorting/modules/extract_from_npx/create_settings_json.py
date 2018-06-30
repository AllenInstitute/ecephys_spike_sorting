from xmljson import gdata
from xml.etree.ElementTree import fromstring

def create_settings_json(input_file):

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

    for processor in a['SETTINGS']['SIGNALCHAIN'][1]['PROCESSOR']:

        #print(processor)
        #print(type(processor))
    
        if str.find(processor['name'], 'Neuropix') > -1:
            
            neuropix['phase'] = processor['name'][-2:]

            try:
                settings = processor['EDITOR']['NEUROPIXELS']
                hardware_info = [info.split(': ') for info in settings['info'].split('\n')[::2]]
                
                neuropix['ap gain'] = settings['apGainValue']
                neuropix['lfp gain'] = settings['lfpGainValue']
                neuropix['reference channel'] = settings['referenceChannel']
                neuropix['filter cut'] = settings['filterCut']
                
                for info in hardware_info:
                    neuropix[str.lower(info[0])] = info[1]
            except KeyError:
                neuropix['error'] = 'probe info not found'
            
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

    return oe_json

