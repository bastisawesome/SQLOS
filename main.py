# Migration to GitHub
import sys
from database import Database
from command_line import CommandLine, ExitException

def main(args):
    #return test_database()
    
    cl = CommandLine(db = Database())
    cl.parse_command('test', [])
    return
    #cl.parse_command('database', ['dump'])
    #return
    try:
        cl.loop()
    except (ExitException, KeyboardInterrupt):
        cl.__del__()
        return

def arg_parser(args):
    return {}

if __name__ == "__main__":
    main(arg_parser(sys.argv))
