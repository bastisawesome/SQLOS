'''
Base class for commands.
Each command must extend this class and implement the abstract functions.
Abstract functions will raise a NotImplementedError if they are not implemented by
the child class.
'''
class Command():
    '''
    Initialise Command. This constructor is similar to the `Builtin` constructor, with one major difference: commands do not have a short description. This is because commands do
    not display with the help command, so the short description is unused.
    Commands are expected, but not required, to include a manual page entry. This entry
    is used with the shell's manual page command to show additional usage and explanations.
    If the manual page entry is empty, it is the job of the shell to handle the error
    appropriately.
    Commands must contain a name and description. The name is used to reference the command
    from the shell. This cannot contain spaces. The description is required to be defined
    but is not required to be used. It is up to the command to decide how to handle
    the long description, either showing when `on_help` is invoked or never shown.
    @param name Name of the command
    @param desc Long description of command
    @param kwargs Special attributes for commands
    @see command_line.Builtin
    '''
    def __init__(self, name, desc, **kwargs):
        self.name = name
        self.desc = desc
        self.man_page_entry = None

        if kwargs.get('man_page_entry', None):
            self.man_page_entry = kwargs['man_page_entry']
            del kwargs['man_page_entry']
            
        self.spec = kwargs

    '''
    Return the manual page entry for the command. Commands may not have a manual page entry,
    which is to be handled by the shell itself and not the command. There is no reason to
    implement this function in sub-classes.
    @return Manual page entry for the command
    '''
    def man_page(self):
        return self.man_page_entry
    
    '''
    Because `Command` is not a built-in, the `on_help` function is not pre-defined. There
    is no short description to display, so it's up to a command to decide how to implement
    the `on_help` function. Normally this function will either call the shell's manual page
    command then return or display the full description, complete with explanations on how
    to use the command or a list of arguments that can be passed in.
    This function can also be called when the user passes the help argument to the command.
    '''
    def on_help(self):
        raise NotImplementedError('Abstract function `on_help` has not been implemented.')
    
    '''
    Runs the command, passing in the shell and additional arguments to the command. This
    function is abstract and requires the sub-classes to implement it, otherwise it will
    raise a `NotImplementedError`. Commands are not required to use the shell or 
    additional arguments, although most commands will use at least the arguments. This
    function is similar to the `Builtin` commands' on_run, complete with the same
    arguments. If the implementation does not follow this style, there is a chance
    the shell will not execute the command correctly and likely will crash.
    @param cl Shell the command is running from
    @param args Arguments passed to the command 
    @see command_line.Builtin
    '''
    def on_run(self, cl, args):
        raise NotImplementedError('Abstract function `on_run(self, cl, args)` has not been implemented.')