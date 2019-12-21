import unittest

from command_line import CommandLine, HelpBuiltin, ExitException, ExitBuiltin
from database import Database
from util import pretty_print

import sys


def clear_stdout():
    sys.stdout.truncate(0)
    sys.stdout.seek(0)


class TestCommandLine(unittest.TestCase):

    def setUp(self):
        self.db = Database('memory')
        self.cl = CommandLine(db=self.db)
    
    def tearDown(self):
        self.cl.__del__()

        clear_stdout()

    def test_builtin_help(self):
        hb = HelpBuiltin()
        hb(cl=self.cl, args=['help'])
        self.assertEqual(sys.stdout.getvalue().strip(), hb.desc)

        clear_stdout()
        
        hb(cl=self.cl, args=['fakecommand'])
        
        self.assertEqual(sys.stdout.getvalue().strip(), 'Command `fakecommand` is not recognised as a builtin command.')

        clear_stdout()

        hb(cl=self.cl, args=[])

        # Store the output of hb
        hb_out = sys.stdout.getvalue().strip()
        clear_stdout()

        # Reimplement algorithm used by help builtin
        coms = dict(self.cl.builtin)
        for com in coms.keys():
            coms[com] = coms[com].short_desc

        pretty_print(coms)

        # Store the output of pretty_print
        pp_out = sys.stdout.getvalue().strip()

        self.assertEqual(hb_out, pp_out)
    
    def test_builtin_exit(self):
        with self.assertRaises(ExitException):
            exit_builtin = ExitBuiltin()
            exit_builtin(cl=self.cl)
    
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