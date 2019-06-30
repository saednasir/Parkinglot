try:
    import unittest
except ImportError as e:
    pip('install', 'unittest')
    import unittest
    
import unittest
from parkinglot import Config,DBStorage
#import parkinglot


class SimpleTest(unittest.TestCase): 
  
    # Returns True or False.  
    def test(self):
        config = Config()
        demo = DBStorage(config)
        demo.unique_slots(13)
        #self.assertTrue(demo.unique_slots(13),[]) 
  
if __name__ == '__main__': 
    unittest.main()
