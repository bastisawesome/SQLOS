import inspect
from importlib import import_module
import pkgutil

from commands.command import Command
from util import pretty_print, print_error

class ExitException(Exception):
    def __init__(self):
        super(__class__, self).__init__(self, "Exited the command line.")

class CommandLine():
    def __init__(self, db, **kwargs):
        self.coms = {}
        self.builtin = {}
        self.aliases = {
            # Database aliases
            'dbx': 'database execute',
            'dbl': 'database log',
            'dbc': 'database create',
            'dbco': 'database commit',
            'dbm': 'datbase modify',
            'dbs': 'database select',
            'dbi': 'database insert',
            'dbu': 'database update',
            'dbd': 'database dump',
            }
        self.spec = {}
        self.todo = [
            'Implement colour shell',
            'Implement long descriptions for builtins',
            'Implement man page text for builtins',
            'Implement default man (no args)',
            'Implement readline with tab-completion',
            'Implement a `clear` builtin',
            'Implement persistent settings (shelve and/or pickle?)',
            'Cleanup documentation on `on_run`, which has been replaced with `__call__`',
            'Implement command output passing',
            'Implement bash-like command structure',
            'Replicate database create multi-line input in database execute (maybe all)',
            'Add security to anything that bypasses SQL escaping (check input for specific tags',
            'Reimplement check for foreign key on meta tables',
            'Implement more tests',
            'Update test command to allow running specific tests',
            'Implement users and authentication',
            'Move all print statements to standard out',
            'Change util.py to return values for commands to process into stdout',
            'Implement stdout as a class',
            'Implement exception handler in database'
        ]
        
        self.db = db

        for name, value in kwargs.items():
            self.spec[name] = value
        
        self.stdout = ''

        self.init_builtins()
        self.init_commands()

        '''
        Set welcome message
        '''
        self.welcome_msg = \
r'''   _____   ____   _       ____    _____ 
  / ____| / __ \ | |     / __ \  / ____|
 | (___  | |  | || |    | |  | || (___  
  \___ \ | |  | || |    | |  | | \___ \ 
  ____) || |__| || |____| |__| | ____) |
 |_____/  \___\_\|______|\____/ |_____/ 
                                        
''' + '''\t\tSQL SHELL\nCreated by: Giles Johnson\nCopyright: 2019'''
        
    def init_commands(self):
        '''Initialise commands in the commands module'''
        modules = pkgutil.iter_modules(path=['commands'])
        for loader, mod_name, ispkg in modules:
            module = import_module('commands.'+mod_name)
            
            for x in dir(module):
                obj = getattr(module, x)
            
                if inspect.isclass(obj) and issubclass(obj, Command) and obj is not Command:
                    # `obj` is a command! So set everything up
                    instance = obj()
                    self.coms[instance.name] = instance
    
    def init_builtins(self):
        '''Initialise built-in commands!'''
        self.builtin['help'] = HelpBuiltin()
        self.builtin['exit'] = ExitBuiltin()
        self.builtin['alias'] = AliasBuiltin()
        self.builtin['todo'] = TodoBuiltin()
        self.builtin['man'] = ManBuiltin()
        self.builtin['pretty_print'] = PrettyPrintBuiltin()

    def parse_command(self, com, args):
        all_coms = self.get_all()
        # Brilliant solution ahead!
        # This solution fixes the alias problem
        # First, instead of executing the command immediately (like an idiot)
        # we need to separate the commands from the alias strings
        command = all_coms[com]
        
        # Next, we need to check if the command is a string
        if type(command) == str:
            # Now that we know we're working on a string...
            # Obviously, we need to parse it down into a command!
            # Same as before...
            # Start by splitting the string into a list
            com_list = command.split(' ')

            # Next, we take the first index which is the command name
            com_name = com_list[0]
            
            # The rest of that list becomes arguments to be passed!
            com_args = com_list[1:]

            # Now, we put it all together
            # Because it's an alias, there should be other args, so...
            command = all_coms[com_name]
            
            # Interesting error here... `args` is passed in from the parser
            # not the alias. Because of this, you actually have to work backwards
            com_args.extend(args) # First, put all the args together in the correct order
            args = com_args # Finally, move `com_args` into `args` so the order is correct
            
        # Arguments are passed in as an array of strings
        # Commands must properly handle arguments
        command(self, args)
    
    def loop(self):
        print(self.welcome_msg)
        while(True):
            all_coms = self.get_all()
            user_in = input("> ")
            
            # Separate user input into the command and arguments
            com = user_in.split(' ')[0].lower()
            args = user_in.split(' ')[1:]
            if com in all_coms:
                try:
                    self.parse_command(com, args)
                    self.flush_stdout()
                except (ExitException, KeyboardInterrupt) as e:
                    raise e
                except Exception as e:
                    print_error(type(e).__name__, e)
            else:
                self.append_stdout('{} is not a command or alias.'.format(com))
    
    '''
    Concatenate builtins, aliases, and commands into one dictionary for parsing.
    If an aliases overwrites a builtin or command then the alias will take precedence and
    the user won't have access to the original. The original command or builtin will not be returned.
    @return The concatenation of builtins, aliases, and commands
    '''
    def get_all(self):
        all_coms = dict(self.builtin, **self.coms)

        # Remove original command and builtin references for aliases.
        for name, value in self.aliases.items():
            all_coms[name] = value

        return all_coms
    
    '''
    Concatenate builtins and commands into one dictionary for parsing.
    @return The concatenation of builtins and commands
    '''
    def get_coms(self):
        coms = dict(self.builtin, **self.coms)

        return coms
    
    def flush_stdout(self):
        print(self.stdout)
        self.stdout = ''
    
    def append_stdout(self, msg):
        self.stdout += ' ' + msg
    
    def __del__(self):
        self.db.__del__()

