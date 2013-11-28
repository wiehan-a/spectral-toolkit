'''
Created on Jun 13, 2013

@author: Wiehan
'''
from __future__ import division

from struct import *
import array
# import matplotlib.pyplot as plt
import numpy as np
# import scipy.signal as sig
# from numpy.fft.fftpack import ifft
# from numpy.lib.function_base import meshgrid

def parse_header(data):
    
    format_string = "<iiiiiiihhhhiiiiiiiihhiiiihhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhBBBBBBBBBBBBBBBBBBhihhhhhhhhfHhiii"
    head = {}
    
    data = unpack(format_string, data)
    
    head['header_bytes'] = 240
    head['data_form'] = data[91]
    head['sample_count'] = max(data[102], data[38])
    head['sample rate'] = 1 / (data[39] * 1e-6)
    
    return head    

def read_segy_head(filename):
    f = open(filename, 'rb')
    head = parse_header(f.read(240))
    f.close()
    return head

def read_segy_data(filename, head, offset=0, samples='all'):
    f = open(filename, 'rb')
    f.seek(head['header_bytes'] + offset*4)
    
    # Note: this assumes little endianness
    i = head['data_form']
    
    if samples == 'all':
        data = np.ndarray(shape=(head['sample_count'] - offset,), dtype='i4', buffer=f.read())
    else:
        samples = int(samples)
        data = np.ndarray(shape=(samples,), dtype='i4', buffer=f.read(samples * 4))
    
    f.close()
     
    transducer_coefficient = 1 / (20 * 0.83)
    sensitivity = 2 * 20 / (2 ** 32)
    # data = -(data - np.mean(data)) * sensitivity / transducer_coefficient
    data = -(data) * sensitivity / transducer_coefficient
 
    return np.array(data)

def read_in_segy(files, begin_trim=0, end_trim=0):
    return SegyFileBuffer(files, begin_trim, end_trim)

class SegyFileBuffer:
    
    def __init__(self, files, begin_trim=0, end_trim=0):
        self.files = files
        self.begin_trim = int(begin_trim)
        self.end_trim = int(end_trim)
        
        self.headers = [read_segy_head(f) for f in files]
        self.sample_counts = map(lambda x: x['sample_count'], self.headers)
        self.buffer_size = reduce(lambda x, y: x + y, self.sample_counts)
        
        for idx in xrange(1, len(self.files)):
            self.sample_counts[idx] = self.sample_counts[idx] + self.sample_counts[idx - 1]
        
        self.seek(0)
        
    def __len__(self):
        return self.buffer_size - (self.begin_trim + self.end_trim)
    
    def __getitem__(self, key):
        if isinstance(key, slice) :
            self.seek(key.start + self.begin_trim)
            return self.read(key.stop - key.start)
        
    def seek(self, sample):
        '''
            Set the internal position to sample.
        '''
        self.cur_file = None
        self.cur_sample = sample
        for idx, val in enumerate(self.sample_counts):
            if sample < val and sample >= val - self.headers[idx]['sample_count']:
                self.cur_file = idx
                self.offset_in_file = sample - (val - self.headers[idx]['sample_count'])
                break
    
    def read(self, samples):
        '''
            Read a number of samples from the amalgamation.
        '''
        if self.cur_file is None:
            return None
        
        samples = min(samples, self.buffer_size - self.cur_sample)
        data = np.zeros(shape=(samples,), dtype=np.float64)
        samples_remaining = samples
        foffset = self.offset_in_file
        offset = 0
        f = self.cur_file
        
        while samples_remaining > 0:
            #
            
            diff_in_file = self.headers[f]['sample_count'] - foffset
            #print f, offset, diff_in_file, samples_remaining, self.headers[f]['sample_count'], foffset
            if diff_in_file <= samples_remaining:
                print "file", f, "; sample", foffset, "to", diff_in_file+foffset, "in buffer", offset, 'to', offset + diff_in_file
                data[offset : offset + diff_in_file] = read_segy_data(self.files[f], self.headers[f], offset=foffset, samples=diff_in_file)
                samples_remaining -= diff_in_file
                f += 1
                foffset = 0
                offset += diff_in_file
            else: #diff_in_file >= samples_remaining 
                print "file", f, "; sample", foffset, "to", samples_remaining+foffset, "in buffer", offset, 'to', offset + samples_remaining
                data[offset : offset + samples_remaining] = read_segy_data(self.files[f], self.headers[f], offset=foffset, samples=samples_remaining)
                samples_remaining = 0
         
        
        return data
        
        
        
    def load_all_files(self):
        return self.read(self.buffer_size)
