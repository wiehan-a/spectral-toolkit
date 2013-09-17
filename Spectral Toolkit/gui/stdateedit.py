'''
Created on Sep 12, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *
from datetime import date, timedelta

class STDateEdit(QDateEdit):
    
    def __init__(self):
        QDateEdit.__init__(self, QDate(date.today() - timedelta(days=1)))
    
    def date(self):
        qdate = super(QDateEdit, self).date()
        return qdate.toPython()