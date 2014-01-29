'''
Created on Oct 3, 2013

@author: Wiehan
'''

import sys, os
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
    
    def __init__(self, x, y, annotations=None, x_unit=None, y_unit=None, component_labels=None, standalone=False):
        QWidget.__init__(self)
        
        self.setWindowTitle('Spectral Toolkit (Figure)')
        
        self.setWindowIcon(QIcon('icon.png'))
        if os.name == 'nt':
            # This is needed to display the app icon on the taskbar on Windows 7
            import ctypes
            myappid = 'MyOrganization.MyGui.1.0.0' # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        plt.close() 
        plt.clf()
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        ax = self.figure.add_subplot(111)
        if x is not None:
            if isinstance(y, list):
                for idx, signal in enumerate(y):
                    print "idx, signal:", idx, signal
                    if component_labels is not None and len(component_labels) == len(y):
                        ax.plot(x, signal, label=component_labels[idx])
                    else:
                        ax.plot(x, signal)
                ax.legend()
            else:
                ax.plot(x, y)
            if annotations is not None:
                for annot in annotations:
                    ax.axvspan(annot[0], annot[1], facecolor='g', alpha=0.5)
        else:
            ax.plot(y)
        self.figure.autofmt_xdate()
        
        if x_unit is not None:
            self.figure.gca().set_xlabel(x_unit)
            
        if y_unit is not None:
            self.figure.gca().set_ylabel(y_unit)
            
        self.canvas.draw()

        # set the layout
        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(self.toolbar)
        self.main_vbox.addWidget(self.canvas)
        self.setLayout(self.main_vbox)
        
        if standalone:
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