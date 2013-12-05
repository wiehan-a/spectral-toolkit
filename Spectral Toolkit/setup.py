from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy, os, struct

'''

    This script compiles the Cython modules for this project.
    
    If installation is done from source, and compiled extensions
    are not distributed with it, this script should be invoked
    with 'python setup.py build_ext --inplace' before running the 
    software for the first time.
    
    Ensure that the proper libraries such as OpenMP and FFTW are installed
    and available.

'''

class build_ext_subclass(build_ext):
    '''
    Extend the build_ext class to provide differential compiler options
    for e.g. OpenMP support.
    '''
    def build_extensions(self):
        if self.compiler.compiler_type == 'msvc':
            bitness = struct.calcsize("P") * 8
            print bitness
            for e in self.extensions:
                e.include_dirs = [numpy.get_include(), 
                                  os.path.join('fftw_wrapper'),]
                e.extra_compile_args = ['/openmp']
                e.libraries = [os.path.join({32 : 'fftw_32', 64: 'fftw_64'}[bitness], 'libfftw3-3')]
        else:
            for e in self.extensions:
                e.include_dirs = [numpy.get_include(), 
                                  os.path.join('fftw_wrapper'),]
                e.extra_compile_args = ['-fopenmp']
                e.extra_link_args = ['-fopenmp', '-lm', '-lfftw3', '-lfftw3_threads']
                

        build_ext.build_extensions(self)

ext_modules = [Extension("data_processing.sigproc", ["data_processing/sigproc.pyx"]),
               Extension("data_processing.convolution", ["data_processing/convolution.pyx"]),
               Extension("data_processing.windowing", ["data_processing/windowing.pyx"]),
                Extension("data_processing.spectral_estimation", ["data_processing/spectral_estimation.pyx"]),
                Extension("data_processing.discontinuity_tool", ["data_processing/discontinuity_tool.pyx"]),
                Extension("data_processing.peak_detection", ["data_processing/peak_detection.pyx"]),
                Extension("fftw_wrapper.fftw_py", ["fftw_wrapper/fftw_py.pyx"]),
               
                ]

setup(
  name='Spectral Toolkit',
  cmdclass={'build_ext': build_ext_subclass},
  ext_modules=ext_modules
)
