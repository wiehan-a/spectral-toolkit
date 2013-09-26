'''
Created on Sep 25, 2013

@author: Wiehan
'''

from cfftw cimport * 
import cython

def test():
    cdef fftw_complex * input, *output
    cdef fftw_plan p
    cdef size_t N = 500000000
    
    input = <fftw_complex *> fftw_malloc(cython.sizeof(fftw_complex) * N)
    output = <fftw_complex *> fftw_malloc(cython.sizeof(fftw_complex) * N)
    p = fftw_plan_dft_1d(N, input, output, FFTW_FORWARD, FFTW_ESTIMATE)
    
    fftw_execute(p)
    fftw_destroy_plan(p)
    fftw_free(input)
    
#     print input
#     print output