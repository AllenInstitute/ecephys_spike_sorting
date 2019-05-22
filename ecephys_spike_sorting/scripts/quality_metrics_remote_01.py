import os
import shutil
import glob
import subprocess
import time

from functools import reduce

from create_input_json import createInputJson, create_samba_directory

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
  '404554' :  'sd4'
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
    


