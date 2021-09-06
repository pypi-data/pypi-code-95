from cmdbomb.helper import get_key
from cmdbomb.cmd import *
from inspect import getmembers

class Shell:
    """
    The main class for CmdBomb. Provides an interactive shell for your application.
    """
    def __help__(self):
        """Displays this message."""
        print(self.notice)
        for cmd in self.__commands.values():
            print(get_key(self.__commands, cmd))
            print(cmd.__doc__)
    def __init__(self, prefix="=>", notice=""):
        self.prefix = prefix + " "
        self.notice = "CmdBomb (c) 2021\n" + notice
        self.__commands = {"help": self.__help__}
    def register_command(self, command, name=""):
        """
        Registers a command for use in the shell.
        """
        if name == "":
            name = command.__name__
        self.__commands[name] = command
    def register_commands(self, commands):
        """
        Registers a `Cmd` object for use in the shell.
        """
        for cmd in getmembers(commands):
            if cmd[0][:1] == "_" or cmd[0] == "get_name":
                continue
            self.register_command(getattr(commands, cmd[0]), commands.get_name(getattr(commands, cmd[0])))
    def start(self):
        """
        Starts the shell.
        """
        while True:
            i = input(self.prefix).split(" ")
            if i[0] == "exit":
                break
            if i[0] in self.__commands.keys():
                # Dealing with built-in commands that are part of the class
                argcount = self.__commands[i[0]].__code__.co_argcount
                if len(self.__commands[i[0]].__code__.co_varnames) > 0 and self.__commands[i[0]].__code__.co_varnames[0] == "self":
                    argcount -= 1
                if len(i) > 1:
                    if argcount > 0:
                        self.__commands[i[0]](i[1:])
                    else:
                        # Handling the wrong number of arguments being passed
                        print(i[0] + ": Wrong number of argumements.")
                else:
                    if argcount == 0:
                        self.__commands[i[0]]()
                    else:
                        # Same
                        print(i[0] + ": Wrong number of argumements.")
            else:
                print("Command not found")
if __name__ == "__main__":
    def ping():
        """Prints "pong"."""
        print("pong")
    def nerd():
        """Calls you a nerd"""
        print("hi nerd")
    class CmdTest(Cmd):
        def ebic(self):
            """Prints "chad"."""
            print("chad")
    class CmdTest2(Cmd):
        def cool(self):
            """Prints "cool"."""
            print("cool")
        def get_name(self, func):
            return "print_cool"
    shell = Shell()
    shell.register_command(ping)
    shell.register_command(nerd, "call_nerd")
    shell.register_commands(CmdTest())
    shell.register_commands(CmdTest2())
    shell.start()
