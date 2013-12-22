""" This module is provided as a scaffold to write your own command line
    interface (CLI) to whatever payment system you are testing.
"""

import sys
from cmd import Cmd


class PaymentCLI(Cmd):
    prompt = '[command] '
    intro = 'Command line interface to ??? payment services.'

    def do_transaction(self, args):
        raise NotImplemented

    def help_transaction(self):
        raise NotImplemented

    def do_quit(self, args):
        return True
    
    def help_quit(self):
        print 'Immediately quit the program.'
    
    def do_q(self, args):
        return self.do_quit(args)

    def help_q(self):
        return self.help_quit()
    

def main():
    command = PaymentCLI()
    Cmd.cmdloop(command)

if __name__ == '__main__':
    main()
