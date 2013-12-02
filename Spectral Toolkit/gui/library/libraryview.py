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
from gui.downloader.importer import Importer
from gui.spectral_conf.spectral_conf import SpectralConf

import gc, os


from config import *
from gui.display.plot_td import *
from gui.icons import *

from data_access import export_td


class Library(QMainWindow):
    
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Spectral Toolkit (Data library)')
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)
        self.setWindowIcon(QIcon('icon.png'))
        
        self.statusBar().showMessage('Ready')
        
        if os.name == 'nt':
            # This is needed to display the app icon on the taskbar on Windows 7
            import ctypes
            myappid = 'MyOrganization.MyGui.1.0.0'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        self.lib = LibraryCentralWidget(self)
        self.setCentralWidget(self.lib)
        
        self.init_menus()
        
    def init_menus(self):
        self.data_menu = self.menuBar().addMenu("&Data")
        self.download_action = QAction(app_icons['download'], "&Download data", self)
        self.download_action.triggered.connect(self.lib.download_more_slot)
        self.import_action = QAction(app_icons['import'], "&Import local data", self)
        self.import_action.triggered.connect(self.import_slot)
        self.invalidate_action = QAction(app_icons['add_event'], "&Add data invalid event", self)
        self.data_menu.addAction(self.download_action)
        self.data_menu.addAction(self.import_action)
        self.data_menu.addSeparator()
        self.data_menu.addAction(self.invalidate_action)
        
        self.overviews_menu = self.menuBar().addMenu("&Overviews")
        self.sansa_menu = self.overviews_menu.addMenu("&SANSA")
        self.lsbb_menu = self.overviews_menu.addMenu("&LSBB")
        
        self.help_menu = self.menuBar().addMenu("&Help")
        self.help_action = QAction(app_icons['help'], "&User guide", self)
        self.about_action = QAction("&About Spectral Toolkit", self)
        self.help_menu.addAction(self.help_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)
        
    @Slot()
    def import_slot(self):
        self.importer = Importer(self).run()
        
    def run(self):
        self.show()

class LibraryCentralWidget(QWidget):
    
    plots = []
    estimation_windows = []
    workers = []
    worker_threads = []
    
    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        
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
        verthead.setDefaultSectionSize(verthead.fontMetrics().height() + 4)
         
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
#         self.action_bar_hbox = QHBoxLayout()
#         self.left_vbox.addLayout(self.action_bar_hbox)
#         self.import_file_button = QPushButton('Import from file')
#         self.action_bar_hbox.addWidget(self.import_file_button)
#         self.download_more_button = QPushButton('Download more')
#         self.download_more_button.clicked.connect(self.download_more_slot)
#         self.action_bar_hbox.addWidget(self.download_more_button)
#         self.action_bar_hbox.addStretch()
#         self.analyze_button = QPushButton('Perform spectral analysis')
#         self.action_bar_hbox.addWidget(self.analyze_button)
        
        self.filter_widget = LibraryFilterWidget(self.table_model)
        self.right_vbox.addWidget(self.filter_widget)
        
        self.main_hbox.setStretchFactor(self.left_vbox, 2)
        
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.tableContextMenu)
        
    @Slot(QPoint)
    def tableContextMenu(self, point):
        menu = QMenu(self)
        self.display_td_action = QAction(app_icons['graph'], 'Display time domain', self)
        self.display_td_action.triggered.connect(self.display_td_slot)
        
        self.spec_est_action = QAction(app_icons['estimate'], 'Spectral estimation', self)
        self.spec_est_action.triggered.connect(self.spectral_estimation_slot)
        
        self.exp_matlab_action = QAction(app_icons['export'], 'Export to MATLAB', self)
        self.exp_matlab_action.triggered.connect(self.exp_matlab_slot)
        
        self.exp_python_action = QAction(app_icons['export'], 'Export to Python/Numpy', self)
        self.exp_python_action.triggered.connect(self.exp_python_slot)
        
        self.delete_action = QAction(app_icons['delete'], 'Delete', self)
        self.delete_action.triggered.connect(self.delete_slot)
        
        menu.addAction(self.display_td_action)
        menu.addSeparator()
