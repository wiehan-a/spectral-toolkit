from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy, os

# class build_ext_subclass(build_ext):
#     '''
#     Extend the build_ext class to provide differential compiler options
#     for e.g. OpenMP support.
#     '''
#     def build_extensions(self):
#         if self.compiler.compiler_type == 'msvc':
#             for e in self.extensions:
#                 e.extra_compile_args = ['/openmp']
#         else:
#             for e in self.extensions:
#                 e.extra_compile_args = ['-fopenmp']
#                 e.extra_link_args = ['-fopenmp'],
#                 
# 
#         build_ext.build_extensions(self)

ext_modules = [Extension("test_fftw", ["test_fftw.pyx"], libraries=['libfftw3-3'])]

setup(
  name='Spectral Toolkit',
  cmdclass={'build_ext': build_ext},
  ext_modules=ext_modules
)
