import sqlite3
import os

class Config:
    CONFIGS = {
        'dev': {
         'database_folder': 'database',
         'storage_file': 'storage.json',
         'db_file': 'parking_lot.sqlite',
         'table_name': 'parking',
         'table_fields': [
             ['slot_id','INTEGER PRIMARY KEY'],
             ['slot_status'],
             ['registration'],
             ['color'],
             ['timestamp', 'INTEGER']
          ]
      }
    }
    
    def __init__(self, env='dev'):
        self._define_properties(env)

    # private
    def _define_properties(self, collection_env):
        for (key, value) in self.CONFIGS[collection_env].items():
            setattr(self, key, value)

class Storage:
    def _prepare_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        
#curr_path = os.getcwd()
#actual_path = os.path.join(curr_path,"database")
#print(actual_path)

class DBStorage(Storage):

    def __init__(self, config):
        self._prepare_dir(os.path.join(os.getcwd(),config.database_folder))
        self.conn = sqlite3.connect(os.path.join(os.getcwd(), config.database_folder, config.db_file))
        self.conn.text_factory = str
        self.conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        self.curr = self.conn.cursor()
        self.curr.execute(
            'create table if not exists {} ({})'.format(
                config.table_name, ','.join([' '.join(k) for k in config.table_fields])
            )
        )
    
    def create_table(self,space):
        try:
            for each in range(1, space+1):
                self.curr.execute(
                'INSERT INTO {} ({}) VALUES ( {} );'.format(
                    config.table_name,
                    'slot_status', '?'
                ),['Free'])
            self.conn.commit()
        except:
            print("Inser exception raised!")
            
        return 'Created a parking lot with ' + str( space ) + ' slots'
    @property
    def last_event(self):
        """select * from events ORDER BY timestamp COUNT 1"""
        self.curr.execute(
            'select slot_id  from {} ORDER BY slot_id desc LIMIT 1'.format(
                config.table_name)
        )
        last_event = self.curr.fetchall()
        return last_event
    
    @property
    def events(self):
        """select * from events ORDER BY timestamp;"""
        self.curr.execute(
            'select * from {} ORDER BY timestamp'.format(
                config.table_name),
        )
        events = self.curr.fetchall()
        return events
    
    def allocate_space(self,reason,registration,color):
        try:
            if(reason == 'park'):
                sql = ''' UPDATE {} SET slot_status = ?, registration = ?, color = ?  WHERE slot_id = ?'''.format(config.table_name)
                self.curr.execute(sql,['busy', registration, color, 1])
                self.conn.commit()
            else:
                raise Exception
        except Exception as e:
            print(e)
            
        return 'Allocated slot number: 1'
    
    def vacate_slot(self,reason, slot):
        try:
            if(reason == 'leave'):
                sql = ''' UPDATE {} SET slot_status = ?, registration = ?, color = ?  WHERE slot_id = ?'''.format(config.table_name)
                self.curr.execute(sql,['Free', None, None, slot])
                self.conn.commit()
            else:
                raise Exception
        except Exception as e:
            print(e)
            print('Kindly check your command!')
            
        return 'Slot is vacated'
    
            
    

if __name__ == '__main__':
    config = Config()
    print(config.table_fields[0][0])
    demo = DBStorage(config)
    #print(demo.create_table(2))
    #park KA-01-HH-1234 White
    #Allocated slot number: 1
    #print(demo.allocate_space('park','KA-01-HH-1234', 'White'))
    print(demo.vacate_slot('leave', 1))
    print(demo.events)
    #print(demo.last_event)
    
    
   
    
    
