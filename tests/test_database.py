import unittest

from database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database(_type='memory')
    
    def tearDown(self):
        self.db.__del__()
        del self.db
    
    def test_create_meta(self):
        '''
        Test database meta tables.
        CREATE TABLE users (username STRING, password STRING)
        Should create:
        table_meta:
            name -> users
            column1 ->
                name -> username
                type -> string
                is_nullable -> 1
                is_unique -> 1
                is_primary_key -> 0
            column2 ->
                name -> password
                type -> string
                is_nullable -> 1
                is_unique -> 0
                is_primary_key -> 0
        '''
        self.db.execute('''CREATE TABLE users (username STRING UNIQUE NOT NULL, password STRING NOT NULL)''')
        
        self.assertListEqual(self.db.get_table_meta('users'), [('users', 'username', 'STRING', 1, 1, 0), ('users', 'password', 'STRING', 1, 0, 0)])
    
    def test_delete_meta(self):
        self.db.execute('''CREATE TABLE users (username STRING, password STRING)''')
        self.db.execute('''DROP TABLE users''')

        self.assertCountEqual(self.db.get_table_meta('users'), [])