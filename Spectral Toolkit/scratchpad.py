'''
Created on Aug 2, 2013

@author: Wiehan
'''

import data_access.lsbb as lsbb
import datetime

# print lsbb.ftp_connection
# lsbb.ftp_connect()
# print lsbb.ftp_connection
# lsbb.ftp_close()
# print lsbb.ftp_connection

print lsbb.build_download_string(datetime.date(2012,3,8))

from scipy.fftpack import fft
import scipy.signal as sig
import numpy as np
import matplotlib.pyplot as plt
def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
 
from ftplib import FTP
ftp = FTP('193.52.13.2')  # connect to host, default port
ftp.login()  # user anonymous, passwd anonymous@
 
days = [4]
 
for d in days:
    ftp.cwd("pub/data/Daily_SEGY_Data/2012.08/2012.08.0"+str(d))
    s = ftp.nlst()  # list directory contents
    print s
    filename = [f for f in s if f.endswith('CGE.SEGY')][0]
    
    #print ftp.retrlines('LIST')
#     print filename
#     f = open(filename, 'wb')
#     bytes = 0
#       
    def callback(p):
        print len(p)
        ftp.abort()
        ftp.close()
       
    ftp.sendcmd('TYPE I')
    # print ftp.size('2011.08.04-00.00.00.FR.GGB.06.HHZ.SEGY')
    #ftp.retrbinary('RETR '+filename, callback, 240)
    import socket
    conn = ftp.transfercmd('RETR '+filename, rest=None)
    x = conn.recv(240)
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
    print x
    #print(conn.__class__)
    
#     f.close()
#     print "DONE"

# F = 1000.0
# fs = F*2*2
# N = 100*2
# T = N/fs
# 
# zp_factor = 100
# 
# time = np.arange(0, T, 1.0/fs)
# signal = np.sin(2*np.pi*F*time)
# windowed_signal = sig.blackman(N)*signal
# zp = np.hstack((signal, np.zeros(zp_factor*N)))
# windowed_zp = np.hstack((windowed_signal, np.zeros(zp_factor*N)))

# plt.plot(signal, 'r-')
# plt.plot(windowed_signal, 'g-')
# plt.show()
# 
# plt.plot(np.abs(fft(zp)), 'r-')
# plt.plot(np.abs(fft(windowed_zp)), 'g-')
# plt.show()

# import frequency as fr
# 
# 
# plt.plot(fr.periodogram(zp), 'r-')
# plt.plot(fr.periodogram(windowed_zp), 'g-')
# plt.show()
