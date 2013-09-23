'''
Created on Sep 23, 2013

@author: Wiehan
'''
import sys

from PySide.QtCore import *
from PySide.QtGui import *
from gui.library.librarymodel import LibraryModel

class Library(QWidget):
    
    widget_stack = []
    
    def __init__(self):

        QWidget.__init__(self)
        self.setWindowTitle('Spectral Toolkit (Data library)')
        self.setMinimumWidth(500)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        
        self.table = QTableView()
        self.table.setModel(LibraryModel())
        self.main_vbox.addWidget(self.table)
        
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
    def run(self):
        self.show()
        

if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    app = Library()
    app.run()
    qt_app.exec_()