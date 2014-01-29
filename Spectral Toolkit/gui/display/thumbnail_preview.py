'''
Created on Jan 24, 2014

@author: Wiehan
'''

import sys, os
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np

from PySide.QtCore import *
from PySide.QtGui import *

class ThumbnailPlotter(QWidget):
    
    def __init__(self, title="Time domain preview"):
        QWidget.__init__(self)
      
        plt.close() 
        plt.clf()
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.figure.patch.set_facecolor('none')

        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0, right=0.99, top=0.99, bottom=0.01)

        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(QLabel("<h3>"+title+"</h3>"))
        self.main_vbox.addWidget(self.canvas)
        self.canvas.setVisible(False)
        self.setLayout(self.main_vbox)
        
        self.movie = QMovie("ajax-loader.gif")
        self.process_label = QLabel()
        self.process_label.setMovie(self.movie)
        self.movie.start()
        
        self.main_hbox = QHBoxLayout()
        self.main_vbox.addLayout(self.main_hbox)
        self.main_hbox.addStretch()
        self.main_hbox.addWidget(self.process_label)
        self.main_hbox.addStretch()
        self.process_label.setVisible(False)
        
        self.sizepolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(self.sizepolicy)
        
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.setLoading()
        
    def setLoading(self):
        self.canvas.setVisible(False)
        self.process_label.setVisible(True)
    
    def draw(self, y):
        self.canvas.setVisible(True)
        self.process_label.setVisible(False)
        self.ax.clear()
        self.ax.plot(y)
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.canvas.draw()
        
    def sizeHint(self, *args, **kwargs):
        return QSize(100, 150)