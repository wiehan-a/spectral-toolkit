'''
Created on Oct 24, 2013

@author: Wiehan
'''

from config import db
import os

def make_matlab(params, sr, f_map):
    
    p = "% Auto-generated script\n"
    p += "% Start time: " + str(params['start_time']) + "\n"
    p += "% End time: " + str(params['end_time']) + "\n\n"
    
    p += "sampling_rate =  " + str(sr) + ";\n\n"
    
    p += "file = '"+f_map+".data';\n "
    p += '''
fid = fopen(file, 'r');
status = fseek(fid, 0, 'bof');
info = dir(file);
data = fread(fid, info.bytes, 'float64');
frequencies = (sampling_rate/2)*[0:length(data)-1]/length(data);
plot(frequencies, 10*log10(data));
    '''
    return p

def double_escape(filename):
#     return ('\\\\').join(filename.split('\\\\'))
    return filename

    
def make_numpy(params, sr, f_map):
    
    print params
    
    p = "# Auto-generated script\n"
    p += "# Start time: " + str(params['start_time']) + "\n"
    p += "# End time: " + str(params['end_time']) + "\n\n"
    
    p += "import numpy as np\n\n"
    p += "import matplotlib.pyplot as plt\n"
    
    p += "sampling_rate =  " + str(sr) + "\n\n"
    
    p += 'data = None\n'
    p += "with open(r'"+f_map+".data', 'rb') as f:\n"
    p += "    buffer = f.read()\n"
    p += "    data = np.ndarray(shape=(len(buffer)/8,), dtype='float64', buffer=buffer)\n"
    p += "frequencies = (sampling_rate / 2) * np.arange(len(data)) / len(data)\n"
    p += "plt.plot(frequencies, 10*np.log10(data))\n"
    p += "plt.show()\n"
    
    return p
