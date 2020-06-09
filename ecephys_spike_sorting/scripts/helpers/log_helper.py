#dummy output generator to test logging and piping

import logging
import datetime
import subprocess
import os
import time
import sys
import multiprocessing

logging.basicConfig(level = logging.DEBUG)


logger = logging.getLogger(__name__)

file_name1 = 'all_'+datetime.datetime.now().strftime("%y.%m.%d.%I.%M.%S")+".log"
log_file1 = os.path.join(r'C:\Users\svc_neuropix\Documents\log_files',file_name1)
file_name2 = 'err_'+datetime.datetime.now().strftime("%y.%m.%d")+".log"
log_file2 = os.path.join(r'C:\Users\svc_neuropix\Documents\log_files',file_name2)
file_handler1 = logging.FileHandler(log_file1)
file_handler2 = logging.FileHandler(log_file2)

file_handler1.setLevel(logging.DEBUG)
file_handler2.setLevel(logging.ERROR)

file1_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file2_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler1.setFormatter(file1_format)
file_handler2.setFormatter(file2_format)

logger.addHandler(file_handler1)
logger.addHandler(file_handler2)




"""
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("logfile.log", "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    

sys.stdout = Logger()
"""
def my_readline(pout, send_end):
	line = pout.readline()
	print('line',line)
	send_end.send(line)

def worker(procnum, send_end):
    '''worker function'''
    result = str(procnum) + ' represent!'
    print(result)
    send_end.send(result)
	
def readline_timeout(process_in): #Try passing proc.
	recv_end, send_end = multiprocessing.Pipe(False)
	p = multiprocessing.Process(target = my_readline, args=(process_in.stdout,send_end))
	p.start()
	p.join(100)
	line = recv_end.recv()
	return line

def log_out(p):
	p.stdout.seek(0,2)
	pos = p.stdout.tell()
	if pos:
		tot_read = 0
		while tot_read < pos:
			line = p.stdout.readline()
			tot_read = tot_read +len(line)
			print(line.rstrip())
	time.sleep(3)

def log_err(p):
	start =  datetime.datetime.now()
	line = p.stderr.readline()
	while line:
		print(line.rstrip())
			#print('reading line')
		line = p.stderr.readline()

#log_out_final()

def main():
	key = 1
	count = 1
	print('initiating process for ',key,' count = ',count)
	p = subprocess.Popen(['python','fake_utility.py'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	time.sleep(3)
	while True:
		#print('nothing1?')
		#log_out(p)
		#print('nothing?')
		#with open(p.stdout ,'r') as file:
	#		print(file)
		#print(p.stdout.readline())
		log_out(p)

"""
	list = [0,1,2,3,4,5,6,7,8,9,10]
	repeat = ['one','two']
	finished = [0,0]
	process_dict = {}
	for key in repeat:
		process_dict[key] = []

	count = 0
	while sum(finished)<1:
		count = count+1
		for idx,key in enumerate(process_dict):
			#time.sleep(2)
			busy = False
			print('busy',datetime.datetime.now())
			for p in process_dict[key]:
				if p.poll() is None:
					busy = True
			print('attempting to print output for ',key,' count = ',count)
			try:
				p = process_dict[key][-1]
				#log_err(p)
				log_out(p)
				#line = p.stdout.readline()

					#print(now)
				#if p.poll is not None:
			#		print('full output:')
		#			output,error = p.communicate()
	#				sys.stdout.write(output)

			except Exception as E:
				logging.exception(E)

			if not(busy):
				print('initiating process for ',key,' count = ',count)
				process_dict[key].append(subprocess.Popen(['python','fake_utility.py'],stdout = subprocess.PIPE, stderr = subprocess.PIPE))
"""
if __name__ == "__main__":
	main()
