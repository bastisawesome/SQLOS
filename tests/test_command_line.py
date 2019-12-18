import unittest

from command_line import CommandLine, HelpBuiltin
from database import Database

import sys

class TestCommandLine(unittest.TestCase):

    def setUp(self):
        self.db = Database('memory')
        self.cl = CommandLine(db=self.db)
    
    def tearDown(self):
        self.cl.__del__()

        self.clear_stdout()
    
    def clear_stdout(self):
        sys.stdout.truncate(0)
        sys.stdout.seek(0)
    
    def test_builtin_help(self):
        hb = HelpBuiltin()
        hb(cl=self.cl, args=['help'])
        self.assertEqual(sys.stdout.getvalue().strip(), hb.desc)

        self.clear_stdout()
        
        hb(cl=self.cl, args=['fakecommand'])
        
        self.assertEqual(sys.stdout.getvalue().strip(), 'Command `fakecommand` is not recognised as a builtin command.')
    
    def test_builtin_exit(self):
        pass
    
    def test_builtin_alias(self):
        pass
    
    def test_builtin_todo(self):
        pass
    
    def test_builtin_man(self):
        pass
    
    def test_builtin_pretty_print(self):
        pass
    
    def test_init_commands(self):
        self.cl.init_commands()
    
    def test_init_builtins(self):
        pass
    
    def test_get_all(self):
        pass
    
    def test_append_stdout(self):
        pass
    
    def test_flush_stdout(self):
        pass