from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy, os

'''

    This script compiles the Cython modules for this project.
    
    If installation is done from source, and compiled extensions
    are not distributed with it, this script should be invoked
    with 'python setup.py build_ext --inplace' before running the 
    software for the first time.

'''

class build_ext_subclass(build_ext):
    '''
    Extend the build_ext class to provide differential compiler options
    for e.g. OpenMP support.
    '''
    def build_extensions(self):
        if self.compiler.compiler_type == 'msvc':
            for e in self.extensions:
                e.include_dirs = [numpy.get_include(), 
                                  os.path.join('external_libs', 'include', 'msvc_2008'),
                                  os.path.join('external_libs', 'include'),
                                  os.path.join('external_libs', 'include', 'win')]
                e.extra_compile_args = ['/openmp']
                e.libraries = [os.path.join('libfftw3-3')]
        else:
            for e in self.extensions:
                e.extra_compile_args = ['-fopenmp']
                e.extra_link_args = ['-fopenmp'],
                

        build_ext.build_extensions(self)

ext_modules = [Extension("data_processing.sigproc", ["data_processing/sigproc.pyx"]),
               Extension("data_processing.convolution", ["data_processing/convolution.pyx"])]

setup(
  name='Spectral Toolkit',
  cmdclass={'build_ext': build_ext_subclass},
  ext_modules=ext_modules
)
