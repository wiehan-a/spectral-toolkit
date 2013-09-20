'''
Created on Sep 12, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *
from datetime import datetime, timedelta

class STDateTimeEdit(QDateTimeEdit):
    
    def __init__(self):
        QDateTimeEdit.__init__(self, QDateTime(datetime.now() - timedelta(days=1)))
    
    def date(self):
        qdate = super(QDateTimeEdit, self).datetime()
        return qdate.toPython()