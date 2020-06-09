from helpers.check_data_processing import check_data_processing                
import os


drives_to_clean = ['H:', 'I:', 'J:']

probe_type = 'PXI'
raw_path = 'none'

backup_list = [
		r'\\10.128.50.43\sd6',
		r'\\10.128.50.43\sd6.2'
	]

def find_sorted_backup(session):
	for location in backup_list:
		for directory in os.listdir(location):
			if session in directory:
				return os.path.join(location, directory) 

def get_session(dir_name):
	return dir_name.split('_')[0]

def cleanup_drives():
	for drive in drives_to_clean:
		for directory in os.listdir(drive):
			if 'sorted' in directory:
				sorted_path = os.path.join(drive, directory)
				session_id = get_session(directory)
				session_backup = find_sorted_backup(session_id)
				unsorted_name = directory[0:32]
				unsorted_raw_mock = os.path.join('A:', unsorted_name)
				onsorted_backup_modk = os.path.join('B:', unsorted_name)
				if session_backup is None:
					print('failed to find backup for {}'.format(sorted_path))
				else:
					sorted_backup = os.path.join(session_backup, directory)
					print('Attemting to cleaup {} with backup {}'.format(sorted_path, sorted_backup))
					dir_sucess = check_data_processing(probe_type, unsorted_raw_mock, sorted_path, onsorted_backup_modk, onsorted_backup_modk, sorted_backup, sorted_backup)


if __name__ == '__main__':
	cleanup_drives()