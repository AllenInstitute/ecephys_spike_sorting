import os
import shutil
import glob
import subprocess
import time

from functools import reduce

from create_input_json import createInputJson, create_samba_directory

mice = { \
  '405751' :  'sd4',
  '406807' :  'sd4',
  '412794' :  'sd4',
  '412793' :  'sd4',
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
} 


  
for mouse in mice.keys():

   # try:
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
   #   print("Failure for mouse " + mouse)
    


