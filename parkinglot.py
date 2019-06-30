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
             ['slot', 'INTEGER PRIMARY KEY'],
             ['registration'],
             ['color'],
             ['timestamp', 'INTEGER']
          ]
      }
    }

class Storage:
    def __prepare_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        
#curr_path = os.getcwd()
#actual_path = os.path.join(curr_path,"database")
#print(actual_path)

class DBStorage(Storage):

    def __init__(self, config):
        self.__prepare_dir(os.path.join(os.getcwd(),config.database_folder))
        self.conn = sqlite3.connect(os.path.join(os.getcwd(), config.database_folder, config.db_file))
        self.conn.text_factory = str
        self.conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        self.curr = self.conn.cursor()
        self.curr.execute(
            'create table if not exists {} ({})'.format(
                config.table_name, ','.join([' '.join(k) for k in config.table_fields])
            )
        )
        
    @property
    def create_table(self,space):
        try:  
            self.curr.execute(
                'INSERT INTO {} ({}) VALUES ( {} );'.format(
                    config.table_name,
                    config.table_fields[0]
                ),  [slot for slot in range(1,space)])
            self.conn.commit()
        except:
            self.curr.execute('DROP TABLE {}'.format(config.table_name))
            self.conn.commit()
            self.curr.execute(
            'create table if not exists {} ({})'.format(
                config.table_name, ','.join([' '.join(k) for k in config.table_fields])
                )
            )
        return 'Created a parking lot with' + str(space) + 'slots'
            
    

if __name__ == '__main__':
    config = Config()
    demo = DBStorage(config)
   
    
    
