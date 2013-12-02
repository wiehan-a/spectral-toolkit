'''
Created on Dec 2, 2013

@author: Wiehan
'''

import os, datetime, struct
from sansa import SansaFileBuffer
from config import *

local_storage_path = '/SANSA_LOCAL/'

if not os.path.exists(config_db['data_folder'] + local_storage_path):
    if not os.path.exists(config_db['data_folder']):
        os.mkdir(config_db['data_folder'])
    os.mkdir(config_db['data_folder'] + local_storage_path)
    
def make_file_name(start, end, comp, tag):
    return config_db['data_folder'] + local_storage_path + '{:%Y.%m.%d.%H.%M.%S}'.format(start) + '.' + '{:%Y.%m.%d.%H.%M.%S}'.format(end) + '.' + tag + '.' + comp
    

def import_files(filenames, tag, sampling_rate):
    for filename in filenames:
        with open(filename, "r") as f:
            
            comp_1_file = open('tmp1', 'wb')
            comp_2_file = open('tmp2', 'wb')
            comp_3_file = open('tmp3', 'wb')
            
            first_line = True
            for line in f:
                line = line.strip().split(",")
                if len(line) > 1:
                    
                    if first_line:
                        start_time = datetime.datetime.strptime(line[0], "%Y-%m-%d %H:%M:%S.%f").replace(microsecond=int(line[1]))
                        first_line = False
                        
                    comp_1_file.write(struct.pack('f', float(line[2])))
                    comp_2_file.write(struct.pack('f', float(line[3])))
                    comp_3_file.write(struct.pack('f', float(line[4])))
                    
            
            comp_1_file.close()
            comp_2_file.close()
            comp_3_file.close()
            
            end_time = datetime.datetime.strptime(line[0], "%Y-%m-%d %H:%M:%S.%f").replace(microsecond=int(line[1]))
            
            n1 = make_file_name(start_time, end_time, "COMP1", tag)
            n2 = make_file_name(start_time, end_time, "COMP2", tag)
            n3 = make_file_name(start_time, end_time, "COMP3", tag)
            
            try:
                os.rename('tmp1', n1)
                os.rename('tmp2', n2)
                os.rename('tmp3', n3)
            except OSError:
                # since Windows bugs out if dest already exists
                os.remove(n1)
                os.remove(n2)
                os.remove(n3)
                
                os.rename('tmp1', n1)
                os.rename('tmp2', n2)
                os.rename('tmp3', n3)
            
            db_add_entry(n1, 'SANSA_LOCAL', 'COMP1', sampling_rate, start_time, end_time, False, tag=tag)
            db_add_entry(n2, 'SANSA_LOCAL', 'COMP2', sampling_rate, start_time, end_time, False, tag=tag)
            db_add_entry(n3, 'SANSA_LOCAL', 'COMP3', sampling_rate, start_time, end_time, False, tag=tag)
            save_db()
                
                

def read_in_filenames(filenames, start_trim=0, end_trim=0):
    return SansaFileBuffer(filenames, start_trim, end_trim)
