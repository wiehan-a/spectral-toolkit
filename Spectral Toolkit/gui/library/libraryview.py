'''
Created on Sep 23, 2013

@author: Wiehan
'''
import sys

from PySide.QtCore import *
from PySide.QtGui import *
from gui.library.librarymodel import LibraryModel
from gui.library.libraryfilter import LibraryFilterWidget
from gui.downloader.downloader import Downloader

class Library(QWidget):
    
    def __init__(self):

        QWidget.__init__(self)
        self.setWindowTitle('Spectral Toolkit (Data library)')
        self.setMinimumWidth(800)
        
        self.main_hbox = QHBoxLayout(self)
        self.main_hbox.setAlignment(Qt.AlignTop)
        
        self.left_vbox = QVBoxLayout()
        self.right_vbox = QVBoxLayout()
        self.main_hbox.addLayout(self.left_vbox)
        self.main_hbox.addLayout(self.right_vbox)
        
        self.table = QTableView()
        self.table_model = LibraryModel()
        self.table.setModel(self.table_model)
        self.left_vbox.addWidget(self.table)
        
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.action_bar_hbox = QHBoxLayout()
        self.left_vbox.addLayout(self.action_bar_hbox)
        self.import_file_button = QPushButton('Import from file')
        self.action_bar_hbox.addWidget(self.import_file_button)
        self.download_more_button = QPushButton('Download more')
        self.download_more_button.clicked.connect(self.download_more_slot)
        self.action_bar_hbox.addWidget(self.download_more_button)
        self.action_bar_hbox.addStretch()
        self.analyze_button = QPushButton('Perform spectral analysis')
        self.action_bar_hbox.addWidget(self.analyze_button)
        
        self.filter_widget = LibraryFilterWidget()
        self.right_vbox.addWidget(self.filter_widget)
        
        self.main_hbox.setStretchFactor(self.left_vbox, 2)
        
    @Slot()
    def download_more_slot(self):
        self.downloader = Downloader()
        self.downloader.run()
        self.downloader.finished_downloading_signal.connect(self.table_model.refreshModel)
        
        
    def run(self):
        self.show()
        

if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    app = Library()
    app.run()
    qt_app.exec_()