#         menu.addAction('Downsample')
#        menu.addAction('Discontinuity tool')
#         menu.addAction('Spectral normalisation')
        menu.addAction(self.spec_est_action)
        menu.addSeparator()
        menu.addAction(self.exp_matlab_action)
        menu.addAction(self.exp_python_action)
        menu.addSeparator()
        menu.addAction(self.delete_action)
        
        menu.exec_(self.mapToGlobal(point))
        
    @Slot()
    def delete_slot(self):
        self.parent().statusBar().showMessage('Deleting files...')
        rows = list(set([qmi.row() for qmi in self.table.selectedIndexes()]))
        files = [self.table_model.filtered_list[r][0] for r in rows]
        
        for f in files:
            try:
                os.remove(f)
            except IOError:
                print "something went wrong here"
            except WindowsError:
                print "file already deleted"
            finally:
                print "deleting..."
                print id(db)
                del db[f]
        
        save_db()
        
        self.parent().statusBar().showMessage('Done deleting files...')
        self.table_model.refreshModel()
        self.parent().statusBar().showMessage('Saving database...')
        save_db()
        self.parent().statusBar().showMessage('Ready')
        
    def validate_selection(self, files, allow_multiple_comps=False):
        if len(files) > 1:
            sources = set([db[f]['source'] for f in files])
            multiple_comps = False
            
            if len(sources) > 1:
                raise MultipleSourcesException()
            
            components = set([db[f]['component'] for f in files])
            
            sampling_rates = set([db[f]['sampling_rate'] for f in files])
            
            if len(components) > 1:
                if not allow_multiple_comps:
                    raise MultipleComponentsException()
            
            if len(sampling_rates) > 1:
                raise MultipleSamplingRatesException()
            
            files = sorted(files, key=lambda f: db[f]['start_time'])
            f_map = {c : [] for c in components}
            for f in files:
                f_map[db[f]['component']].append(f)
            
            start_times = []
            end_times = []
            for c in components:
                files = f_map[c]
                for idx in xrange(len(files) - 1):
                    if db[files[idx + 1]]['start_time'] - db[files[idx]]['end_time'] > timedelta(seconds=1):
                        raise NotContiguousException()
                start_times.append(db[files[0]]['start_time'])
                end_times.append(db[files[-1]]['end_time'])
            
            if len(set(start_times)) > 1 or len(set(end_times)) > 1:
                raise TimeMismatchException
            
            print f_map
        elif len(files) == 1:
            f_map = {db[files[0]]['component'] : files}
        else:
            return None
            
        return f_map
        
    @Slot(np.ndarray, np.ndarray)
    def display_td_processing_done_slot(self, x_axis, signal):
        print "I crash here"
        plotter = Plotter(x_axis, signal)
        plotter.closed.connect(self.plot_closed_slot)
        self.parent().statusBar().showMessage('Ready')
        self.plots.append(plotter)
    
    @Slot()
    def display_td_slot(self):
        print 'displaying td plot'
        rows = list(set([qmi.row() for qmi in self.table.selectedIndexes()]))
        files = [self.table_model.filtered_list[r][0] for r in rows]
        
        try:
            if not self.validate_selection(files):
                msgBox = QMessageBox()
                msgBox.setText("Library is empty.")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.exec_()
                return
            
            worker = ProcessTDWorker(files, self.parent())
            worker.messaging.connect(self.parent().statusBar().showMessage)
            self.workers.append(worker)
            process_td_thread = QThread()
            self.worker_threads.append(process_td_thread)
            worker.moveToThread(process_td_thread)
            worker.done.connect(self.display_td_processing_done_slot)
            process_td_thread.started.connect(worker.process_td)
            process_td_thread.start()
            worker.done.connect(process_td_thread.quit)
            process_td_thread.finished.connect(process_td_thread.deleteLater)
            
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
            
    def get_selected_rows_and_files(self):
        rows = list(set([qmi.row() for qmi in self.table.selectedIndexes()]))
        files = [self.table_model.filtered_list[r][0] for r in rows]
        return rows, files
        
    @Slot()
    def spectral_estimation_slot(self):
        print 'spectral estimation'
        rows, files = self.get_selected_rows_and_files()
        
        try:
            
            
            if not self.validate_selection(files):
                msgBox = QMessageBox()
                msgBox.setText("Library is empty.")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.exec_()
                return
            
            estimation_window = SpectralConf(files, self)
            estimation_window.show()
            estimation_window.closed.connect(self.spec_est_close_slot)
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
            
            
    def preprocess_export(self):
        rows, files = self.get_selected_rows_and_files()
        try:
            f_map = self.validate_selection(files, True)
            if not f_map:
                msgBox = QMessageBox()
                msgBox.setText("Library is empty.")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.exec_()
                return False
            
        except NotContiguousException:
            msgBox = QMessageBox()
            msgBox.setText("Only a selection of temporally contiguous files supported.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
            return False
        except MultipleComponentsException:
            pass
        except MultipleSourcesException:
            msgBox = QMessageBox()
            msgBox.setText("Please do not select data from multiple sources.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
            return False
        except MultipleSamplingRatesException:
            msgBox = QMessageBox()
            msgBox.setText("Please do not select data with different sampling rates.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
            return False
        except TimeMismatchException:
            msgBox = QMessageBox()
            msgBox.setText("Time intervals for multiple components do not align.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
            return False
        return f_map
            
    @Slot()
    def exp_matlab_slot(self):
        
        f_map = self.preprocess_export()
        if f_map:
            print f_map
            script = export_td.make_matlab(f_map)
            f_qt = QFileDialog.getSaveFileName(self, 'Save', filter='*.m')
            if f_qt is not None:
                with open(f_qt[0], 'w') as f:
                    f.write(script)

    
    @Slot()
    def exp_python_slot(self):
        f_map = self.preprocess_export()
        if f_map:
            print f_map
            script = export_td.make_numpy(f_map)
            f_qt = QFileDialog.getSaveFileName(self, 'Save', filter='*.py')
            if f_qt is not None:
                with open(f_qt[0], 'w') as f:
                    f.write(script)
        
    @Slot(QObject)
    def spec_est_close_slot(self, window):
        self.estimation_windows.remove(window)

        
    @Slot(QObject)
    def plot_closed_slot(self, plot):
        self.plots.remove(plot)
        
    @Slot()
    def download_more_slot(self):
        self.downloader = Downloader()
        self.downloader.run()
        self.downloader.finished_downloading_signal.connect(self.table_model.refreshModel)
        
class MultipleSourcesException(Exception):
    pass

class MultipleComponentsException(Exception):
    pass

class MultipleSamplingRatesException(Exception):
    pass

class NotContiguousException(Exception):
    pass

class TimeMismatchException(Exception):
    pass
        

if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    app = Library()
    app.run()
    qt_app.exec_()
