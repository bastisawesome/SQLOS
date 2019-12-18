from termcolor import colored, cprint
import functools

# Public functions
# These functions are meant to be imported and called
'''
Takes a message and passes it to one of the printing functions to
depending on the type of the message.
Variable printing utilities:
dictionary -> @see pretty_print_dict
@param message The message to pretty print
'''
def pretty_print(message):
    if type(message) == dict:
        pretty_print_dict(message)
    else:
        raise NotImplementedError('Still working on pretty printing.')

'''
Print the error and message. The error is printed in red while the message is printed in 
white.
'''
def print_error(error, msg):
    print('{}\n{}'.format(colored(error, color='red'), msg))

# Utility's utility functions
# These functions can be imported but mostly exist
# for the public functions
'''
Pretty prints a dictionary.
Takes the length of the longest key and adds a padding of 4 spaces.
Prints the value next to the key
'''
def pretty_print_dict(arg_dict, padding=4):
    key_len = 0
    template = '{}'

    for key in arg_dict:
        if len(key) > key_len - padding: # Ensure there is always a padding
            key_len = len(key) + padding # Gotta pad the string
        
    template = template.format('{0:' + str(key_len) + '}{1:}')

    for key in sorted(arg_dict.keys()):
        print(template.format(key, arg_dict[key]))

'''
Replace nth number in a string
'''
def str_replace_index(string, substring, replace, index):
    find = string.find(substring)
    i = find != -1
    while find != -1 and i != index:
        find = string.find(substring, find+1)
        i += 1
    
    if i == index:
        return string[:find]+replace+string[find+len(substring):]
    
    return string