import shutil
import os

output_directory = os.path.join('C:\\data','test_directory')
output_directory_E = os.path.join('E:\\','test_directory')

shutil.move(output_directory, output_directory_E)