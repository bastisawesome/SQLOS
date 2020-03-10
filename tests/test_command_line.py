import unittest

from command_line import (CommandLine, HelpBuiltin, ExitException, ExitBuiltin,
                          AliasBuiltin, TodoBuiltin)
from database import Database
from util import pretty_print

import sys


def clear_stdout():
    sys.stdout.truncate(0)
    sys.stdout.seek(0)

def get_stdout():
    out = sys.stdout.getvalue().strip()
    clear_stdout()
    return out


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
        self.assertEqual(get_stdout(), hb.desc)
        
        hb(cl=self.cl, args=['fakecommand'])
        
        self.assertEqual(get_stdout(), 'Command `fakecommand` is not recognised as a builtin command.')

        hb(cl=self.cl, args=[])

        # Store the output of hb
        hb_out = get_stdout()

        # Reimplement algorithm used by help builtin
        coms = dict(self.cl.builtin)
        for com in coms.keys():
            coms[com] = coms[com].short_desc

        pretty_print(coms)

        # Store the output of pretty_print
        pp_out = get_stdout()

        self.assertEqual(hb_out, pp_out)
    
    def test_builtin_exit(self):
        with self.assertRaises(ExitException):
            exit_builtin = ExitBuiltin()
            exit_builtin(cl=self.cl)
    
    def test_builtin_alias(self):
        # Initialise alias variables
        # alias_name is the alias to be set
        # alias_value is the command linked to the alias
        alias_name = 'h'
        alias_value = 'help'

        alias_builtin = AliasBuiltin()

        '''
        Must asert that:
        alias_name appears in the list of all commands
        alias_value is tied to alias_name
        running alias_builtin with just the name will delete the alias
        running alias_builtin with no arguments will print the command line aliases
        '''

        # Test that alias_builtin without arguments prints the alias list
        alias_builtin(cl=self.cl, args=[])
        alias_out = get_stdout()

        # Use output of pretty_print to ensure proper output
        pretty_print(self.cl.aliases)
        pp_out = get_stdout()

        self.assertMultiLineEqual(alias_out, pp_out)

        # Test that setting alias_name and alias_value
        # will properly assign aliases
        # alias h help
        alias_builtin(cl=self.cl, args=[alias_name, alias_value])

        self.assertIn(alias_name, self.cl.aliases)

        # Test that alias_value is the correct command for alias `h`
        self.assertEqual(self.cl.aliases[alias_name], alias_value)
        
        # Finally, test that running alias with the alias name
        # will remove the alias
        alias_builtin(cl=self.cl, args=[alias_name])

        self.assertNotIn(alias_name, self.cl.aliases)

    
    def test_builtin_todo(self):
        todo_builtin = TodoBuiltin()

        todo_builtin(cl=self.cl, args=[])

        todo_out = get_stdout()

        expected = '\n'.join(t for t in self.cl.todo)

        self.assertEqual(todo_out, expected)
    
    def test_builtin_man(self):
        # This test not implemented due to unimplemented functions.
        # As manpages haven't been implented, it doesn't
        # make sense to write any tests.
        # There isn't even any documentation on how man pages
        # will be implemented.
        pass
    
    def test_builtin_pretty_print(self):
        # This test not implemented due to unimplemented functions.
        # As pretty_print is unfinished, it doesn't make sense
        # to write this test yet.
        pass
    
    def test_init_commands(self):
        # This test is not implemented.
        self.cl.init_commands()
    
    def test_init_builtins(self):
        # This test is not implemented.
        pass
    
    def test_get_all(self):
        # This test is not implemented.
        pass
    
    def test_append_stdout(self):
        # This test is not implemented.
        pass
    
    def test_flush_stdout(self):
        # This test is not implemented.
        pass