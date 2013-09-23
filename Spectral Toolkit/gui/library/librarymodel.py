'''
Created on Sep 23, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *
from config import *

class LibraryModel(QAbstractTableModel):
    
    def __init__(self):
        
        QAbstractTableModel.__init__(self)
        
        get_date = lambda key : db[key]['start_time']
        
        self.db_flat_view = []
        for key in sorted(db.keys(), key=get_date):
            self.db_flat_view.append([
                                         key, db[key]['start_time'], db[key]['end_time'],
                                         db[key]['source'], db[key]['component'],
                                         db[key]['sampling_rate']
                                     ])
        
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.db_flat_view)
    
    def columnCount(self, parent=QModelIndex()):
        return 5
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            val = self.db_flat_view[index.row()][index.column() + 1]
            return str(val)
        else:
            return None     
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                print 'doing something'
                return ['Start time', 'End time', 'Data source', 'Component', 'Sampling rate'][section]

        return None
#     def removeRows(self, *args, **kwargs):
#         self.beginRemoveColumns()
#         return QAbstractTableModel.removeRows(self, *args, **kwargs)
#         self.endRemoveRows()
