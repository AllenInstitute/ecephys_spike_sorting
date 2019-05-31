import os
import shutil
import glob
import subprocess
import time

from functools import reduce

from create_input_json import createInputJson, create_samba_directory



#import ecephys_spike_sorting.modules.extract_from_npx as extract_from_npx
mice = { \
  '386129' :  'sd4',
  '387858' :  'sd4',
  '388521' :  'sd4',
  '394208' :  'sd4',
  '392810' :  'sd4',
  '404553' :  'sd4',
  '397075' :  'sd4',
  '404568' :  'sd4',
  '404551' :  'sd4',
  '398261' :  'sd4',
  '398263' :  'sd4',
  '404571' :  'sd4',
  '404555' :  'sd4',
  '404569' :  'sd4',
  '403407' :  'sd4',
  '412792' :  'sd4',
  '405755' :  'sd4',
  '404573' :  'sd4',
  '404570' :  'sd4',
  '404554' :  'sd4',
  '405751' :  'sd4',
  '406807' :  'sd4',
  '412794' :  'sd4',
 # '412793' :  'sd4',
  '406805' :  'sd4',
  '412795' :  'sd4',
  '412799' :  'sd4',
  '407972' :  'sd4', 
  '406808' :  'sd4',
  '412802' :  'sd4',
  '412801' :  'sd4',
  '410343' :  'sd4',
  '408152' :  'sd4',
  '412803' :  'sd4',
  '410344' :  'sd4',
  '408155' :  'sd4', 
  '408153' :  'sd4',
  '412804' :  'sd4',
  '412796' :  'sd4.2',
  '415149' :  'sd4.2',
  '412809' :  'sd4.2',
  '415148' :  'sd4.2',
  '419117' :  'sd4.2',
  '410315' :  'sd4.2',
  '419114' :  'sd4.2',
  '419115' :  'sd4.2',
  '419116' :  'sd4.2',
  '419112' :  'sd4.2',
  '419118' :  'sd4.2',
  '419119' :  'sd4.2',
  '417679' :  'sd4.2',
  '416861' :  'sd4.2',
  '416356' :  'sd4.2',
  '416856' :  'sd4.2',
  '416357' :  'sd4.2',
  '417678' :  'sd4.2',
  '420079' :  'sd4.2',
  '424445' :  'sd4.2',
  '418195' :  'sd4.2',
  '418196' :  'sd4.2',
  '421527' :  'sd4.2',
  '421529' :  'sd4.2',
  '421338' :  'sd4.2',
  '424448' :  'sd4.2',
  '425589' : 'sd5',
  '432106' : 'sd5',
  '422575' : 'sd5',
  '422576' : 'sd5',
  '424136' : 'sd4.2',
  '421526' : 'sd4.2',
  '425155' : 'sd5',
  '424409' : 'sd5',
  '418193' : 'sd5',
  '425596' : 'sd5',
  '425599' : 'sd5',
  '432104' : 'sd5',
  '432105' : 'sd5',
  '432106' : 'sd5',
  '429852' : 'sd5',
  '429863' : 'sd5',
  '430329' : 'sd5',
  '430994' : 'sd5',
  '425594' : 'sd5',
  '425597' : 'sd5',
  '430994' : 'sd5',
  '430993' : 'sd5',
  '432512' : 'sd5',
  '432510' : 'sd5',
  '433891' : 'sd5',
  '433468' : 'sd5',
  '429857' : 'sd5',
  '430993' : 'sd5',
  '434845' : 'sd5',
  '434494' : 'sd5',
  '433874' : 'sd5',
  '429860' : 'sd5',
  '434843' : 'sd5',
  '429860' : 'sd5',
  '434497' : 'sd5',
  '434488' : 'sd5',
  '433874' : 'sd5',
  '437660' : 'sd5',
  '437661' : 'sd5',
  '434836' : 'sd5',
  '448505' : 'sd5',
  
  '448506' : 'sd5',
  '438844' : 'sd5',
  '437929' : 'sd5',
  '438843' : 'sd5',
  '448503' : 'sd5.2',
  '448504' : 'sd5.2',
  '439183' : 'sd5.2',
  '441121' : 'sd5.2',
  '448502' : 'sd5.2',
  '438841' : 'sd5.2',
  '441118' : 'sd5.2',
  '441119' : 'sd5.2',
  '443087' : 'sd5.2',
  '443086' : 'sd5.2',
  '443085' : 'sd5.2',
  '443956' : 'sd5.2',
  '443954' : 'sd5.2',
  '442905' : 'sd5.2',
  '443290' : 'sd5.2',
  '443953' : 'sd5.2',
  '444384' : 'sd5.2',
  '447720' : 'sd5.2',
  '447716' : 'sd5.2'
}
  

for mouse in mice.keys():

    remote_directory = '/mnt/' + mice[mouse] #create_samba_directory(mice[mouse][:3] + '.local', mice[mouse])

    mouse_directory = glob.glob(os.path.join(remote_directory, '*' + mouse + '*'))[0]

    probe_directories = glob.glob(os.path.join(mouse_directory, '*' + '_sorted'))

    npx_files = []

    for idx, directory in enumerate(probe_directories):
        npx_files.append(os.path.join(directory[:-7], 'recording1.npx'))

    json_directory = '/mnt/md0/data/json_files'

    process_dict = [ ]

    for npx_file in npx_files:

        print(npx_file)

        probe_directory = glob.glob(os.path.join(os.path.dirname(npx_file) + '_sorted','continuous','Neuropix*100.0'))[0]
        session_id = os.path.basename(probe_directory)

        input_json = os.path.join(json_directory, session_id + '-input.json')
        output_json = os.path.join(json_directory, session_id + '-output.json')

        info = createInputJson(None, probe_directory, input_json)

        new_metrics_file = info['quality_metrics_params']['quality_metrics_output_file']

        if not os.path.exists(new_metrics_file):
            
            print('Processing ' + npx_file)

            commands = ['quality_metrics']

            for command in commands:

                command = "python -m ecephys_spike_sorting.modules." + command + " --input_json " + input_json \
                      + " --output_json " + output_json

                subprocess.check_call(command.split(' '))


