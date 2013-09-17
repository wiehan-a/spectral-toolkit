'''
Created on Sep 11, 2013

@author: Wiehan
'''
from PySide.QtCore import *
from PySide.QtGui import *
import sys, time, os, utils

from gui import *
from gui.downloader import *
from gui.downloader.downloadconfirmwidget import *
from gui.downloader.dataselectorwidgets import *
from gui.stdateedit import *


class Downloader(QWidget):
    
    widget_stack = []
    
    def __init__(self):

        QWidget.__init__(self)
        self.setWindowTitle('Spectral Toolkit (Data selection)')
        self.setMinimumWidth(500)
        
        self.stages = ['Data selection/downloading',
                       'Confirm download',
                       'Download']
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.header_title_label = QLabel()
        self.main_vbox.addWidget(self.header_title_label)
        self.hosted_vbox = QVBoxLayout()
        self.main_vbox.addLayout(self.hosted_vbox)
        self.hosted_widget = DataSelectorWidget()
        self.header_title_label.setText(self.hosted_widget.title)
        self.widget_stack.append(self.hosted_widget)
        self.hosted_vbox.addWidget(self.hosted_widget)
        
        self.main_vbox.addStretch()
        
        self.action_bar_hbox = QHBoxLayout()
        self.main_vbox.addLayout(self.action_bar_hbox)
        
        self.update_action_bar()
        
        self.setLayout(self.main_vbox)
        
    def update_action_bar(self):
        child = self.action_bar_hbox.takeAt(0)
        
        while child is not None:
            
            if hasattr(child, 'widget'):
                if child.widget() is not None:
                    child.widget().deleteLater()
            self.action_bar_hbox.removeItem(child)
            child = self.action_bar_hbox.takeAt(0)        
        
        if hasattr(self.hosted_widget, 'get_actions'):
            buttons = self.hosted_widget.get_actions(self)
            for b in buttons['left']:
                self.action_bar_hbox.addWidget(b)
            self.action_bar_hbox.addStretch()
            for b in buttons['right']:
                self.action_bar_hbox.addWidget(b)
                
    def switch_in_new_hosted_widget(self, widget, forward=True):
        self.header_title_label.setText(widget.title)
        
        self.hosted_widget.setVisible(False)
        self.hosted_vbox.removeWidget(self.hosted_widget)
        self.hosted_widget = widget
        self.hosted_vbox.addWidget(self.hosted_widget)
        self.hosted_widget.setVisible(True)
        self.update_action_bar()
        
        if forward:
            self.widget_stack.append(self.hosted_widget)
        
    @Slot()
    def data_select_slot(self):
        
        idx = self.hosted_widget.sources_combo.currentIndex()
        self.parameters = {}
        self.hosted_widget.data_selector_widget.annotateParams(self.parameters)
        
        if idx != 2:
            self.parameters['source'] = self.hosted_widget.sources[idx].split(' ')[0]
            self.switch_in_new_hosted_widget(DownloadConfirmWidget(self.parameters))
        else:
            print 'file'
    
    @Slot()
    def go_back(self):
        print 'Go back'
        self.widget_stack.pop()
        self.switch_in_new_hosted_widget(self.widget_stack[-1], forward=False)

    @Slot()
    def download_confirm_slot(self):
        self.switch_in_new_hosted_widget(DownloaderWidget(self.parameters, self))
    
    @Slot()
    def done_slot(self):
        self.switch_in_new_hosted_widget(DownloadDoneWidget(self.parameters))
        self.main_vbox.setStretchFactor(self.hosted_widget, 2)
        self.hosted_widget.download_more_button.clicked.connect(self.go_download_more_slot)
        
    @Slot()
    def go_download_more_slot(self):
        self.switch_in_new_hosted_widget(DataSelectorWidget(), forward=False)
    
    def run(self):
        self.show()

