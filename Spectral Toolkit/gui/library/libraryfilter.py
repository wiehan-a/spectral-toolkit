'''
Created on Sep 23, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *

import librarymodel
from config import *
import operator
from gui.stdateedit import STDateTimeEdit

operator_map = {
                    '<' : operator.lt,
                    '<=' : operator.le,
                    '>' : operator.gt,
                    '>=' : operator.ge,
                    '=' : operator.eq,
                    '!=' : operator.ne
                }

operators = operator_map.keys()

class LibraryFilterWidget(QWidget):
    
    def __init__(self, model):
        QWidget.__init__(self)
        
        self.model = model
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel('<h3>Select filtering options</h3>')
        self.main_vbox.addWidget(self.title_label)
        
        self.filter_widgets = []
        
        try:
            prototype = db[db.keys()[0]]
        except IndexError:
            prototype = {
                            "component": "HGZ",
                            "end_time": datetime.datetime.now(),
                            "sampling_rate": 125,
                            "source": "LSBB",
                            "start_time": datetime.datetime.now()
                        }
        
        for key, value in prototype.iteritems():
            self.filter_widgets.append(FilterItemWidget(key, value))

            
        for fw in self.filter_widgets:
            self.main_vbox.addLayout(fw)
            
        self.main_vbox.addStretch()
            
        self.action_bar_hbox = QHBoxLayout()
        self.main_vbox.addLayout(self.action_bar_hbox)
        self.reset_view_button = QPushButton('Reset view')
        self.reset_view_button.clicked.connect(self.model.reset_slot)
        self.action_bar_hbox.addWidget(self.reset_view_button)
        self.action_bar_hbox.addStretch()
        self.filter_button = QPushButton('Apply filter')
        self.filter_button.clicked.connect(self.apply_filter_slot)
        self.action_bar_hbox.addWidget(self.filter_button)
        
    @Slot()
    def apply_filter_slot(self):
        self.model.applyFilters([w.makeFilter() for w in self.filter_widgets])

    
class FilterItemWidget(QHBoxLayout):
    
    def __init__(self, key, prototype):
        QHBoxLayout.__init__(self)
        
        self.key = key
        self.prototype = prototype
                    
        self.use_chkbox = QCheckBox()
        self.addWidget(self.use_chkbox)
        self.label = QLabel(librarymodel.headers_db_pretty_map[key])
        self.addWidget(self.label)
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(operators)
        self.addWidget(self.operator_combo)
        
        self.addStretch()
        
        self.edit_field = None
        
        if isinstance(prototype, datetime.datetime):
            self.edit_field = STDateTimeEdit()
        else:
            self.edit_field = QLineEdit()
        
        self.addWidget(self.edit_field)
        
    def makeFilter(self):
        value = None
        
        if self.use_chkbox.isChecked():
            if isinstance(self.prototype, datetime.datetime):
                value = self.edit_field.date()
            elif isinstance(self.prototype, int):
                value = int(self.edit_field.text())
            else:
                value = self.edit_field.text()
        
        return Filter(value, self.key, operator_map[operators[self.operator_combo.currentIndex()]])
    
class Filter():
    
    def __init__(self, value, key, operator):
        self.value = value
        self.operator = operator
        self.key = key
    
    def apply(self, entry):
        if self.value is None:
            return True
        return self.operator(entry[librarymodel.headers_db_indices[self.key]], self.value)
        
    
    