from cleanup.check_data_processing import postprocessing



import subprocess
import shutil
import os
import time
import psutil
from pprint import pprint
from collections import namedtuple
import glob
import datetime
import psutil

npx_params = namedtuple('npx_params',['backup_location','start_module','end_module'])

backup_drive = r'E:'
default_start = 'copy_raw_data'
default_end = 'copy_processed_data'

network_location = r"\\sd4\SD4"

npx_directories = {r'F:\testA_758798717_406805_20180926_probeC':npx_params(backup_drive,default_start,default_end),
					#r'K:\757216464_412794_20180924_probeE':npx_params(backup_drive,default_start,default_end),
					#r'L:\757216464_412794_20180924_probeF':npx_params(backup_drive,default_start,default_end)
					}
					
postprocessing(npx_directories)