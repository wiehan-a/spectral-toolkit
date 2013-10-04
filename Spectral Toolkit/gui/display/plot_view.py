'''
Created on Oct 3, 2013

@author: Wiehan
'''

import sys
# import matplotlib
# matplotlib.use('Qt4Agg')
# matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np

from PySide.QtCore import *
from PySide.QtGui import *

class Plotter(QWidget):
    
    closed = Signal(QObject)
    
    def __init__(self, x, y):
        QWidget.__init__(self)
        
        self.setWindowTitle('Spectral Toolkit (Figure)')
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        ax = self.figure.add_subplot(111)
        if x is not None:
            ax.plot(x, y)
        else:
            ax.plot(y)
        self.figure.autofmt_xdate()
        self.canvas.draw()

        # set the layout
        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(self.toolbar)
        self.main_vbox.addWidget(self.canvas)
        self.setLayout(self.main_vbox)
        
        self.show()
        
    def closeEvent(self, *args, **kwargs):
        print 'Plot closed'
        self.closed.emit(self)
        self.closed = None
        self.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Plotter(np.arange(10), np.arange(10))
    sys.exit(app.exec_())