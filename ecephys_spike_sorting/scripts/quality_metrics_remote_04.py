import os
import shutil
import glob
import subprocess
import time

from functools import reduce

from create_input_json import createInputJson, create_samba_directory


mice = { \
  
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
  '448505' : 'sd5'
}

  
for mouse in mice.keys():

    #try:
      remote_directory = create_samba_directory(mice[mouse][:3], mice[mouse])

      print(remote_directory)

      mouse_directory = glob.glob(os.path.join(remote_directory, '*' + mouse + '*'))[0]

      probe_directories = glob.glob(os.path.join(mouse_directory, '*' + '_sorted'))

      npx_files = []

      for idx, directory in enumerate(probe_directories):
          npx_files.append(os.path.join(directory[:-7], 'recording1.npx'))

      json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

      process_dict = [ ]

      for npx_file in npx_files:

          print(npx_file)

          probe_directory = os.path.dirname(npx_file)
          session_id = os.path.basename(probe_directory)

          input_json = os.path.join(json_directory, session_id + '-input.json')
          output_json = os.path.join(json_directory, session_id + '-output.json')

          info = createInputJson(probe_directory, input_json)

          if not os.path.exists(info['quality_metrics_params']['quality_metrics_output_file']):

              commands = ['quality_metrics']

              for command in commands:

                  command = "python -m ecephys_spike_sorting.modules." + command + " --input_json " + input_json \
                        + " --output_json " + output_json

                  os.system(command)
          else:
            print("New metrics already computed")

    #except:
    #  print("Failure for mouse " + mouse)
    


