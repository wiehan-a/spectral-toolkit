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

def read_segy_data(filename, head):
    f = open(filename, 'rb')
    f.seek(head['header_bytes'])
    
    # Note: this assumes little endianness
    i = head['data_form']
    
    
    data = np.ndarray(shape=(head['sample_count'],), dtype=['i2', 'i4', 'float64'][i], buffer=f.read())
    f.close()
     
    transducer_coefficient = 1 / (20 * 0.83)
    sensitivity = 2 * 20 / (2 ** 32)
    # data = -(data - np.mean(data)) * sensitivity / transducer_coefficient
    data = -(data) * sensitivity / transducer_coefficient
 
    return np.array(data)

def read_in_segy(files):
    return SegyFileBuffer(files).load_all_files()

class SegyFileBuffer:
    def __init__(self, files):
        self.files = files
        self.headers = [read_segy_head(f) for f in files]
        self.buffer_size = reduce(lambda x, y: x + y, map(lambda x: x['sample_count'], self.headers))
        
    
        
    def load_all_files(self):
        data = np.empty(shape=(self.buffer_size,), dtype=np.float64)  
        offset = 0
        for header, file in zip(self.headers, self.files):
            bs = header['sample_count']
            data[offset:offset + bs] = read_segy_data(file, header)
            offset += bs
        return data
