'''
Created on Sep 23, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *
from config import *

headers_db = ['start_time', 'end_time', 'source', 'component', 'sampling_rate', 'num_missing_samples']
headers_filter = [True, True, True, True, True, False]
headers_filter_map = {headers_db[x] : headers_filter[x] for x in xrange(len(headers_db))}
headers_db_indices = {headers_db[x] : (x + 1)  for x in xrange(len(headers_db))}
headers_pretty = ['Start', 'End', 'Source', 'Component', 'Sampling rate', '# Missing']
headers_db_pretty_map = {headers_db[x] : headers_pretty[x] for x in xrange(len(headers_db))}

class LibraryModel(QAbstractTableModel):
    
    def __init__(self):
        QAbstractTableModel.__init__(self)
        self.refreshModel()
    
    @Slot()
    def refreshModel(self):
        self.beginResetModel()
        get_date = lambda key : db[key]['start_time']
        self.db_flat_view = []
        self.filtered_list = self.db_flat_view
        for key in sorted(db.keys(), key=get_date):
            row = [key]
            for field in headers_db:
                row.append(db[key][field])
            self.db_flat_view.append(row)
        self.endResetModel()
        
    @Slot()
    def applyFilters(self, filters):
        self.beginResetModel()
        self.filtered_list = []
        for entry in self.db_flat_view:
            keep = True
            for filter in filters:
                if not filter.apply(entry):
                    keep = False
                    break
            if keep:
                self.filtered_list.append(entry)
        self.endResetModel()
        
    @Slot()
    def reset_slot(self):
        self.beginResetModel()
        self.filtered_list = self.db_flat_view
        self.endResetModel()
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.filtered_list)
    
    def columnCount(self, parent=QModelIndex()):
        return 6
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            val = self.filtered_list[index.row()][index.column() + 1]
            return str(val)
        else:
            return None     
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return headers_pretty[section]

        return None