'''
Created on Sep 23, 2013

@author: Wiehan
'''
import sys

from PySide.QtCore import *
from PySide.QtGui import *
from gui.library.librarymodel import LibraryModel
from gui.library.libraryfilter import LibraryFilterWidget
from gui.downloader.downloader import Downloader, DownloaderWidget
from gui.downloader.importer import Importer
from gui.data_invalid import DataInvalidAdder
from gui.spectral_conf.spectral_conf import SpectralConf

import gc, os, datetime, pytz, functools


from config import *
from gui.display.plot_td import *
from gui.icons import *

from data_access import export_td
from gui.display.thumbnail_preview import ThumbnailPlotter
from data_access import file_buffer
from gui.library.interpolate_worker import InterpolateWorker


class Library(QMainWindow):
    
    workers = []
    worker_threads = []
    
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Spectral Toolkit (Data library)')
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        self.setWindowIcon(QIcon('icon.png'))
        
        self.statusBar().showMessage('Ready')
        
        if os.name == 'nt':
            import ctypes
            myappid = 'SpecTool.Library.1.0.0'
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
        self.invalidate_action.triggered.connect(self.data_invalid_add_slot)
        self.data_menu.addAction(self.download_action)
        self.data_menu.addAction(self.import_action)
        self.data_menu.addSeparator()
        self.data_menu.addAction(self.invalidate_action)
        
        self.overviews_menu = self.menuBar().addMenu("&Overviews")
        self.overview_times = ["Last 10 &minutes", "Last &hour", "Last &6 hours", "Last &24 hours"]
        self.overview_timedeltas = [datetime.timedelta(minutes=10), datetime.timedelta(hours=1), datetime.timedelta(hours=6), datetime.timedelta(hours=24)]
        for idx, ot in enumerate(self.overview_times):
            action = QAction(ot, self)
            action.triggered.connect(functools.partial(self.overview_triggered, self.overview_timedeltas[idx]))
            self.overviews_menu.addAction(action)
        
        self.help_menu = self.menuBar().addMenu("&Help")
        self.help_action = QAction(app_icons['help'], "&User guide", self)
        self.help_action.triggered.connect(self.user_guide_slot)
        self.about_action = QAction("&About Spectral Toolkit", self)
        self.about_action.triggered.connect(self.about_slot)
        self.help_menu.addAction(self.help_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)
        
    @Slot()
    def user_guide_slot(self):
        QDesktopServices.openUrl(QUrl("User_guide.pdf"));
        
    @Slot()
    def about_slot(self):
        QMessageBox.about(self, "About Spectral Toolkit", 
                          '''<p><b>Author:</b> Wiehan Agenbag (<a href="mailto:wiehan.a@gmail.com?Subject=Spectral Toolkit">wiehan.a@gmail.com</a>)</p>
                          <p>Source code is available on the project's GitHub <a href="https://github.com/wiehan-a/spectral-toolkit/">page</a>.</p>'''
                          )
        
    @Slot()
    def cancel_successful(self):
        pass
    
    @Slot()
    def done_slot(self):
        print "done downloading data for overview"
        files, start, end = query_db_by_time('SANSA', self.overview_params['start_date'], self.overview_params['end_date'])
        
        print files
        
        worker = ProcessTDWorker(files, self, multi_component=True)
        worker.messaging.connect(self.statusBar().showMessage)
        self.lib.workers.append(worker)
        process_td_thread = QThread()
        self.lib.worker_threads.append(process_td_thread)
        worker.moveToThread(process_td_thread)
        worker.done.connect(self.overview_processing_done_slot)
        process_td_thread.started.connect(worker.process_td)
        process_td_thread.start()
        worker.done.connect(process_td_thread.quit)
        process_td_thread.finished.connect(process_td_thread.deleteLater)
        
        estimation_window = SpectralConf(files, self.lib, True, self.overview_params['start_date'], self.overview_params['end_date'])
        estimation_window.show()
        estimation_window.closed.connect(self.lib.spec_est_close_slot)
        self.lib.estimation_windows.append(estimation_window)
        
        
    @Slot()
    def overview_processing_done_slot(self, x_axis, signals, annotations, components):
        print "done downsampling"
        self.statusBar().showMessage('Plotting...')
        plotter = Plotter(x_axis, signals, annotations, None, "nT", components, False)
        self.lib.main_tabwidget.addTab(plotter, "Plot (TD)")
        plotter.closed.connect(self.lib.plot_closed_slot)
        self.statusBar().showMessage('Ready')
        self.lib.plots.append(plotter)
        self.overview_downloader.setVisible(False)
        self.overview_downloader.deleteLater()
        self.lib.table_model.refreshModel()
        
        
    def overview_triggered(self, timedelta_):
        now = datetime.datetime.utcnow()
        print "get from", now - timedelta_, "to", now
        
        self.overview_params = {'access_engine': data_access.sansa,
                  'sampling_rate': 125,
                  'start_date': now - timedelta_,
                  'end_date': now,
                  'source': 'SANSA'}
        
        self.overview_downloader = DownloaderWidget(self.overview_params, self, stand_alone=True).run()
    
    @Slot()
    def import_slot(self):
        self.importer = Importer(self).run()
        
    @Slot()
    def data_invalid_add_slot(self):
        self.data_inv = DataInvalidAdder(self).run()
        
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
        
        self.main_tabwidget = QTabWidget()
        self.table = QTableView()
        self.table_model = LibraryModel()
        self.table.setModel(self.table_model)
        self.left_vbox.addWidget(self.main_tabwidget)
        self.main_tabwidget.addTab(self.table, "Library")
        self.main_tabwidget.tabCloseRequested.connect(self.closeTab)
        self.main_tabwidget.tabBar().installEventFilter(self)
        verthead = self.table.verticalHeader()
        verthead.setDefaultSectionSize(verthead.fontMetrics().height() + 4)
         
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        
        self.filter_widget = LibraryFilterWidget(self.table_model)
        self.right_vbox.addWidget(self.filter_widget)
        self.thumb_plot_widget = ThumbnailPlotter()
        self.right_vbox.addWidget(self.thumb_plot_widget)
        self.thumb_plot_f_widget = ThumbnailPlotter("Frequency domain preview")
        self.right_vbox.addWidget(self.thumb_plot_f_widget)
        self.right_vbox.addStretch()
        
        self.main_hbox.setStretchFactor(self.left_vbox, 2)
        
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.tableContextMenu)
        
        m = self.table.selectionModel()
        m.selectionChanged.connect(self.tableSelectionChanged)
        
    def eventFilter(self, obj, event):
        if isinstance(event, QContextMenuEvent):
            print "right click"
            tab_index = self.main_tabwidget.tabBar().tabAt(event.pos())
            if tab_index != 0:
                menu = QMenu(self)
                callback = functools.partial(self.popOutTab, tab_index)
                self.popout_action = QAction(app_icons['export'], 'Pop out tab', self)
                self.popout_action.triggered.connect(callback)
                
                callback = functools.partial(self.closeTab, tab_index)
                self.close_action = QAction(app_icons['delete'], 'Close tab', self)
                self.close_action.triggered.connect(callback)
                
                menu.addAction(self.popout_action)
                menu.addAction(self.close_action)
                
                menu.exec_(self.mapToGlobal(event.pos()))
                return True
        return QWidget.eventFilter(self, obj, event)
        
    def popOutTab(self, index):
        if index == 0:
            return
        widget = self.main_tabwidget.widget(index)
        self.main_tabwidget.removeTab(index)
        widget.setVisible(True)
        widget.setParent(None)
        widget.show()
        
    @Slot(int)
    def closeTab(self, index):
        widget = self.main_tabwidget.widget(index)
        self.main_tabwidget.removeTab(index)
        widget.close()
        
    @Slot()
    def tableSelectionChanged(self):
        rows = list(set([qmi.row() for qmi in self.table.selectedIndexes()]))
        files = [self.table_model.filtered_list[r][0] for r in rows]
        if len(files) == 1:
            self.thumb_plot_widget.setLoading()
            self.preview_signal = file_buffer.load_preview(files)
            self.thumb_plot_widget.draw(self.preview_signal)
            
            self.preview_f_signal = file_buffer.load_f_preview(files)
            self.thumb_plot_f_widget.draw(self.preview_f_signal)

        
    @Slot(QPoint)
    def tableContextMenu(self, point):
        menu = QMenu(self)
        self.display_td_action = QAction(app_icons['graph'], 'Display time domain', self)
        self.display_td_action.triggered.connect(self.display_td_slot)
        
        self.spec_est_action = QAction(app_icons['estimate'], 'Spectral estimation', self)
        self.spec_est_action.triggered.connect(self.spectral_estimation_slot)
        
        self.interpolate_action = QAction(app_icons['estimate'], 'Interpolate missing samples', self)
        self.interpolate_action.triggered.connect(self.interpolate_slot)
        
        self.exp_matlab_action = QAction(app_icons['export'], 'Export to MATLAB', self)
        self.exp_matlab_action.triggered.connect(self.exp_matlab_slot)
        
        self.exp_python_action = QAction(app_icons['export'], 'Export to Python/Numpy', self)
        self.exp_python_action.triggered.connect(self.exp_python_slot)
        
        self.delete_action = QAction(app_icons['delete'], 'Delete', self)
        self.delete_action.triggered.connect(self.delete_slot)
        
        menu.addAction(self.display_td_action)
        menu.addSeparator()
        menu.addAction(self.interpolate_action)
        menu.addAction(self.spec_est_action)
        menu.addSeparator()
        menu.addAction(self.exp_matlab_action)
        menu.addAction(self.exp_python_action)
        menu.addSeparator()
        menu.addAction(self.delete_action)
        
        menu.exec_(self.mapToGlobal(point))
        
    @Slot()
    def interpolate_slot(self):
        rows = list(set([qmi.row() for qmi in self.table.selectedIndexes()]))
        if len(rows) == 1:
            files = [self.table_model.filtered_list[rows[0]][0]]

            worker = InterpolateWorker(files, self.parent())
            worker.messaging.connect(self.parent().statusBar().showMessage)
            self.workers.append(worker)
            interpolate_thread = QThread()
            self.worker_threads.append(interpolate_thread)
            worker.moveToThread(interpolate_thread)
            
            callback = functools.partial(self.parent().statusBar().showMessage, 'Done interpolating...')
            worker.done.connect(callback)
            interpolate_thread.started.connect(worker.interpolate)
            interpolate_thread.start()
            worker.done.connect(interpolate_thread.quit)
            interpolate_thread.finished.connect(interpolate_thread.deleteLater)
        
    @Slot()
    def delete_slot(self):
        self.parent().statusBar().showMessage('Deleting files...')
        rows = list(set([qmi.row() for qmi in self.table.selectedIndexes()]))
        files = [self.table_model.filtered_list[r][0] for r in rows]
        
        for f in files:
            
            try:
                os.remove(f+".pre")
            except:
                pass
            
            try:
                os.remove(f+".spec_pre")
            except:
                pass
            
            try:
                os.remove(f+".annot")
            except:
                pass
            
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
        
    @Slot(np.ndarray, np.ndarray, list)
    def display_td_processing_done_slot(self, x_axis, signal, annotations):
        # print "I crash here"
        plotter = Plotter(x_axis, signal, annotations, None, "nT")
        plotter.closed.connect(self.plot_closed_slot)
        self.parent().statusBar().showMessage('Ready')
        self.plots.append(plotter)
        self.main_tabwidget.addTab(plotter, "Plot (TD)")
    
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
            if f_qt is not None and len(f_qt[0]) > 0:
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
        print "print this runs"
        plt.close(plot.figure)
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
        
