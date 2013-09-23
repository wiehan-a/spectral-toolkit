'''
Created on Sep 23, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *

from config import *
import operator
from gui.stdateedit import STDateTimeEdit

class LibraryFilterWidget(QWidget):
    
    operator_map = {
                        '<' : operator.lt,
                        '<=' : operator.le,
                        '>' : operator.gt,
                        '>=' : operator.ge,
                        '=' : operator.eq,
                        '!=' : operator.ne
                    }
    
    operators = operator_map.keys()
    
    def __init__(self):
        QWidget.__init__(self)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel('<h3>Select filtering options</h3>')
        self.main_vbox.addWidget(self.title_label)
        
        self.filter_widgets = []
        
        prototype = db[db.keys()[0]]
        for key, value in prototype.iteritems():
            print key, value, type(value)
            layout = QHBoxLayout()
            use = QCheckBox()
            layout.addWidget(use)
            label = QLabel(key)
            layout.addWidget(label)
            combo = QComboBox()
            combo.addItems(self.operators)
            layout.addWidget(combo)
            self.filter_widgets.append(layout)
            layout.addStretch()
            
            edit_field = None
            
            if isinstance(value, datetime.datetime):
                edit_field = STDateTimeEdit()
            else:
                edit_field = QLineEdit()
            
            layout.addWidget(edit_field)
            
        for fw in self.filter_widgets:
            self.main_vbox.addLayout(fw)
            
        self.action_bar_hbox = QHBoxLayout()
        self.main_vbox.addLayout(self.action_bar_hbox)
        self.filter_button = QPushButton('Filter')
        self.action_bar_hbox.addStretch()
        self.action_bar_hbox.addWidget(self.filter_button)
        
    
    