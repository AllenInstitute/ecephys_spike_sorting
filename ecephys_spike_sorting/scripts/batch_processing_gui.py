#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

from qtmodern import styles, windows
from qtpy import QtGui, QtCore
from qtpy.QtWidgets import *

import subprocess
import glob
import shutil
import os
import time
import psutil
from collections import namedtuple, OrderedDict
from pprint import pprint
from recordclass import recordclass
import datetime
import logging
from qtpy import QtGui, QtCore
import multiprocessing
import json
import xml.etree.ElementTree as ET

logging.basicConfig(level = logging.DEBUG)


from helpers.batch_processing_common import processing_session
#import helpers.processing as npxprocess
from create_input_json import createInputJson
from zro import RemoteObject, Proxy

class RemoteInterface(RemoteObject):
	def __init__(self, rep_port, parent):
		super(RemoteInterface, self).__init__(rep_port=rep_port)
		print('Opening Remote Interface on port: '+ str(rep_port))
		self.parent = parent

	def process_npx(self, session_name, probes = [], WSE_computer=None):
		print('Attempting to initiate processing from remote command')
		print('Probes = '+ str(probes))
		self.parent.set_session( session_name)
		#started = self.parent.start_processing(session_name, probes, WSE_computer=WSE_computer)
		#commenting out until we fix it to run the appropriate day
		return started

	def ping(self):
		print("its alive")       


class Processing_Agent(QWidget):
	def __init__(self):
		super(Processing_Agent, self).__init__()

		#logging.basicConfig(level=logging.DEBUG,
		#        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		#self.config = mpeconfig.source_configuration('neuropixels')

		self.interface = RemoteInterface(rep_port=1234, parent=self)
		print('Starting Remote Interface')

		self.interfaceTimer = QtCore.QTimer()
		self.interfaceTimer.timeout.connect(self._check_sock)
		self.interfaceTimer.start(100)

		self.smallFont = QtGui.QFont()
		self.smallFont.setPointSize(8)
		self.smallFont.setBold(False)

		self.bigFont = QtGui.QFont()
		self.bigFont.setPointSize(12)
		self.bigFont.setBold(False)

		self.vLayout = QVBoxLayout()

		self.header = QLabel()
		self.header.setFont(self.bigFont)
		self.header.setText('NPX Processing Agent')
		self.header.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.vLayout.addWidget(self.header)

		self.processing_layout = QGridLayout()

		self.sessoin_label = QLabel()
		self.sessoin_label = QLabel()
		self.sessoin_label.setFont(self.smallFont)
		self.sessoin_label.setText('Full session name:')
		self.sessoin_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.session_entry = QLineEdit()
		self.session_entry.setFont(self.smallFont)
		self.processing_layout.addWidget(self.sessoin_label, 1, 0)
		self.processing_layout.addWidget(self.session_entry, 1, 1)

		self.vLayout.addLayout(self.processing_layout)

		self.processButton = QPushButton("Process Data")
		self.processButton.setStyleSheet("color: #333; border: 2px solid #555; border-radius: 11px; padding: 5px;background: qradialgradient(cx: 0.3, cy: -0.4,fx: 0.3, fy: -0.4,radius: 1.35, stop: 0 #fff, stop: 1 #388E3C);min-width: 80px;font-size:15px;")
		self.processButton.clicked.connect(self.process_button_press)
		self.vLayout.addWidget(self.processButton)


		###############################################################

		self.setLayout(self.vLayout)

	def set_session(self, session_name):
		self.session_entry.setText(session_name)

	def process_button_press(self):
		session_name = self.session_entry.text()
		reply = QMessageBox.question(self, 'Message', "Are you sure you want to process npx with session name: "+session_name+"?", QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self.start_processing(session_name, ['A', 'B', 'C', 'D', 'E', 'F'])
		else:
			pass

	def closeEvent(self, event):
		reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)

		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

	def _check_sock(self):
		self.interface._check_rep()

   

#For testing session_name = 'data_test'
	def start_processing(self, session_name, probes, WSE_computer=None):
		print('checking readiness for '+session_name)
		started_processing = False
		try:
			processor = processing_session(session_name, probes, probe_type = 'PXI', WSE_computer=WSE_computer)
			#check_ready_for_processing(session_name, probes)
			print('Processing npx for '+session_name)
			#p = multiprocessing.Process(target=processor.start_processing, args=())
			#time.sleep(100)
			#p.start()
			processor.start_processing()
			started_processing = True
		except Exception as E:
			logging.exception('Failed to start processing')
		print('finished processing')
		return started_processing

				
def main():
	app = QApplication([])
	styles.dark(app)

	g = windows.ModernWindow(Processing_Agent())
	# g.resize(350,100)
	g.move(50,270)
	g.setWindowTitle('Neuropixels Surgery/Experiment Notes')
	g.show()
	app.exec_()
	
if __name__ == '__main__':
	main()