class Builtin():
    '''
    Class for built-in shell commands. This class is used to initialise 
    all shell commands.
    @param name Invocation name of command
    @param short_desc Help message description
    @param desc Full description of command, shown when user types `help [command]`
    '''
    def __init__(self, name, short_desc='', desc='THIS HAS NOT BEEN IMPLEMENTED YET!'):
        self.name = name
        self.short_desc = short_desc
        self.desc = desc
    
    def on_help(self):
        print(self.desc)
    
    '''
    Function to be run when a command is invoked. This function is required to be declared
    by child functions. If it's not, it will raise an error.
    The *args parameter is also required to have the command line passed as the first argument.
    @param cl Command line interface, for access to special variables.
    @param args Arguments to be passed to the command (dict)
    '''
    def __call__(self, cl, args):
        raise NotImplementedError('This function is required to be implemented by child classes')

class HelpBuiltin(Builtin):
    def __init__(self):
        super(HelpBuiltin, self).__init__('help', 'Shows built-in commands and descriptions')
    
    def __call__(self, cl, args):
        if len(args) == 0:
            arg_dict = dict(cl.builtin) # Casting to avoid creating a pointer
            for com in arg_dict.keys():
                arg_dict[com] = arg_dict[com].short_desc

            pretty_print(arg_dict)
        else:
            if not args[0] in cl.builtin:
                print('Command `{}` is not recognised as a builtin command.'.format(args[0]))
                return 1
            
            cl.builtin[args[0]].on_help()

        return 0

class ExitBuiltin(Builtin):
    def __init__(self):
        super(ExitBuiltin, self).__init__('exit', 'Exits the shell')
    
    def __call__(self, cl, *args):
        raise ExitException()

class AliasBuiltin(Builtin):
    def __init__(self):
        super(AliasBuiltin, self).__init__('alias', 'Creates and modifies aliases')
    
    def __call__(self, cl, args):
        if len(args) == 0:
            pretty_print(cl.aliases)
            return 0
        elif len(args) == 1:
            if args[0] in cl.aliases:
                del cl.aliases[args[0]]
            return 0
        
        a_name = args[0]
        a_com = ' '.join([i for i in args[1:]])
        cl.aliases[a_name] = a_com

        return 0

class TodoBuiltin(Builtin):
    def __init__(self):
        super(TodoBuiltin, self).__init__('todo', 'Lists everything to be done for the shell.')
    
    def __call__(self, cl, args):
        for todo in cl.todo:
            print(todo)

class ManBuiltin(Builtin):
    def __init__(self):
        super(ManBuiltin, self).__init__('man', 'Opens the man-page for a command')
    
    def __call__(self, cl, args):
        if len(args) < 1:
            return 0
        
        coms = cl.get_coms()
        
        if not args[0] in coms:
            print('No man page found for {}'.format(args[0]))
            return 0
        com = coms[args[0]]
        
        if isinstance(com, Builtin):
            print('Builtins coming soon!')
            return 0
        else:
            if com.man_page_entry is not None:
                print(com.man_page_entry)
                return 0
            else:
                print('No man page found for {}'.format(com))
                return 0
        
        # If this returns, something went horribly wrong
        return -1

class PrettyPrintBuiltin(Builtin):
    def __init__(self):
        super(PrettyPrintBuiltin, self).__init__('pretty_print', 'Prettifies output')
    
    def __call__(self, cl, args):
        pretty_print(args)

        return 0