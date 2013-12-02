'''
Created on Nov 29, 2013

@author: Wiehan
'''

from PySide.QtGui import *
import os

app_icons = {
                'download' : 'cloud-download.png',
                'import' : 'download.png',
                'add_event' : 'flag.png',
                'help' : 'question.png',
                'graph' : 'stats.png',
                'estimate' : 'lab.png',
                'export' : 'export.png',
                'delete' : 'remove.png',
                'next' : 'arrow-right.png',
                'back' : 'arrow-left.png',
                'cancel' : 'cancel-circle.png',
                'apply' : 'checkmark.png',
            }

for key in app_icons.keys():
    app_icons[key] = QIcon(os.path.join('icons', app_icons[key]))