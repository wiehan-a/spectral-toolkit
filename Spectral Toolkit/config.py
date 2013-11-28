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
    with open(DB_FILENAME, 'w') as f:
       f.write(json.dumps(db, sort_keys=True, indent=4, separators=(',', ': '), cls=DateTimeJSONEncoder))
       
def db_add_entry(filename, source, component, sampling_rate, start_time, end_time):
    db[filename] = {
                        'source' : source,
                        'component' : component,
                        'start_time' : start_time,
                        'end_time' : end_time,
                        'sampling_rate' : sampling_rate
                       }
    
def db_get_entry_count():
    return len(db)

def db_load_data(filenames):
    pass

def db_discard_data(filenames):
    pass
    

try:
    with open(DB_FILENAME) as f:
        db = json.loads(f.read(), cls=DateTimeJSONDecoder)
except IOError:
    initialize_db()
except ValueError:
    initialize_db()

try:
    with open(CONFIG_FILENAME) as f:
        config_db = json.loads(f.read())
        print config_db['proxies']
except IOError:
    initialize_config()
except ValueError:
    initialize_config()
