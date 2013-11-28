'''
Created on Sep 18, 2013

@author: Wiehan
'''

from __future__ import division

import utils, time, urllib2, urllib, datetime, os, zlib, struct
from config import *
from PySide.QtCore import *
import numpy as np

SUPPORT_PARTIAL_PROGRESS_REPORTING = False
SANSA_URL = 'http://geomagnet.ee.sun.ac.za/dbreadusec.php'
SANSA_READ_BUFFER_SIZE = 1024 * 1024 / 4

SANSA_LOCAL_STORAGE_PATH = '/SANSA/'

if not os.path.exists(config_db['data_folder'] + '/SANSA/'):
    if not os.path.exists(config_db['data_folder']):
        os.mkdir(config_db['data_folder'])
    os.mkdir(config_db['data_folder'] + '/SANSA/')

def sansa_date_format(date):
    return urllib.quote_plus('{:%Y-%m-%d %H:%M:%S}'.format(date))

def build_request_string(params):
    return SANSA_URL + '?fromdatetime=' + sansa_date_format(params['start_date']) + '&todatetime=' + sansa_date_format(params['end_date']) 
    
def calculate_size(params):
    return (params['end_date'] - params['start_date']).total_seconds()

def make_file_name(params, comp):
    return config_db['data_folder'] + SANSA_LOCAL_STORAGE_PATH + '{:%Y.%m.%d.%H.%M.%S}'.format(params['start_date']) + '.' + '{:%Y.%m.%d.%H.%M.%S}'.format(params['end_date']) + '.' + comp

class DownloaderWorker(QObject):
    
    progress_update = Signal(dict)
    done = Signal()
    cancel_done = Signal()
    cancel_flag = False
    
    def __init__(self, params):
        QObject.__init__(self)
        self.params = params
        
    def callback(self, buffer):
        
        self.size += len(buffer)
        
        self.progress_update.emit({'overall_downloaded': utils.sizeof_fmt(self.size),
                                   'overall_bytes': self.size
                                   })
        
    @Slot()
    def cancel(self):
        self.cancel_flag = True
        self.comp_1_file.close()
        os.remove(self.comp_1_file.name)
        self.comp_2_file.close()
        os.remove(self.comp_1_file.name)
        self.comp_3_file.close()
        os.remove(self.comp_3_file.name)
    
    def download(self, start_time, end_time):
        
        if config_db.has_key("proxies"):
            proxy_support = urllib2.ProxyHandler(config_db['proxies'])
            opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler(debuglevel=1))
            urllib2.install_opener(opener)
        
        request = urllib2.Request(build_request_string({'start_date' : start_time,
                                                        'end_date' : end_time}))
        request.add_header('Accept-encoding', 'gzip,deflate')
        response = urllib2.urlopen(request)
        self.response = response
        
        is_gzipped = response.headers.get('content-encoding', '').find('gzip') >= 0
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        buffer = response.read()
        if is_gzipped:
            compressed = len(buffer)
            self.real_size += compressed
            buffer = d.decompress(buffer)
            print len(buffer) / compressed
            
            for x in buffer.split('<br>'):
                line = x.split(';')
                if len(line) > 1:
                    self.comp_1_file.write(struct.pack('f', float(line[3])))
                    self.comp_2_file.write(struct.pack('f', float(line[4])))
                    self.comp_3_file.write(struct.pack('f', float(line[5])))            
            
        self.size += 10 * 60
        
        print utils.sizeof_fmt(self.real_size)
        
        self.progress_update.emit({'overall_downloaded': utils.sizeof_fmt(self.real_size),
                                   'overall_bytes': self.size,
                                   'size_unknown' : True
                                   })
    
    Slot()
    def start_downloading(self):
        
        self.size = 0
        self.real_size = 0
        
        self.comp_1_file = open(make_file_name(self.params, 'COMP1'), 'wb')
        self.comp_2_file = open(make_file_name(self.params, 'COMP2'), 'wb')
        self.comp_3_file = open(make_file_name(self.params, 'COMP3'), 'wb')
        
        start_time = self.params['start_date']
        incr_end_time = start_time + datetime.timedelta(minutes=10)
        end_time = self.params['end_date']
        
        while incr_end_time < end_time:
            if self.cancel_flag:
                self.cancel_done.emit()
                return
            self.download(start_time, incr_end_time)
            start_time = incr_end_time + datetime.timedelta(seconds=1)
            incr_end_time += datetime.timedelta(minutes=10)
        
        self.download(start_time, end_time)

        db_add_entry(make_file_name(self.params, 'COMP1'), 'SANSA',
                     'COMP1', 125, self.params['start_date'], self.params['end_date'])
        db_add_entry(make_file_name(self.params, 'COMP2'), 'SANSA',
                     'COMP2', 125, self.params['start_date'], self.params['end_date'])
        db_add_entry(make_file_name(self.params, 'COMP3'), 'SANSA',
                     'COMP3', 125, self.params['start_date'], self.params['end_date'])
        save_db()

        self.comp_1_file.close()
        self.comp_2_file.close()
        self.comp_3_file.close()
                
        self.done.emit()
        
def read_in_filenames(filenames):
    data = np.zeros(0)
    for filename in filenames:
        with open(filename, 'rb') as f:
            buffer = f.read()
            
            print len(buffer)
            print len(buffer) / 4
            
            data = np.hstack((data, np.ndarray(shape=(int(len(buffer) / 4)), dtype='float32', buffer=buffer)))
    
    return data.astype(np.float64)

if __name__ == '__main__':
    f = open('../DEBUG.COMP3', 'rb')
    buffer = f.read()
    
    print np.ndarray(shape=(len(buffer) / 4,), dtype='float32', buffer=buffer)
