

import subprocess
import sys


session_name = '1055415082_533539_20201008'#test_2019-07-25_18-16-48' #Fill in with appropriate session name

if __name__ == '__main__':
  try:
    session_name = sys.argv[1]
  except exception as E:
    print('No arguments found in sys call, using session name from py file instead')
  command_string_1 = r"python C:\Users\svc_neuropix\Documents\GitHub\ecephys_spike_sorting\ecephys_spike_sorting\scripts\cortex_from_extraction.py "+session_name
  subprocess.check_output(command_string_1)

  command_string_2 = r"python C:\Users\svc_neuropix\Documents\GitHub\ecephys_spike_sorting\ecephys_spike_sorting\scripts\full_from_kilosort.py "+session_name
  subprocess.check_output(command_string_2)


