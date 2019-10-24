import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QFileDialog
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtGui import QIcon, QKeyEvent
from PyQt5.QtCore import pyqtSlot, Qt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib

import numpy as np
import pandas as pd

import os

matplotlib.use('QT5Agg')

mapping = {
            Qt.Key_O : (1, 'one channel', 'red'),
            Qt.Key_X : (2, 'symmetric multiple spikes', 'orange'),
            Qt.Key_Z : (3, 'symmetric one spike', 'magenta'),
            Qt.Key_A : (4, 'asymmetric, non-propagating', 'darkgreen'),
            Qt.Key_D : (5, 'divided', 'brown'),
            Qt.Key_M : (6, 'multi-spike', 'teal'),
            Qt.Key_W : (7, 'multiple sharp peaks', 'green'),
            Qt.Key_S : (8, 'single channel spike', 'turquoise'),
            Qt.Key_U : (9, 'upward spike', 'pink'),
            Qt.Key_C : (10, 'trough in corner', 'maroon'),
            Qt.Key_P : (11, 'propagating', 'tan'),
            Qt.Key_F : (12, 'weird spike', 'aqua'),
            Qt.Key_Q : (13, 'other', 'gray'),
            Qt.Key_V : (14, 'vertical', 'purple'),
            Qt.Key_G : (0, 'good', 'black')
        }

def get_colors(ratings):

    colors = []
    for r in ratings:
        for k in mapping.keys():
            if mapping[k][1] == r:
                colors.append(mapping[k][2])

    return colors


def get_channel_location(channel, is3b = False):

    """
    Returns physical location (in microns) of a Neuropixels channel, 
    relative to the probe tip.
    
    Parameters:
    -----------
    channel - int
        channel number (0-383)
    
    Returns:
    --------
    location - tuple
        (xpos, ypos) in microns
    isReference - bool
        True if channel is a reference, False otherwise
    
    """

    xlocations = [16, 48, 0, 32]
    
    try:
        if is3b:
            [36, 75, 112, 151, 188, 227, 264, 303, 340, 379].index(channel)
        else:
            [191].index(channel)
        isReference = True
    except ValueError:
        isReference = False
    
    return (xlocations[channel%4], np.floor(channel/2)*20), isReference


class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(131)
        self.ax2 = self.fig.add_subplot(132)
        self.ax3 = self.fig.add_subplot(133)
        Canvas.__init__(self, self.fig)
        Canvas.updateGeometry(self)

