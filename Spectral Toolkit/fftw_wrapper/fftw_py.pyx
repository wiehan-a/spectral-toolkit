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
    
    fftw_init_threads()
    fftw_plan_with_nthreads(8)
    
    cdef np.ndarray[np.complex128_t] out_buffer = np.empty(shape=(N / 2 + 1), dtype=np.complex128)
    
    if(len(x) < N):
        x = np.ascontiguousarray(np.hstack((x, np.zeros(N - len(x)))))
    
    cdef fftw_plan forward_plan = fftw_plan_dft_r2c_1d(N, < double *> x.data, < fftw_complex *> out_buffer.data, FFTW_ESTIMATE)
    fftw_execute(forward_plan)
    fftw_destroy_plan(forward_plan)
    return out_buffer

def inverse_real_fft(np.ndarray[np.complex128_t, ndim=1] x, N):
    '''
    Performs the N-point inverse FFT of the real sequence x.
    
    Returns new numpy.float64 array of length N
    '''
    
    fftw_init_threads()
    fftw_plan_with_nthreads(8)
    
    cdef np.ndarray[np.float64_t] out_buffer = np.empty(shape=(N), dtype=np.float64)
    
    cdef fftw_plan forward_plan = fftw_plan_dft_c2r_1d(N, < fftw_complex *> x.data, < double *> out_buffer.data, FFTW_ESTIMATE)
    fftw_execute(forward_plan)
    return out_buffer/N
