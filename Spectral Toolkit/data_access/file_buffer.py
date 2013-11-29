'''
Created on Nov 28, 2013

@author: Wiehan
'''

import numpy as np

class FileBuffer:
    
    def __init__(self, files, begin_trim=0, end_trim=0):
        self.files = files
        self.begin_trim = int(begin_trim)
        self.end_trim = int(end_trim)
        
        self.sample_counts = map(lambda x: x['sample_count'], self.headers)
        self.buffer_size = reduce(lambda x, y: x + y, self.sample_counts)
        
        for idx in xrange(1, len(self.files)):
            self.sample_counts[idx] = self.sample_counts[idx] + self.sample_counts[idx - 1]
        
        self.seek(0)
        
    def read_proxy(self, filename, head, offset=0, samples='all'):
        raise Exception()
        
    def __len__(self):
        return int(self.buffer_size - (self.begin_trim + self.end_trim))
    
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
                data[offset : offset + diff_in_file] = self.read_proxy(self.files[f], self.headers[f], offset=foffset, samples=diff_in_file)
                samples_remaining -= diff_in_file
                f += 1
                foffset = 0
                offset += diff_in_file
            else: #diff_in_file >= samples_remaining 
                print "file", f, "; sample", foffset, "to", samples_remaining+foffset, "in buffer", offset, 'to', offset + samples_remaining
                data[offset : offset + samples_remaining] = self.read_proxy(self.files[f], self.headers[f], offset=foffset, samples=samples_remaining)
                samples_remaining = 0
         
        
        return data
        
        
        
    def load_all_files(self):
        return self.read(self.buffer_size)