class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
        self.canvas = MplCanvas()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Template Rating'
        self.left = 200
        self.top = 200
        self.width = 1520
        self.height = 800
        self.initUI()
     
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        grid = QGridLayout()
    
        self.canvas = MplCanvas()
        grid.setSpacing(10)
        grid.addWidget(self.canvas,0,0,5,8)

        forward_button = QPushButton('>>>', self)
        forward_button.setToolTip('Go to next unit')
        grid.addWidget(forward_button,6,8)
        forward_button.clicked.connect(self.move_forward)

        back_button = QPushButton('<<<', self)
        back_button.setToolTip('Go to previous unit')
        grid.addWidget(back_button,6,7)
        back_button.clicked.connect(self.move_back)

        #label_button = QPushButton('Change label', self)
        #label_button.setToolTip('Switch from good to noise or vice versa')
        #grid.addWidget(label_button,6,6)
        #label_button.clicked.connect(self.change_label)

        save_button = QPushButton('Save', self)
        save_button.setToolTip('Save ratings as CSV')
        grid.addWidget(save_button,6,5)
        save_button.clicked.connect(self.save_data)

        load_button = QPushButton('Load', self)
        load_button.setToolTip('Load data directory')
        grid.addWidget(load_button,6,4)
        load_button.clicked.connect(self.load_data)

        self.category_key = Qt.Key_G

        self.unit_idx = 0
        self.current_directory = '/mnt/sd5.3/RE-SORT'

        self.data_loaded = False

        self.setLayout(grid)
        self.show()

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Comma:
            self.move_back()
        elif e.key() == Qt.Key_Period:
            self.move_forward()
        elif e.key() in mapping:
            self.change_label(e.key())

    def move_forward(self):
        if self.data_loaded:
            self.unit_idx = np.min([self.unit_idx + 1, len(self.unit_list)-1])
            
            self.plot_data()

    def move_back(self):
        if self.data_loaded:
            
            self.unit_idx = np.max([self.unit_idx - 1, 0])
            
            self.plot_data()
     
    def change_label(self, category=None):
        
        if self.data_loaded:
            
            self.category_key = category
            
            self.ratings[self.unit_idx] = mapping[self.category_key][1]
            self.colors[self.unit_idx] = mapping[self.category_key][2]

            self.save_data()
            
            self.plot_data()

    def save_data(self):
        
        if self.data_loaded:
            df = pd.DataFrame(data = {'cluster_id' : self.unit_list, 'rating' : self.ratings})
            df.to_csv(self.output_file, index=False)

    def load_data(self):
        fname = QFileDialog.getExistingDirectory(self, 'Select data directory', self.current_directory)
        
        if len(fname) > 0: 
            if os.path.exists(os.path.join(fname, 'spike_times.npy')):
                self.spike_times = np.load(os.path.join(fname, 'spike_times.npy'))
                self.spike_clusters = np.load(os.path.join(fname, 'spike_clusters.npy'))

                templates = np.load(os.path.join(fname, 'templates.npy'))
                whitening_mat_inv = np.load(os.path.join(fname, 'whitening_mat_inv.npy'))
                self.channel_map = np.load(os.path.join(fname, 'channel_map.npy'))

                self.templates = np.zeros(templates.shape)

                self.unit_list = np.unique(self.spike_clusters)

                for unit in self.unit_list:
                    template = templates[unit,:,:]
                    self.templates[unit,:,:] = np.dot(np.ascontiguousarray(template),np.ascontiguousarray(whitening_mat_inv))

                self.output_file = os.path.join(fname, 'template_ratings_new.csv')

                if os.path.exists(self.output_file):
                    info = pd.read_csv(self.output_file)
                    self.ratings = info['rating']
                    self.colors = get_colors(self.ratings)
                else:
                    self.ratings = ['good'] * len(self.unit_list)
                    self.colors = ['black'] * len(self.unit_list)

                self.peak_channels = np.argmin(np.min(self.templates,1),1)

                self.data_loaded = True
                self.unit_idx = 0

                self.setWindowTitle(fname)
                self.current_directory = fname
                
                if self.current_directory.find('PXI') > -1:
                    self.phase3b = True

                self.plot_data()


    def plot_data(self):

        self.canvas.ax1.clear()

        peak_channel = self.peak_channels[self.unit_idx]

        min_chan = np.max([0,peak_channel-16])
        if min_chan == 0:
            max_chan = 32

        max_chan = np.min([self.templates.shape[2], peak_channel+16])
        if max_chan == self.templates.shape[2]:
            min_chan = max_chan - 32

        sub_template = self.templates[self.unit_idx, 21:, min_chan:max_chan]

        self.canvas.ax1.imshow(sub_template.T, origin='lower', aspect='auto', vmin=-10, vmax=10)
        self.canvas.ax1.set_axis_off()

        self.canvas.ax2.clear()
        for ch in range(sub_template.shape[1]):
            data = sub_template[:,ch]
            actual_ch = int(self.channel_map[ch + min_chan])
            loc, isRef = get_channel_location(actual_ch)

            x_values = np.linspace(0,10,len(data)) + loc[0]
            y_values = data * 2.5 + loc[1]
            
            self.canvas.ax2.plot(x_values, y_values, color=self.colors[self.unit_idx])

        self.canvas.ax2.set_axis_off()
        if self.unit_idx == len(self.unit_list) - 1:
            self.canvas.ax2.set_title('END')
        else:
            self.canvas.ax2.set_title(str(self.unit_idx))

        self.canvas.ax3.clear()
        for_unit = self.spike_clusters == self.unit_idx
        spike_times = self.spike_times[for_unit] / 30000.
        h,b = np.histogram(np.diff(spike_times), bins=np.linspace(0,0.1,100))
        self.canvas.ax3.bar(b[:-1],h,width=0.0015)
        self.canvas.ax3.set_ylim([-np.max(h), np.max(h)*2])
        self.canvas.ax3.set_axis_off()

        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

