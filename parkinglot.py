import os
import sys

try:
    import sqlite3
except ImportError as e:
    pip('install', 'sqlite3')
    import sqlite3


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
             ['color']
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
        """creates a table with defined space"""
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
        """shows all data """
        self.curr.execute(
            'select slot_id, registration, color from {} WHERE slot_status = ?'.format(
                config.table_name, '?'),['Busy']
        )
        data = self.curr.fetchall()
        return data
    
    @property
    def nearest_vacant_slot(self):
        """shows nearest available slot in ascending order"""
        
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
                vacant_slots = self.unique_slots(slot)
                if(vacant_slots):
                    if(vacant_slots[0]['slot_status'] == 'Busy'):
                        sql = ''' UPDATE {} SET slot_status = ?, registration = ?, color = ?  WHERE slot_id = ?'''.format(config.table_name)
                        self.curr.execute(sql,['Free', None, None, slot])
                        self.conn.commit()
                        return 'Slot number {} is free'.format(slot)
                    else:
                        return 'This slot is already Free!'
                else:
                    return 'Sorry, No slot found with this slot number!'
            else:
                return 'Kindly check your command!'
        except Exception as e:
            print(e)
            print('Kindly check your command!')
    
    
    def all_registrations_with_color(self, msg , color):
        """selects slots with given color"""
        if(msg == 'registration_numbers_for_cars_with_colour'):
            
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
        """selects slots with given color and msg;"""
        if(msg == 'slot_numbers_for_cars_with_colour'):
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
        """selects slots with given color and msg;"""
        if(msg == 'slot_number_for_registration_number'):
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
        """gives all reistration numbers"""
        self.curr.execute(
            'select slot_id from {} WHERE registration = ?'.format(
                config.table_name, '?'),[reg]
            )
        data = self.curr.fetchall()
        return data
    
    def unique_slots(self,slot):
        """gives all available slots;"""
        self.curr.execute(
            'select slot_status from {} WHERE slot_id = ?'.format(
                config.table_name, '?'),[slot]
            )
        data = self.curr.fetchall()
        return data
            
if __name__ == '__main__':
    config = Config()
    demo = DBStorage(config)
    try:
        
        #print(demo.unique_registrations('KA-01-wwwwwHH-1234'))
        #command = sys.argv[1]
        
        command = input()
        while(command != 'exit'):
            command_list = command.split()
            if(len(command_list) <=3):
                if(command_list[0] == 'create_parking_lot'):
                    print(demo.create_parking_lot(command_list[0], int(command_list[1])))
                elif(command_list[0] == 'park'):
                    print(demo.allocate_space(command_list[0], command_list[1], command_list[2]))
                elif(command_list[0] == 'leave'):
                    print(demo.vacate_slot(command_list[0], int(command_list[1])))
                elif(command_list[0] == 'status'):
                    ret_data = demo.show_status
                    print('Slot No. Registration     No Colour')
                    for each in ret_data:
                        print(each['slot_id'], end=' '*8)
                        print(each['registration'],end=' '*8)
                        print(each['color'])
                    #print(ret_data.keys())
                elif(command_list[0] == 'registration_numbers_for_cars_with_colour'):
                    reg_numbers = demo.all_registrations_with_color(command_list[0], command_list[1])
                    for each in reg_numbers:
                        print(each['registration'], end = ', ')
                    print('\n')
                elif(command_list[0] == 'slot_numbers_for_cars_with_colour'):
                    reg_numbers = demo.all_slots_with_color(command_list[0], command_list[1])
                    for each in reg_numbers:
                        print(each['slot_id'], end = ', ')
                    print('\n')
                elif(command_list[0] == 'slot_number_for_registration_number'):
                    reg_number = demo.slot_with_registration(command_list[0], command_list[1])
                    print(reg_number[0]['slot_id'])
                else:
                    print("Kindly check your cammand!")
                    break
                #print(command_list)
                command = input()
                
            else:
                print("Kindly check your cammand!")
                break
    except Exception as e:
        print(e)
    
    
   
    
    
