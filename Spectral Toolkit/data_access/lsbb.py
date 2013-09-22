'''
Created on Sep 12, 2013

@author: Wiehan
'''

import ftplib as ftp
import socket
import data_access.segy as segy
import datetime
import os.path
import utils

from config import *
from PySide.QtCore import *

SUPPORT_PARTIAL_PROGRESS_REPORTING = True

LSBB_IP_ADRESS = '193.52.13.2'
LSBB_BASE_URL = 'pub/data/Daily_SEGY_Data/'

LSBB_LOCAL_STORAGE_PATH = 'LSBB/'

if not os.path.exists(config_db['data_folder'] + '/LSBB/'):
    if not os.path.exists(config_db['data_folder']):
        os.mkdir(config_db['data_folder'])
    os.mkdir(config_db['data_folder'] + '/LSBB/')
    
class ControlledFTP:
    ftp_connection = None
    file_list_cache = {}
    download_callbacks = []
    
    def __enter__(self):
        if self.ftp_connection is None:
            self.ftp_connection = ftp.FTP(LSBB_IP_ADRESS)
            self.ftp_connection.login()
        return self
    
    def __exit__(self, type, value, traceback):
        if self.ftp_connection != None:
            self.ftp_connection.close()
        self.ftp_connection = None
    
    def get_file_list(self, date, cache=True):
        if cache and (date in self.file_list_cache):
            return self.file_list_cache[date]
        try:
            self.ftp_connection.cwd('/')
            self.ftp_connection.cwd(build_download_string(date))
            files = [f for f in self.ftp_connection.nlst() if 'MGN' in f]  # list directory contents
            self.ftp_connection.cwd('/')
            if cache:
                self.file_list_cache[date] = files
            return files
        except ftp.error_perm as x:
            print x
            return []
        
    def download_persist_callback(self, buffer):
        for callback in self.download_callbacks: 
            callback(buffer)
        self.file.write(buffer)
        
    def download(self, date, component, params):
        self.ftp_connection.cwd('/')
        self.ftp_connection.sendcmd('TYPE I')
        filename = get_local_file_name(date, component, params)
        self.file = open(filename, 'wb')
        self.ftp_connection.retrbinary('RETR '+self.get_path(date, component), self.download_persist_callback, 1024*1024/4)
        
        start_time = datetime.datetime.combine(self.params['start_date'], datetime.time())
        end_time = datetime.datetime.combine(self.params['end_date'] + datetime.timedelta(days=1) - 
                                             datetime.timedelta(seconds=1), datetime.time())
        
        db_add_entry(filename, 'LSBB', component, self.params['sampling_rate'], 
                     start_time, end_time)
        
        save_db()
        self.file.close()
    
    def get_components(self, filelist):
        return sorted(list(set([x.split('.')[-2] for x in filelist])))
    
    def get_file_name(self, date, component):
        if date not in self.file_list_cache:
            self.get_file_list(date)
        file_list = self.file_list_cache[date]
        return [x for x in file_list if component in x][0]
    
    def get_path(self, date, component):
        return build_download_string(date) + "/" + self.get_file_name(date, component)
    
    def retry_persistently(self, function, **args):
        pass
    
    def get_header(self, date, component):
        self.ftp_connection.cwd('/')
        self.ftp_connection.sendcmd('TYPE I')
        conn = self.ftp_connection.transfercmd('RETR ' + self.get_path(date, component), rest=None)
        data = conn.recv(240)
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        self.__exit__(type, None, None)
        self.__enter__()
        
        return segy.parse_header(data)
    
    def calculate_size(self, header):
        return header['header_bytes'] + [2, 4, 8][header['data_form']] * header['sample_count']
    
    def get_size(self, date, component):
        self.ftp_connection.sendcmd("TYPE I")
        self.ftp_connection.cwd(self.build_download_string(date))
        return self.ftp_connection.size(self.get_file_name(date, component))
    
class DownloaderWorker(QObject):
    
    progress_update = Signal(dict)
    done = Signal()
    
    def __init__(self, params):
        QObject.__init__(self)
        self.params = params
        
    def callback(self, buffer):
        
        self.cur_size += len(buffer)
        
        self.progress_update.emit({'cur_file_number': str(self.count),
                   'cur_downloaded': utils.sizeof_fmt(self.cur_size),
                   'overall_downloaded': utils.sizeof_fmt(self.size + self.cur_size),
                    'cur_file_bytes': self.cur_size,
                    'overall_bytes': self.size + self.cur_size
                   })
    
    Slot()
    def start_downloading(self):
        file_size = get_single_file_size(self.params)
        
        self.count = 1
        self.size = 0
        self.cur_size = 0
        
        with ControlledFTP() as handle:
            sd = self.params['start_date']                
            handle.download_callbacks = [self.callback]
            while sd <= self.params['end_date']:                 
                for c in self.params['components']:
                    self.cur_size = 0
                    print 'Downloading', sd, c

                    handle.download(sd, c, self.params)

                    self.size += file_size
                    self.count += 1
                     
                sd += datetime.timedelta(days=1)
                
                
        self.done.emit()
    
def get_local_file_name(date, component, params):
    sample_dir = config_db['data_folder'] + '/' + LSBB_LOCAL_STORAGE_PATH + str(params['sampling_rate'])
    if not os.path.exists(sample_dir):
        os.mkdir(sample_dir)
    return sample_dir + '/{:%Y.%m.%d}.'.format(date) + component + '.segy'
    
def build_download_string(date):
    return LSBB_BASE_URL + '{:%Y.%m/%Y.%m.%d}'.format(date)
    
def get_number_of_files(params):
    td = params['end_date'] - params['start_date']
    return (td.days + 1) * len(params['components'])

def get_single_file_size(params):
    return (4 * 24 * 60 * 60 * params['sampling_rate'] + 240) 
    
def calculate_size(params):
    return (get_number_of_files(params)) * get_single_file_size(params)

if __name__ == '__main__':
    print get_local_file_name(datetime.date.today(), 'CGE', {'sampling_rate' : 125})
