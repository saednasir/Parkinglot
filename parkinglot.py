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
    
    def create_parking_lot(self,msg,space):
        try:
            if(msg == 'create_parking_lot'):
                for each in range(1, space+1):
                    self.curr.execute(
                    'INSERT INTO {} ({}) VALUES ( {} );'.format(
                        config.table_name,
                        'slot_status', '?'
                    ),['Free'])
                self.conn.commit()
                return 'Created a parking lot with {} slots'.format(space)
            else:
                return 'Kindly check your command!'
        except:
            print("Insert exception raised!")
            
    
    @property
    def show_status(self):
        """select * from events ORDER BY timestamp;"""
        self.curr.execute(
            'select slot_id, registration, color from {} WHERE slot_status = ?'.format(
                config.table_name, '?'),['Busy']
        )
        data = self.curr.fetchall()
        return data
    
    @property
    def nearest_vacant_slot(self):
        """select * from events ORDER BY timestamp COUNT 1"""
        """ select  timestamp from {} ORDER BY timestamp LIMIT 1 """
        self.curr.execute(
            'select slot_id from {} WHERE slot_status = ? ORDER BY slot_id LIMIT 1'.format(
                config.table_name, '?'), ['Free']
        )
        vacant_slot = self.curr.fetchall()
        #vacant_slot = []
        return vacant_slot
    
    def allocate_space(self,reason,registration,color):
        try:
            if(reason == 'park'):
                get_reg_status = self.unique_registrations(registration)
                if(get_reg_status):
                    return 'Vehicle with given registration is already parked at slot number: {}'.format(get_reg_status[0]['slot_id'])
                status = self.nearest_vacant_slot
                if(status):
                    slot_no = status[0]['slot_id']
                    sql = ''' UPDATE {} SET slot_status = ?, registration = ?, color = ?  WHERE slot_id = ?'''.format(config.table_name)
                    self.curr.execute(sql,['Busy', registration, color, slot_no])
                    self.conn.commit()
                    return 'Allocated slot number: {}'.format(slot_no)
                else:
                    return 'Sorry, parking lot is full'
            else:
                return 'Kindly check your command!'
        except Exception as e:
            print(e)
    
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
    
    
    def all_registrations_with_color(self, msg , color):
        if(msg == 'registration_numbers_for_cars_with_colour'):
            
            """select * from events ORDER BY timestamp;"""
            self.curr.execute(
                'select registration from {} WHERE color = ?'.format(
                    config.table_name, '?'),[color]
            )
            data = self.curr.fetchall()
            if(data):
                return data
        else:
            return 'Kindly check your command!'
        return 'Not found'

    def all_slots_with_color(self, msg , color):
        if(msg == 'slot_numbers_for_cars_with_colour'):
            
            """select * from events ORDER BY timestamp;"""
            self.curr.execute(
                'select slot_id from {} WHERE color = ?'.format(
                    config.table_name, '?'),[color]
            )
            data = self.curr.fetchall()
            if(data):
                return data
        else:
            return 'Kindly check your command!'
        return 'Not found'
    
    def slot_with_registration(self, msg , reg):
        if(msg == 'slot_number_for_registration_number'):
            
            """select * from events ORDER BY timestamp;"""
            self.curr.execute(
                'select slot_id from {} WHERE registration = ?'.format(
                    config.table_name, '?'),[reg]
            )
            data = self.curr.fetchall()
            if(data):
                return data
        else:
            return 'Kindly check your command!'
        return 'Not found'
    
    def unique_registrations(self,reg):
        """select * from events ORDER BY timestamp;"""
        self.curr.execute(
            'select slot_id from {} WHERE registration = ?'.format(
                config.table_name, '?'),[reg]
            )
        data = self.curr.fetchall()
        return data
            
    

if __name__ == '__main__':
    config = Config()
    demo = DBStorage(config)
    try:
        #print(demo.create_parking_lot('create_parking_lot',1))
        print(demo.allocate_space('park','KA-01-wwHH-1234', 'White'))
        #print(demo.unique_registrations('KA-01-wwwwwHH-1234'))
    except Exception as e:
        print(e)
        
    #print(demo.allocate_space('park','KA-01-HH-1234', 'White'))
    #print(demo.vacate_slot('leave', 1))
    #print(demo.slot_with_registration('slot_number_for_registration_number', 'KA-01-HH-1234'))
    #print(demo.all_slots_with_color('slot_numbers_for_cars_with_colour', 'White'))
    #print(demo.all_registrations_with_color('registration_numbers_for_cars_with_colour', 'Wheite'))
    #print(demo.show_status)
    #print(demo.nearest_vacant_slot)
    #print(demo.last_event)
    
    
   
    
    
