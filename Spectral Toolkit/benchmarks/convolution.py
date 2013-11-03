'''
Created on Sep 24, 2013

@author: Wiehan
'''

from data_processing.convolution import *
import numpy as np
import time

from data_processing.filter_design import *

from data_access.segy import *

from data_processing.spectral_estimation import periodogram


data = None
with open(r'C:/Users/Wiehan/Desktop/toets.py.data', 'rb') as f:
    buffer = f.read()
    data = np.ndarray(shape=(len(buffer)/8,), dtype='float64', buffer=buffer)

arrx = np.log10(np.copy(data))
plt.figure(0)
plt.plot(arrx)

arry = design_low_pass_fir(0.05, 0.07*0.05, 120, 1)
x = fast_convolve_fftw_w(arrx, arry)
plt.figure(1)
plt.plot(x)

x = np.ascontiguousarray(np.copy(x[::10]))
plt.figure(2)
plt.plot(x)

arry = design_low_pass_fir(0.05, 0.07*0.05, 120, 1)
x = fast_convolve_fftw_w(x, arry)
plt.figure(3)
plt.plot(x)

x = np.ascontiguousarray(np.copy(x[::10]))
plt.figure(4)
plt.plot(x)

arry = design_low_pass_fir(0.05, 0.07*0.05, 120, 1)
x = fast_convolve_fftw_w(x, arry)
plt.figure(5)
plt.plot(x)

x = np.ascontiguousarray(np.copy(x[::10]))
plt.figure(6)
plt.plot(x)



plt.show()