class DownloadDoneWidget(QWidget):
    
    title = "<h3>Downloading has completed successfully</h3>"
    
    
    def __init__(self, params):
        QWidget.__init__(self)
        
        self.params = params
        
        self.main_hbox = QHBoxLayout(self)
        self.main_hbox.setAlignment(Qt.AlignHCenter)
        
        self.main_vbox = QVBoxLayout()
        self.main_hbox.addLayout(self.main_vbox)
        self.main_vbox.setAlignment(Qt.AlignHCenter)
        
        self.exit_button = QPushButton('Exit')
        self.open_folder_button = QPushButton('Open download folder')
        self.download_more_button = QPushButton('Download more data')
        self.go_home_button = QPushButton('Spectral Toolkit (Main)')
        
        self.main_vbox.addWidget(self.download_more_button)
        self.main_vbox.addWidget(self.open_folder_button)
        self.main_vbox.addWidget(self.go_home_button)
        self.main_vbox.addWidget(self.exit_button)
        
        self.open_folder_button.clicked.connect(self.open_folder_slot)
        self.exit_button.clicked.connect(sys.exit)
        
    @Slot()
    def open_folder_slot(self):
        path = QDir.toNativeSeparators(os.path.abspath(os.path.dirname(sys.argv[0]))+'/Downloaded Data/')
        print QDesktopServices.openUrl(QUrl('file:///'+path))
        
            
        
class DownloaderWidget(QWidget):
    
    title = "<h3>Step 3: Downloading</h3>"
    
    
    def __init__(self, params, parent_):
        QWidget.__init__(self)
        
        self.params = params
        self.parent_ = parent_
        
        self.file_count = lsbb.get_number_of_files(params)
        self.file_size = lsbb.get_single_file_size(params)
        self.overall_size = lsbb.calculate_size(params)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        
        self.current_progress_label = QLabel()
        
        self.main_vbox.addWidget(self.current_progress_label)
        
        self.current_progress_bar = QProgressBar()
        self.current_progress_bar.setMinimum(0)
        self.current_progress_bar.setMaximum(self.file_size)
        self.current_progress_bar.setTextVisible(True)
        self.main_vbox.addWidget(self.current_progress_bar)
        
        self.overall_progress_label = QLabel()
        self.main_vbox.addWidget(self.overall_progress_label)
        
        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setTextVisible(True)
        self.overall_progress_bar.setMinimum(0)
        self.overall_progress_bar.setMaximum(self.overall_size)
        self.main_vbox.addWidget(self.overall_progress_bar)
        
        self.update_progress({'cur_file_number':'1',
                              'cur_downloaded':'0MB',
                              'overall_downloaded':'0MB',
                              'cur_file_bytes': 0, 
                              'overall_bytes': 0})
        
        self.worker = lsbb.DownloaderWorker(self.params)
        self.wthread = QThread()
        self.worker.moveToThread(self.wthread)
        self.worker.progress_update.connect(self.update_progress)
        self.wthread.started.connect(self.worker.start_downloading)
        self.worker.done.connect(self.wthread.quit)
        self.worker.done.connect(self.parent_.done_slot)
        self.wthread.start()
        
        
    def get_actions(self, parent):
        
        back = QPushButton('Back')
        back.clicked.connect(parent.go_back)
        
        cancel = QPushButton('Cancel')
        # download.clicked.connect(parent.download_confirm_slot)
        
        buttons = {'left' : [],
                   'right' : [cancel]}
        
        return buttons
    
    @Slot(dict)
    def update_progress(self, kwparams):
        
        kwparams['overall_file_size'] = utils.sizeof_fmt(self.file_size)
        kwparams['file_count'] = str(self.file_count)
        kwparams['overall_size'] = utils.sizeof_fmt(self.overall_size)
        
        
        self.current_progress_label.setText('Current file (' + kwparams['cur_file_number'] + ' of ' + 
                                            kwparams['file_count'] + '): ' + kwparams['cur_downloaded'] + 
                                            ' of ' + kwparams['overall_file_size'] + ' downloaded')
        self.current_progress_bar.setValue(kwparams['cur_file_bytes'])
        
        self.overall_progress_label.setText('Overall progress: ' + kwparams['overall_downloaded'] + ' of ' + 
                                             kwparams['overall_size'] + ' downloaded')
        self.overall_progress_bar.setValue(kwparams['overall_bytes'])
        

        
 

