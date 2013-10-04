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
from gui.spectral_conf.spectral_conf import SpectralConf

from config import *
from gui.display.plot_td import *

class Library(QWidget):
    
    plots = []
    estimation_windows = []
    
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
        verthead = self.table.verticalHeader()
        verthead.setDefaultSectionSize(verthead.fontMetrics().height()+4)
         
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.action_bar_hbox = QHBoxLayout()
        self.left_vbox.addLayout(self.action_bar_hbox)
#         self.import_file_button = QPushButton('Import from file')
#         self.action_bar_hbox.addWidget(self.import_file_button)
        self.download_more_button = QPushButton('Download more')
        self.download_more_button.clicked.connect(self.download_more_slot)
        self.action_bar_hbox.addWidget(self.download_more_button)
        self.action_bar_hbox.addStretch()
#         self.analyze_button = QPushButton('Perform spectral analysis')
#         self.action_bar_hbox.addWidget(self.analyze_button)
        
        self.filter_widget = LibraryFilterWidget(self.table_model)
        self.right_vbox.addWidget(self.filter_widget)
        
        self.main_hbox.setStretchFactor(self.left_vbox, 2)
        
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.tableContextMenu)
        
    @Slot(QPoint)
    def tableContextMenu(self, point):
        menu = QMenu()
        self.display_td_action = QAction('Display time domain', self)
        self.display_td_action.triggered.connect(self.display_td_slot)
        
        self.spec_est_action = QAction('Spectral estimation', self)
        self.spec_est_action.triggered.connect(self.spectral_estimation_slot)
        
        menu.addAction(self.display_td_action)
        menu.addSeparator()
#         menu.addAction('Downsample')
        menu.addAction('Discontinuity tool')
#         menu.addAction('Spectral normalisation')
        menu.addAction(self.spec_est_action)
        menu.addSeparator()
        menu.addAction('Export to MATLAB')
        menu.addAction('Export to Python/Numpy')
        menu.addSeparator()
        menu.addAction('Delete')
        menu.exec_(QCursor.pos())
        
    def validate_selection(self, files):
        if len(files) > 1:
            sources = set([db[f]['source'] for f in files])
            
            if len(sources) > 1:
                raise MultipleSourcesException()
            
            components = set([db[f]['component'] for f in files])
            
            if len(components) > 1:
                raise MultipleComponentsException()
            
            files = sorted(files, key=lambda f: db[f]['start_time'])
            
            for idx in xrange(len(files) - 1):
                if db[files[idx + 1]]['start_time'] - db[files[idx]]['end_time'] > timedelta(seconds=1):
                    raise NotContiguousException()
        
    
    @Slot()
    def display_td_slot(self):
        print 'displaying td plot'
        rows = list(set([qmi.row() for qmi in self.table.selectedIndexes()]))
        files = [self.table_model.filtered_list[r][0] for r in rows]
        
        try:
            self.validate_selection(files)
            worker = ShowTDWorker(files)
            worker.show_td()
            self.plots.append(worker)
        except NotContiguousException:
            msgBox = QMessageBox()
            msgBox.setText("Only a selection of temporally contiguous files supported.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
        except MultipleComponentsException:
            msgBox = QMessageBox();
            msgBox.setText("Only a single component can be plotted at one time.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
        except MultipleSourcesException:
            msgBox = QMessageBox()
            msgBox.setText("Please do not select data from multiple sources.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
        
        
    @Slot()
    def spectral_estimation_slot(self):
        print 'spectral estimation'
        rows = list(set([qmi.row() for qmi in self.table.selectedIndexes()]))
        files = [self.table_model.filtered_list[r][0] for r in rows]
        
        try:
            self.validate_selection(files)
            estimation_window = SpectralConf(files)
            estimation_window.show()
            self.estimation_windows.append(estimation_window)
        except NotContiguousException:
            msgBox = QMessageBox()
            msgBox.setText("Only a selection of temporally contiguous files supported.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
        except MultipleComponentsException:
            msgBox = QMessageBox();
            msgBox.setText("Only a single component can be plotted at one time.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
        except MultipleSourcesException:
            msgBox = QMessageBox()
            msgBox.setText("Please do not select data from multiple sources.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
        
        
    @Slot()
    def download_more_slot(self):
        self.downloader = Downloader()
        self.downloader.run()
        self.downloader.finished_downloading_signal.connect(self.table_model.refreshModel)
        
        
    def run(self):
        self.show()
        
class MultipleSourcesException(Exception):
    pass

class MultipleComponentsException(Exception):
    pass

class NotContiguousException(Exception):
    pass
        

if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    app = Library()
    app.run()
    qt_app.exec_()