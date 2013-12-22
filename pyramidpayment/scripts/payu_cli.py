import sys
from cmd import Cmd

from pyramidpayment.processors import PayUProcessor


class PayUCLI(Cmd):
    prompt = '[PayU] '
    intro = 'Command line interface to PayU payment services.'

    def do_getTransaction(self, args):
        print 'getting a transaction'

    def help_getTransaction(self):
        print 'getTransaction help'

    def do_setTransaction(self, args):
        print 'setting a new transaction'

    def help_setTransaction(self):
        print 'setTransaction help'

    def do_quit(self, args):
        return True
    
    def help_quit(self):
        print 'Immediately quit the program.'
    
    def do_q(self, args):
        return self.do_quit(args)

    def help_q(self):
        return self.help_quit()
    

def main():
    command = PayUCLI()
    Cmd.cmdloop(command)

if __name__ == '__main__':
    main()
