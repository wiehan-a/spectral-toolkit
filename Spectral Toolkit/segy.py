'''
Created on Jun 13, 2013

@author: Wiehan
'''
from __future__ import division

from struct import *
import array
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig
from numpy.fft.fftpack import ifft
from numpy.lib.function_base import meshgrid

def read_segy_head(filename):
    format_string = "<iiiiiiihhhhiiiiiiiihhiiiihhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhBBBBBBBBBBBBBBBBBBhihhhhhhhhfHhiii"
    
    head = {}
    f = open(filename, 'rb')
    data = unpack(format_string, f.read(240))
    f.close()
    
    head['header_bytes'] = 240
    head['data_form'] = data[91]
    head['sample_count'] = max(data[102], data[38])
    head['sample rate'] = 1 / (data[39] * 1e-6)
    
    return head

def read_segy_data(filename, head):
    f = open(filename, 'rb')
    f.seek(head['header_bytes'])
    
    # Note: this assumes little endianness
    i = head['data_form']
    
    
    data = np.ndarray(shape=(head['sample_count'],), dtype=['i2', 'i4', 'float64'][i], buffer=f.read())
    f.close()
     
    transducer_coefficient = 1 / (20 * 0.83)
    sensitivity = 2 * 20 / (2 ** 32)
    data = -(data - np.mean(data)) * sensitivity / transducer_coefficient
 
    return np.array(data)

def read_in_segy(files):
    data = np.zeros(0)
    for filename in files:
        head = read_segy_head(filename)
        data = np.hstack((data, read_segy_data(filename, head)))
    return data

def download(date, verbose=True):
    pass

if __name__ == '__main__':
    import time, util
    time.clock()
    
    files = ["2011.08.04-00.00.00.FR.MGN.00.CGE.SEGY", "2011.08.05-00.00.00.FR.MGN.00.CGE.SEGY",  "2011.08.06-00.00.00.FR.MGN.00.CGE.SEGY"]
    #files = ["2012.08.02-23.59.59.FR.MGN.00.CGE.SEGY"]
    data = np.zeros(0)
    for filename in files:
        head = read_segy_head(filename)
        data = np.hstack((data, read_segy_data(filename, head)))
       
    print "Finished reading after: ", time.clock()
    ds = data
    for _ in xrange(3):
        ds = sig.decimate(ds, 5)
    ds = sig.decimate(ds, 2)
#     ds = np.hstack((ds, np.zeros(1)))
    print "Data length after downsample: ", len(data)
    util.prime_factors(len(data))
    print "Finished downsampling after: ", time.clock()
    
    import sigproc
#     a = sigproc.linear_predictor(ds, order=1)
#     w, h = sig.freqz(np.hstack((np.array([1]), a)))
#     plt.plot(w, np.log10(1/np.abs(h)),'r')
#     a = sigproc.linear_predictor(ds, order=2)
#     w, h = sig.freqz(np.hstack((np.array([1]), a)))
#     plt.plot(w, np.log10(1/np.abs(h)),'c')
#     a = sigproc.linear_predictor(ds, order=500)
#     w, h = sig.freqz(np.hstack((np.array([1]), a)))
#     plt.plot(w, np.log10(1/np.abs(h)),'b')
#     a = sigproc.linear_predictor(ds, order=1000)
#     w, h = sig.freqz(np.hstack((np.array([1]), a)))
#     plt.plot(w, np.log10(1/np.abs(h)),'g')
#     plt.legend(["p = 1","p = 2","p = 500","p = 1000"])
#     plt.show()
    a = sigproc.predict_signal(ds, 10)
    
    print "Finished predicting after: ", time.clock()
    from scipy.signal.signaltools import lfilter
    #ds = lfilter([1, a[0]], [1], ds)
#     plt.plot(ds)
#     plt.show()
    #data = sig.lfilter([1, 0, -16, 0,  16, 0, -1], [-16], data)
#     plt.plot(np.abs(f_sig))
#     plt.show()
    
#     import frequency as fr
#  
#     #pb = fr.bartlett(ds, 337*2*5, zp_fact=3)
# #     print pb.shape
#     print "Finished bartlett after: ", time.clock()
#     #pp = fr.periodogram(data, window=None, zp_fact=10)
#     p = fr.periodogram(ds, window=sig.blackman, zp_fact=1)
# #     print p.shape
# #     print "Finished periodogram after: ", time.clock()
#     
#     N = len(p)
#     ref = 125/2
#     #1mhz tot 10mhz
#     start = int(N*(1e-3)/ref)
#     end = int(N*(10e-3)/ref)
#     t = np.arange(0, 125/2, (125/2) / (N - 0.5))
#     
#     p = p[start:end]
#     t = t[start:end]
# #     tp = np.arange(0, 75, (75) / (len(p) - 0.5))
# # #     
# #     start = int(0.1 * N)
# #     end = int(0.8 * N)
#      
#     # pp = pp[start:end]
# #     pb = pb[start:end]
# #     p = p[start:end]
# #     t = t[start:end]
#      
#     do_log = True
#     if do_log:
#         # pp = 10 * np.log10(pp)
#         #p = 10 * np.log10(p)
#         p = 10 * np.log10(p)
# #     # plt.plot(t, pp, 'c')
# # #     plt.plot(t, p, 'b')
#     plt.plot(t, p, 'g')
# #     plt.plot(tp, p, 'g')
#     plt.show()



#     from mpl_toolkits.mplot3d import axes3d, Axes3D
#     
#     _, Z = fr.stft(data, 5*181, zp_fact=1)
#     Z = np.transpose(Z)
#     #Z = 10*np.log10(Z)
#     print Z.shape
#     fig = plt.figure()
#  
# #     im = plt.pcolor(Z, vmin=Z.min(), vmax=Z.max())
# #      
# #     cb = fig.colorbar(im, ax=ax)
#     ax = Axes3D(fig)
#     
#     x, y = np.meshgrid(np.arange(0, Z.shape[1]), np.arange(0, Z.shape[0]))
#       
#     p = ax.plot_surface(x, y, Z)
#     plt.show()

