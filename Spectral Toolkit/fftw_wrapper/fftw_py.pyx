'''
Created on Sep 26, 2013

@author: Wiehan
'''
from cfftw cimport * 
import numpy as np
cimport numpy as np

def import_wisdom():
    print 'Importing wisdom.'
    fftw_import_wisdom_from_filename('fftw_wisdom')
        
def export_wisdom():
    print 'Exporting wisdom.'
    fftw_export_wisdom_to_filename('fftw_wisdom')

def real_fft(np.ndarray[np.float64_t, ndim=1] x, N):
    '''
    Performs the N-point FFT of the real sequence x.
    
    Returns new numpy.complex128 array of length N/2 + 1
    '''
    cdef np.ndarray[np.complex128_t] out_buffer = np.empty(shape=(N / 2 + 1), dtype=np.complex128)
    
    if(len(x) < N):
        x = np.ascontiguousarray(np.hstack((x, np.zeros(N - len(x)))))
    
    cdef fftw_plan forward_plan = fftw_plan_dft_r2c_1d(N, < double *> x.data, < fftw_complex *> out_buffer.data, FFTW_ESTIMATE)
    fftw_execute(forward_plan)
    return out_buffer
