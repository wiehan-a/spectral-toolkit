'''
Created on Sep 16, 2013

@author: Wiehan
'''

from PySide.QtGui import *
from PySide.QtCore import *
import sys, os
from gui.downloader.downloader import Downloader
from gui.library.libraryview import Library

qt_app = QApplication(sys.argv)

app = Library()
app.run()
qt_app.exec_()