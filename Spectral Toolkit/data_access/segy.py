'''
Created on Jun 13, 2013

@author: Wiehan
'''
from __future__ import division

from struct import *
import array
# import matplotlib.pyplot as plt
import numpy as np
from data_access.file_buffer import FileBuffer
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
     
    transducer_coefficient = 1.0 / (20 * 0.83)
    sensitivity = 2.0 * 20 / (2.0 ** 32)
    # data = -(data - np.mean(data)) * sensitivity / transducer_coefficient
    data = -(data) * sensitivity / transducer_coefficient
 
    return np.array(data)

def read_in_segy(files, begin_trim=0, end_trim=0):
    return SegyFileBuffer(files, begin_trim, end_trim)

class SegyFileBuffer(FileBuffer):
    
    def __init__(self, files, begin_trim=0, end_trim=0, trans_coeff=1):        
        self.headers = [read_segy_head(f) for f in files]
        FileBuffer.__init__(self, files, begin_trim, end_trim)
        
    def read_proxy(self, filename, head, offset=0, samples='all'):
        return read_segy_data(filename, head, offset, samples)
        