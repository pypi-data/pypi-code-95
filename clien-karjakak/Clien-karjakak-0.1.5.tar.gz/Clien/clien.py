# -*- coding: utf-8 -*-
#Copyright (c) 2020, KarjaKAK
#All rights reserved.

import argparse
from subprocess import Popen, PIPE
import os
from sys import platform as plat

def insdat():
    # Input data, var, and pass for encrypting.
    
    from tkinter import Tk, Label, Entry, E, simpledialog

    root = Tk()
    root.withdraw()
    class MyDialog(simpledialog.Dialog):
    
        def body(self, master):
            Label(master, text="Data: ").grid(row=0, column = 0, sticky = E)
            self.e1 = Entry(master, show = '-')
            self.e1.grid(row=0, column=1)
            Label(master, text="Var: ").grid(row=1, column = 0, sticky = E)
            self.e2 = Entry(master)
            self.e2.grid(row=1, column=1)
            Label(master, text="Pass: ").grid(row=2, column = 0, sticky = E)
            self.e3 = Entry(master)
            self.e3.grid(row=2, column=1)            
            return self.e1
    
        def apply(self):
            if self.e1.get() and self.e3.get():
                if self.e2.get():
                    self.result = (self.e1.get(), self.e2.get(), self.e3.get())
                else:
                    self.result = (self.e1.get(), self.e3.get())
            else:
                self.result = None
                
    d = MyDialog(root)
    root.destroy()
    if d.result:
        return d.result

def pssd():
    # Give passcode for decrypting the data.
    
    from tkinter import Tk, Label, Entry, E, simpledialog

    root = Tk()
    root.withdraw()
    class MyDialog(simpledialog.Dialog):
    
        def body(self, master):
            Label(master, text="Pass: ").grid(row=0, column = 0, sticky = E)
            self.e1 = Entry(master, show = '-')
            self.e1.grid(row=0, column=1)            
            return self.e1
    
        def apply(self):
            self.result = self.e1.get()
                
    d = MyDialog(root)
    root.destroy()
    if d.result:
        return d.result    

def ckshenv():
    # Checking for MacOS terminal shell and it's files 

    sh = os.environ.get('SHELL', None)
    if sh and not plat.startswith('win'):
        if sh.rpartition('/')[2].startswith('z'):
            return {
                'zsh': [i for i in os.listdir(os.path.expanduser('~')) if i.startswith('.z')]
            }
        else:
            return {
                'bash': [i for i in os.listdir(os.path.expanduser('~')) if i.startswith('.b')]
            }
    else:
        return sh


def varenv(val: str, var: str):
    # Writing environment variable to MacOS
    
    wr = f'{var}="{val}"'
    ck = ckshenv()
    if ck:
        wrto = ('zprofile'
                if tuple(ck.keys())[0] == 'zsh' 
                else 'bash_profile'
               )
        os.system(f'echo  >> {os.path.expanduser("~")}/.{wrto}')
        os.system(f'echo {wr} >> {os.path.expanduser("~")}/.{wrto}')
        os.system(f'echo export {var} >> {os.path.expanduser("~")}/.{wrto}')
    else:
        print('Unimplemented!')

def cmsk(data: str, base: str, varn: str = None):
    # WARNING:
    # Do not set variable that already exist and important.
    
    try:
        lb = len(base)
        nlt = f'{data} + {base}'
        base = sum([ord(i) for i in base])
        base = base - lb if base > lb else base + lb
        nlt = ''.join([chr(ord(i) + base) for i in nlt]).encode('punycode')
    except:
        print('Error Occured!')
    else:
        if varn:
            if plat.startswith('win'):
                pnam = f'setx {varn} {nlt.decode()}'
                copline = None
                with Popen(
                    pnam, 
                    stdout = PIPE, 
                    bufsize = 1, 
                    universal_newlines = True, 
                    text = True
                    ) as p:
                    for line in p.stdout:
                        copline = line
                        print(copline, end='')
                if 'SUCCESS:' in copline:
                    print(f'var: {varn}')
                    print('Please restart the console!')
                else:
                    print(f'Variable {varn} not created yet!')
                del copline
            else:
                varenv(nlt.decode(), varn)
        else:
            return nlt.decode()
    finally:
        del lb, nlt, base, data, varn
            
    
def reading(data: str, base: str):
    # reading var that created
    
    try:
        if data[0] == "%" and data[-1] == "%":
            print('Could not read None')
        else:
            lb = len(base)
            ck = base
            base = sum([ord(i) for i in base])
            base = base - lb if base > lb else base + lb        
            nlt = ''.join([chr(ord(i) - base) for i in data.encode().decode('punycode')])
            if dck := True if nlt.rpartition(' + ')[1] and nlt.rpartition(' + ')[2] == ck else False:
                del lb, ck, base, dck
                return nlt.rpartition(' + ')[0]
            else:
                print("The password doesn't matched!")
    except:
        print('Error Occured!')
        
def main():
    # CLI mode.
    
    parser = argparse.ArgumentParser(prog = "CP", description = 'Create Password')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--create", 
                               action = 'store_true', 
                               help = 'Creating encrypted password file',
                              )
    group.add_argument("-r", "--read", 
                               nargs = 1,
                               type = str,
                               help = 'Read ecnrypted password',
                              )
    args = parser.parse_args()
    if args.create:
        a = insdat()
        if a:
            cmsk(a[0], a[2], a[1])
        else:
            print('Please fill all fields!')
    elif args.read:
        a = pssd()
        if a:
            print(reading(args.read[0], a))
        else:
            print('Please fill field!')

if __name__ == "__main__":
    main()