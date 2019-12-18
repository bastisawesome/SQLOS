from commands.command import Command
from util import pretty_print, str_replace_index
from datetime import datetime

'''
Used to manipulate the Sqlite database through a command. This is a complex, multi-stage
command which utilises many sub-commands to handle data manipulation and reading. Included
are select, add table, remove table, modify table, and more. This is essentially
an interactive SQL shell, not to be confused with the default shell for SQLOS, which
handles interacting with the database.

Sub-commands are a special type of command, implemented here instead of by the main
command class. Each one contains a short description and is in charge of handling
their own long description. Sub-commands are implemented as functions instead of objects.
They are called by `__call__` but then handle their own functionality separately. Sub-commands
do not invoke their own functions, everything they do themselves within a single function,
with the exception of general-use functions that may be needed across multiple sub-commands.
'''
class DatabaseCommand(Command):
    def __init__(self, **kwargs):
        super(DatabaseCommand, self).__init__('database', 'Allows the user to modify the Sqlite database in multiple ways.', man_page_entry='''IMPLEMENT ME''')

        # This is a special variable
        # The `__call__` function will set this if it hasn't already been set
        # Each sub-command will be completely unaware of the shell.
        self.db = None

        # Dictionary to keep track of subcommands
        # The key is the name of the sub-command
        # The value is the short description of the sub command
        self.sub_commands = {
            'create': 'Creates a new table',
            'alter': 'Modifies an existing table',
            'select': 'Selects data from the database',
            'insert': 'Inserts data into a table in the database',
            'update': 'Updates a row in a table in the database',
            'help': 'Print help information for each sub-command',
            'execute': 'Executes raw SQL',
            'commit': 'Commits changes to database',
            'log': 'Prints the database log'
        }
    
    '''
    The `__call__` function first determines if there is a database already assigned.
    If not, it sets the database to the shell's database. Sub-commands will be unaware
    of the shell's existence, relying on the internal variables for anything they need.
    Next, it checks if there is a sub-command to invoke, and if not, will return sub-command
    information. Next, it handles executing sub-commands. From there, the sub-commands
    are in charge of taking user input and managing the database.
    '''
    def __call__(self, cl, args):
        # Ensure there is a database reference internally
        if self.db == None: self.db = cl.db

        # Ensure there is a sub-command to invoke
        if len(args) < 1:
            # The user hasn't specified a sub-command
            # Display subcommand information
            pretty_print(self.sub_commands)
            
            return 0
        else:
            com = args[0] # Sub-command to be run
            sargs = args[1:] # Args to be passed to sub-command
            if com in self.sub_commands.keys():
                getattr(self, 'sub_'+com, None)(sargs)
            else:
                print('Function {} not found. For help type `database help` or `database` to see a full list of functions.'.format(com))
                return 1
            
            return 0
        
        # This should not happen!
        return -1
    
    '''
    Select information from a table.
    Arguments passed in must be in the following order:
    args[0] OR args[0:] -> table name OR arguments passed into select
    args[1:] OR args[:] -> columns to select from the table OR table name (if args[0:] are arguments)
    @param args Table information and arguments passed into `select` subcommand
    '''
    def sub_select(self, args):
        # Parse out any arguments
        # TODO: Fill this in!
        '''
        Arguments:

        '''
        # Ensure args contains at least a table name
        if len(args) < 1:
            # Print help information

            return -1
        
        template = ''

        if len(args) == 1:
            # In this case, the user only specified the table name
            template = 'SELECT * FROM {}'.format(args[0])
        else:
            table_name = args[0]
            table_rows = args[1:]
            template_rows = ', '.join([i for i in table_rows])

            template = 'SELECT {} FROM {}'.format(template_rows, table_name)
        
        # TODO: Pretty print results
        results = self.db.execute(template)
        print(results)

        return 0

    '''
    Insert information into a table.
    Args passed in must be in the following order:
    args[0] OR args[0:] -> table name OR arguments passed into insert
    args[1:] OR args[:]-> values passed into the table OR table name (if args[0:] are arguments)
    @param args Table information and arguments passed into `insert` subcommand
    '''
    def sub_insert(self, args):
        # Parse out any arguments
        # TODO: Fill this in!
        '''
        Arguments to be parsed:
        specify columns -> Necessary to specify columns to fill when inserting
        '''
        # Ensure args contains at least the table name and values
        if(len(args) < 2):
            # Display help message here

            return -1

        # Setup the template
        # The number of values to pass will be set
        # by the number of arguments passed in by the user
        template = 'INSERT INTO {} VALUES ({})'

        table_name = args[0]
        table_values = args[1:]

        template = template.format(table_name,
            ''.join(['?,' for i in range(len(table_values))])[:-1])

        template, args = self.sql_stuff(template, *table_values)

        self.db.execute(template, *args)
    
    def sub_update(self, args):
        pass

    def sub_create(self, args):
        '''
        This function is one of the more complicated ones.
        It has 4 required parts, two being EOF indicators, one being the table name, and the last being the first column name.
        The layout for this command is:
        arg[0] -> EOF Indicator
        line[1] -> Name of table to create
        line[2...N] -> Column definitions
        arg[...N+1] -> EOF Indicator
        First, the command reads the EOF character. This is used to determine when the user has finished entering information.
        Next, it reads the table name and column definitions.
        Finally, it sees the EOF indicator and stops reading information.
        This command MUST be called with only one argument. The rest of the information is collected from STDIN. Each column definition is separated by a newline character. Each line must contain the full column definition and only one definition per line.
        Once it receives the EOF indicator, it then parses the input and runs a SQL query.
        '''
        if len(args) != 1:
            # Display help message here
            return -1
        
        eof_indicator = args[0]
        template = '''CREATE TABLE {} ({})'''
        sql_input = []
        # Capture user input until it encounters EOF
        while(True):
            next_line = input()
            if next_line == eof_indicator:
                break
            if next_line != '':
                sql_input.append(next_line)
        
        sql = template.format(sql_input[0], ','.join([i for i in sql_input[1:]]))
        '''
        Input:
        database create EOF
        users
        username string not null
        password string not null
        EOF

        template -> CREATE TABLE {} ({})
        template -> CREATE TABLE users ({})
        template -> CREATE TABLE users (username string not null, password string not null)
        '''

        self.db.execute(sql)

    def sub_alter(self, args):
        pass
    
    def sub_execute(self, args):
        sql = ' '.join([i for i in args])
        value = self.db.execute(sql)
        # Print out any output given from the database
        if value:
            print(value)
    
    def sub_commit(self, args):
        self.db.commit()
    
    def sub_log(self, args):
        print('\n'.join([i for i in self.db.log]))
        # TODO: Implement pretty print for this?

    def sub_help(self, args):
        pass
    
    def sql_stuff(self, template, *args: tuple):
        '''
        Input:
        template -> INSERT INTO users (?,?)
        args[0] -> 'bastisawesome'
        args[1] -> 'exec:datetime('now')'

        Template result:
        database insert users bastisawesome exec:datetime('now')

        Output:
        INSERT INTO users VALUES ('bastisawesome', datetime('now'))
        
        Possible solutions:
        Input: exec:datetime.now()
        Code:
        exec(args[1]) # exec(datetime.now())
        Problem:
        Random code execution -> security hole
        '''
        '''
        If using the sql: command, you have to remember that it is executing sql without
        being escaped. This is a huge security hole because it isn't escaped. You have to make sure you use valid SQL. Furthermore, spaces are not allowed in the commands, so nothing that uses spaces will be accepted.
        '''
        new_template = template
        for i in args:
            if 'sql:' in i:
                command = i.split(':')[1]
                index = args.index(i)
                new_template = str_replace_index(template, '?', command, index+1)
                args = [i for i in args if not 'sql:' in i]
        
        return new_template, args