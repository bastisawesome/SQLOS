from commands.command import Command

import pkgutil
from importlib import import_module

class TestCommand(Command):
    def __init__(self, **kwargs):
        super(TestCommand, self).__init__('test', 'Runs the unit tests.', man_page_entry='''IMPLEMENT ME''')

    def __call__(self, cl, args):
        import unittest
        # Reusing code for code reasons
        '''Initialise tests in the tests module'''
        modules = pkgutil.iter_modules(path=['tests'])
        for loader, mod_name, ispkg in modules:
            if mod_name.startswith('test_'):
                module = import_module('tests.'+mod_name)
                unittest.main(module=module, exit=False, verbosity=2, buffer=True)
    
    def on_help(self):
        pass