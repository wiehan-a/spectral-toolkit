'''
Created on Oct 24, 2013

@author: Wiehan
'''

from config import db
import os

def make_matlab(f_map):
    
    prototype_f = f_map[f_map.keys()[0]][0]
    prototype_e = f_map[f_map.keys()[0]][-1]
    
    offset = {'SANSA' : '0', 'LSBB' : '240'}[db[prototype_f]['source']]
    numtype = {'SANSA' : '\'float64\'', 'LSBB': '\'int32\''}[db[prototype_f]['source']]
    fix_coefficient = {'SANSA' : '1', 'LSBB': '(2*20 /( 2^32 ))/(1/(20*0.83))'}[db[prototype_f]['source']]
    
    p = "% Auto-generated script\n"
    p += "% Origin: " + db[prototype_f]['source'] + "\n"
    p += "% Start time: " + str(db[prototype_f]['start_time']) + "\n"
    p += "% End time: " + str(db[prototype_e]['end_time']) + "\n\n"
    
    p += "sampling_rate =  " + str(db[prototype_e]['sampling_rate']) + ";\n\n"
    
    p += "hold on;\n\n"
    
    for c in f_map.keys():
        fname = "files_" + c
        signame = "signal_" + c
        p += fname + " = {\'"
        for idx in xrange(len(f_map[c]) - 1):
            p += os.path.abspath(f_map[c][idx]) + "\'; \'"
        p += os.path.abspath(f_map[c][-1]) + "\'};\n"
        p += signame + " = [];\n"
        p += "for j=1:length(" + fname + ")\n"
        p += "    file = char(" + fname + "(j));\n "
        p += '''
    fid = fopen(file, 'r');
    status = fseek(fid,''' + offset + ''', 'bof');
    info = dir(file);
    '''
        p += signame + " = [" + signame + '''; fread(fid, info.bytes - 240, ''' + numtype + ''')];\n'''   
        p += "    fclose(fid);\n"
        p += "end\n"
        p += signame + " = " + signame + "*" + fix_coefficient + ";\n"
        p += "plot(" + signame + ");\n\n"
    return p

def double_escape(filename):
#     return ('\\\\').join(filename.split('\\\\'))
    return filename

    
def make_numpy(f_map):
    
    prototype_f = f_map[f_map.keys()[0]][0]
    prototype_e = f_map[f_map.keys()[0]][-1]
    
    offset = {'SANSA' : '0', 'LSBB' : '240'}[db[prototype_f]['source']]
    numtype = {'SANSA' : '\'float64\'', 'LSBB': '\'i4\''}[db[prototype_f]['source']]
    fix_coefficient = {'SANSA' : '1', 'LSBB': '(2*20 /( 2.0**32 ))/(1/(20*0.83))'}[db[prototype_f]['source']]
    bytes = {'SANSA' : '8', 'LSBB': '4'}[db[prototype_f]['source']]
    
    p = "# Auto-generated script\n"
    p += "# Origin: " + db[prototype_f]['source'] + "\n"
    p += "# Start time: " + str(db[prototype_f]['start_time']) + "\n"
    p += "# End time: " + str(db[prototype_e]['end_time']) + "\n\n"
    
    p += "import numpy as np\n"
    p += "import matplotlib.pyplot as plt\n"
    
    p += "sampling_rate =  " + str(db[prototype_e]['sampling_rate']) + "\n\n"
    
    for c in f_map.keys():
        fname = "files_" + c
        signame = "signal_" + c
        p += fname + " = [r'"
        for idx in xrange(len(f_map[c]) - 1):
            p += os.path.abspath(double_escape(f_map[c][idx])) + "', r'"
        p += os.path.abspath(double_escape(f_map[c][-1])) + "']\n"
        p += signame + " = np.array([])\n"
        p += "for f in " + fname + ":\n"
        p += "    with open(f, 'rb') as f:\n"
        p += "        f.seek(" + offset + ")\n"
        p += "        buffer = f.read()\n"
        p += "        data = np.ndarray(shape=(len(buffer)/"+bytes+",), dtype=" + numtype + ", buffer=buffer)\n"
        p += "        " + signame + " = np.hstack((" + signame + ", data))\n"
        p += signame + " = " + signame + "*" + fix_coefficient + "\n"
        p += "plt.plot(" + signame + ")\n\n"
    p += "plt.show()\n\n"
    return p
