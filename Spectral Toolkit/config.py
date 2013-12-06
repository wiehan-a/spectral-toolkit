'''
Created on Sep 20, 2013

@author: Wiehan
'''

import json, datetime
from time import mktime

class DateTimeJSONEncoder(json.JSONEncoder):
    
    '''
        Includes datetime support, which is not part of the base
        JSON spec. This is OK, since the format is not meant to
        be interoperable with other systems, and does not break
        anything if unaware systems read it.
    '''

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return 'datetime(' + str(mktime(obj.timetuple())) + ')'

        return json.JSONEncoder.default(self, obj)
    
class DateTimeJSONDecoder(json.JSONDecoder):
    
    '''
        Reverse of DateTimeJSONEncoder
    '''
    
    def __init__(self, **kwparams):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object, **kwparams)
        
    def dict_to_object(self, d):
        for key, value in d.items():
            if isinstance(value, str) or isinstance(value, unicode):
                if value.startswith('datetime('):
                    d[key] = datetime.datetime.fromtimestamp(float(value[9:-1]))
        return d


DB_FILENAME = 'database.json'
CONFIG_FILENAME = 'config.json'

db_default = {}

config_db_default = {
                        'data_folder' : 'Downloaded Data'
                    }

config_db = {}
db = {}

memory_library = {}

def initialize_config():
    global config_db
    print 'Intializing config file.'
    config_db = config_db_default
    save_config()
    
def initialize_db():
    global db
    print 'Intializing database.'
    db = db_default
    save_db()

def save_config():
    with open(CONFIG_FILENAME, 'w') as f:
       f.write(json.dumps(config_db, sort_keys=True, indent=4, separators=(',', ': ')))
       
def save_db():
    print "saving db"
    global db
    print id(db)
    with open(DB_FILENAME, 'w') as f:
       f.write(json.dumps(db, sort_keys=True, indent=4, separators=(',', ': '), cls=DateTimeJSONEncoder))
    print id(db)
    print "done saving db"
       
def reload_db():
    global db
    db.clear()
    try:
        with open(DB_FILENAME) as f:
            
            db2 = json.loads(f.read(), cls=DateTimeJSONDecoder)
            db.update(db2)
            
            for key, value in db.items():
                if value.has_key('missing_samples') and value['missing_samples']:
                    value['num_missing_samples'] = count_missing_samples(key)
                else: 
                    value['num_missing_samples'] = 0
                
                if not value.has_key('tag'):
                    value['tag'] = ''
                    
    except IOError:
        initialize_db()
    except ValueError:
        initialize_db()
       
def db_add_entry(filename, source, component, sampling_rate, start_time, end_time, missing_samples=False, missing_annotations=None, tag=None):
    global db
    db[filename] = {
                        'source' : source,
                        'component' : component,
                        'start_time' : start_time,
                        'end_time' : end_time,
                        'sampling_rate' : sampling_rate,
                        'missing_samples' : missing_samples,
                       }
    if missing_annotations is not None:
        db[filename]['annotations_file'] = missing_annotations
        
    if tag is not None:
        db[filename]['tag'] = tag
        
def load_annotations(filename):
    global db
    if db[filename].has_key('annotations_file'):
        with open(db[filename]['annotations_file']) as f:
            return json.loads(f.read())
    return []
    
def db_get_entry_count():
    return len(db)

        # need to query db by time: get a list of files whose end times > start and start_times < end
        # sort by time
        # then figure out how many samples in and out
        
        
def query_db_by_time(source, start_time, end_time, components_filter=[]):
    '''
    return file lists and trims
    '''
    
    files = [key for key, value in db.items() 
                            if value['source'] == source
                                and (value['end_time'] > start_time and value['start_time'] < end_time) ]
    
    components = list(set([ db[file]['component'] for file in files ]))
    
    print components
    
    files_by_component = {component : [] for component in components}
    
    for file in files:
        files_by_component[db[file]['component']].append(file)
        
    for component in components:
        files_by_component[component] = sorted(files_by_component[component], key=lambda f: db[f]['start_time'])
        
    first_file = files_by_component[components[0]][0]
    last_file = files_by_component[components[0]][-1]
    sr = db[first_file]['sampling_rate']
    start_sample = int(sr * (start_time - db[first_file]['start_time']).total_seconds())
    end_sample = int(-1 * sr * (end_time - db[last_file]['end_time']).total_seconds())

    return files_by_component, start_sample, end_sample
    

def count_missing_samples(filename):
    annotations = load_annotations(filename)
    missing = 0
    for interval in annotations:
        missing += interval[1] - interval[0]
    return int(missing)


reload_db()
                


try:
    with open(CONFIG_FILENAME) as f:
        
        config_db = json.loads(f.read())
        if not config_db.has_key('transducer_coefficient'):
            config_db['transducer_coefficient'] = 30
        save_config()
            
except IOError:
    initialize_config()
except ValueError:
    initialize_config()
    
    
import data_access
maintenance_logs = {source : [] for source in data_access.data_engines}
maintenance_logs_filenames = {source : source + ".log" for source in data_access.data_engines}

def load_maintenance_logs():
    for key in maintenance_logs.keys():
        try:
            with open(maintenance_logs_filenames[key], 'r') as f:
                maintenance_logs[key] = json.load(f)
        except:
            pass
        
def save_maintenance_logs():
    for key in maintenance_logs.keys():
        try:
            with open(maintenance_logs_filenames[key], 'w') as f:
                json.dump(maintenance_logs[key], f, sort_keys=True, indent=4, separators=(',', ': '))
        except:
            pass
        
load_maintenance_logs()
