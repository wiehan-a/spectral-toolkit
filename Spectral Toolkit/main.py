'''
Created on Sep 16, 2013

@author: Wiehan
'''

from PySide.QtGui import *
from PySide.QtCore import *
import sys, os
from gui.downloader.downloader import Downloader

qt_app = QApplication(sys.argv)

app = Downloader()
app.run()
qt_app.exec_()