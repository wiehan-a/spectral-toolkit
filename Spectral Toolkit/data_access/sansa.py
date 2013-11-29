'''
Created on Sep 18, 2013

@author: Wiehan
'''

from __future__ import division

import utils, time, urllib2, urllib, datetime, os, zlib, struct
from config import *
from PySide.QtCore import *
import numpy as np
from file_buffer import FileBuffer

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

def make_file_name(start, end, comp):
    return config_db['data_folder'] + SANSA_LOCAL_STORAGE_PATH + '{:%Y.%m.%d.%H.%M.%S}'.format(start) + '.' + '{:%Y.%m.%d.%H.%M.%S}'.format(end) + '.' + comp

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
        print start_time, end_time
        num_samples = int(125 * (end_time - start_time).total_seconds())
        
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
            print "LB", len(buffer) / compressed
            
            lines = buffer.split('<br>')
            if len(buffer) == 0 or len(lines) == 0:
                print "********* No data for block: ", num_samples, "samples missed"
                zeros = np.zeros(shape=(num_samples,), dtype=np.float32)
                zeros.tofile(self.comp_1_file, format='f')
                zeros.tofile(self.comp_2_file, format='f')
                zeros.tofile(self.comp_3_file, format='f')
                
                self.missing_intervals.append([self.sample_count, self.sample_count + num_samples])
                self.sample_count += num_samples
            
            else:
                last_time = start_time
                for x in lines:
                    line = x.split(';')
                    if len(line) > 1:
                        time_ = datetime.datetime.strptime(line[1], "%Y-%m-%d %H:%M:%S").replace(microsecond=int(line[2]))
                        interval = time_ - last_time
                        if interval > datetime.timedelta(microseconds=8100):
                            samples_missed = np.round(interval.total_seconds() / (1.0 / 125))
                            print "****** A-- we missed some samples ===", samples_missed, last_time, time_
                            zeros = np.zeros(shape=(samples_missed - 1,), dtype=np.float32)
                            zeros.tofile(self.comp_1_file, format='f')
                            zeros.tofile(self.comp_2_file, format='f')
                            zeros.tofile(self.comp_3_file, format='f')
                            self.missing_intervals.append([self.sample_count, self.sample_count + samples_missed])
                            self.sample_count += samples_missed
                        
                        last_time = time_
                        self.comp_1_file.write(struct.pack('f', float(line[3])))
                        self.comp_2_file.write(struct.pack('f', float(line[4])))
                        self.comp_3_file.write(struct.pack('f', float(line[5])))
                        self.sample_count += 1
                        
                interval = end_time - last_time
                if interval > datetime.timedelta(microseconds=16000):
                    samples_missed = np.round(interval.total_seconds() / (1.0 / 125)) - 1
                    print "****** B-- we missed some samples ===", samples_missed
                    zeros = np.zeros(shape=(samples_missed,), dtype=np.float32)
                    zeros.tofile(self.comp_1_file, format='f')
                    zeros.tofile(self.comp_2_file, format='f')
                    zeros.tofile(self.comp_3_file, format='f')
                    self.missing_intervals.append([self.sample_count, self.sample_count + samples_missed])
                    self.sample_count += samples_missed
                            
            
        self.size += 10 * 60
        
        print utils.sizeof_fmt(self.real_size)
        
        self.progress_update.emit({'overall_downloaded': utils.sizeof_fmt(self.real_size),
                                   'overall_bytes': self.size,
                                   'size_unknown' : True
                                   })
        
    def get_intervals(self):
        start_time = self.params['start_date']
        end_time = self.params['end_date']
        
        sansa_keys = sorted([key for key, value in db.items() 
                            if value['source'] == 'SANSA' 
                                and ((value['end_time'] >= start_time and value['start_time'] <= end_time) or
                                     (value['start_time'] < start_time and value['end_time'] > start_time) or
                                     (value['end_time'] > end_time and value['start_time'] < end_time))
                                and value['component'] == "COMP1"],
                            key=lambda x: db[x]['start_time'])
        
        i = [(db[key]['start_time'], db[key]['end_time']) for key in sansa_keys]
        
        if len(i) == 0:
            return [[start_time, end_time]]

        empty_intervals = [[start_time, i[0][0]]]
        for idx in xrange(len(i) - 1):
            empty_intervals.append([i[idx][1], i[idx + 1][0]])
        empty_intervals.append([i[-1][1], end_time])
            
        empty_intervals = [x for x in empty_intervals if x[0] < x[1]]    
        return empty_intervals
        
    def merge_missing_intervals(self):
        idx = len(self.missing_intervals) - 1
        
        while idx > 0:
            if self.missing_intervals[idx - 1][1] == self.missing_intervals[idx][0]:
                self.missing_intervals[idx - 1][1] = self.missing_intervals[idx][1]
                del self.missing_intervals[idx]

            idx -= 1
    
    Slot()
    def start_downloading(self):
        
        intervals = self.get_intervals()
        
        self.size = 0
        self.real_size = 0
        
        for interval in intervals:
            
            self.sample_count = 0
            self.missing_intervals = []
            
            n1 = make_file_name(interval[0], interval[1], 'COMP1')
            n2 = make_file_name(interval[0], interval[1], 'COMP2')
            n3 = make_file_name(interval[0], interval[1], 'COMP3')
            
            self.comp_1_file = open(n1, 'wb')
            self.comp_2_file = open(n2, 'wb')
            self.comp_3_file = open(n3, 'wb')
            
            start_time = interval[0]
            incr_end_time = start_time + datetime.timedelta(minutes=10)
            end_time = interval[1]
            
            while incr_end_time < end_time:
                if self.cancel_flag:
                    self.cancel_done.emit()
                    return
                self.download(start_time, incr_end_time)
                start_time = incr_end_time + datetime.timedelta(seconds=1)
                incr_end_time += datetime.timedelta(minutes=10)
            
            if start_time < end_time:
                self.download(start_time, end_time)
            
            print self.missing_intervals
            self.merge_missing_intervals()
            if len(self.missing_intervals) > 0:
                with open(n1 + ".annot", "w") as f:
                    f.write(json.dumps(self.missing_intervals))
                    
                db_add_entry(n1, 'SANSA', 'COMP1', 125, interval[0], interval[1], True, n1 + ".annot")
                db_add_entry(n2, 'SANSA', 'COMP2', 125, interval[0], interval[1], True, n1 + ".annot")
                db_add_entry(n3, 'SANSA', 'COMP3', 125, interval[0], interval[1], True, n1 + ".annot")
            else:
                db_add_entry(n1, 'SANSA', 'COMP1', 125, interval[0], interval[1], False)
                db_add_entry(n2, 'SANSA', 'COMP2', 125, interval[0], interval[1], False)
                db_add_entry(n3, 'SANSA', 'COMP3', 125, interval[0], interval[1], False)
                
            
            save_db()
    
            self.comp_1_file.close()
            self.comp_2_file.close()
            self.comp_3_file.close()
                
        self.done.emit()
        
def read_in_filenames(filenames, start_trim=0, end_trim=0):
    return SansaFileBuffer(filenames, start_trim, end_trim)

class SansaFileBuffer(FileBuffer):
    
    def __init__(self, files, begin_trim=0, end_trim=0):        
        self.headers = [{'sample_count' : int(os.path.getsize(f) / 4)} for f in files]
        FileBuffer.__init__(self, files, begin_trim, end_trim)
        
    def read_proxy(self, filename, head, offset=0, samples='all'):
        with open(filename, 'rb') as f:
            f.seek(offset * 4)
            buffer = None
            if samples == "all":
                buffer = f.read()
            else:
                buffer = f.read(4 * samples)
            return np.ndarray(shape=(int(len(buffer) / 4)), dtype='float32', buffer=buffer)
