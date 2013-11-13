'''
Created on Sep 25, 2013

@author: Wiehan
'''

ctypedef double fftw_complex[2]

cdef extern from 'fftw3.h':
	# Double precision plans
	ctypedef struct fftw_plan_struct:
		pass

	ctypedef fftw_plan_struct * fftw_plan
	
	fftw_plan fftw_plan_dft_r2c_1d(int n, double * input, fftw_complex * output, unsigned flags) nogil
	fftw_plan fftw_plan_dft_c2r_1d(int n, fftw_complex *input, double *output, unsigned flags) nogil
	                                
	void * fftw_malloc(size_t n) nogil
	void fftw_free(void *p) nogil
	double *fftw_alloc_real(size_t n) nogil
	fftw_complex *fftw_alloc_complex(size_t n) nogil
	
	void fftw_execute( fftw_plan plan) nogil
	void fftw_execute_dft_r2c( fftw_plan p, double *input, fftw_complex *output) nogil
	void fftw_execute_dft_c2r( fftw_plan p, fftw_complex *input, double *output) nogil
	void fftw_destroy_plan(fftw_plan plan) nogil
	
	int fftw_export_wisdom_to_filename( char *filename)
	int fftw_import_wisdom_from_filename( char *filename)

	int fftw_init_threads()
	void fftw_plan_with_nthreads(int nthreads)

# Direction enum
cdef enum:
	FFTW_FORWARD = -1
	FFTW_BACKWARD = 1

# Documented flags
cdef enum:
	FFTW_MEASURE = 0
	FFTW_DESTROY_INPUT = 1
	FFTW_UNALIGNED = 2
	FFTW_CONSERVE_MEMORY = 4
	FFTW_EXHAUSTIVE = 8
	FFTW_PRESERVE_INPUT = 16
	FFTW_PATIENT = 32
	FFTW_ESTIMATE = 64