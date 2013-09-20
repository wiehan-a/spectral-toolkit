'''
Created on Sep 20, 2013

@author: Wiehan
'''

import json

DB_FILENAME = 'database.json'
CONFIG_FILENAME = 'config.json'

db_default = {}
config_db_default = {
                     'data_folder' : 'Downloaded Data'
                    }

config_db = {}
db = {}


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
       f.write(json.dumps(db, sort_keys=True, indent=4, separators=(',', ': ')))

try:
    with open(DB_FILENAME) as f:
        db = json.loads(f.read())
except IOError:
    initialize_db()
except ValueError:
    initialize_db()

try:
    with open(CONFIG_FILENAME) as f:
        config_db = json.loads(f.read())
except IOError:
    initialize_config()
except ValueError:
    initialize_config()

