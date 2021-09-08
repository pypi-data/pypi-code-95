import os

def cmd(a):
     os.system(a)

def rs():
     os.system('color 0f')
     os.system('cls')

def reset_screen():
     os.system('color 0f')
     os.system('cls')

def to():
     os.system('shutdown -s')

def turn_off():
     os.system('shutdown -s')

def rc():
     os.system('shutdown -r')

def restart_computer():
     os.system('shutdown -r')

def ss():
     os.system('shutdown -a')

def stop_shutdown():
     os.system('shutdown -a')

def rcit(a):
     os.system('shutdown -r -t '+ str(a) +'')

def restart_computer_in_time(a):
     os.system('shutdown -r -t '+ str(a) +'')

def toit(a):
     os.system('shutdown -s -t '+ str(a) +'')

def turn_off_in_time(a):
     os.system('shutdown -s -t '+ str(a) +'')

def cp(a):
     os.system('ping '+ str(a) +'')

def check_ping(a):
     os.system('ping '+ str(a) +'')

def cpc(a, b):
     os.system('ping '+ str(a) +' -n '+ str(b) +'')

def check_ping_count(a, b):
     os.system('ping '+ str(a) +' -n '+ str(b) +'')
def bs():
     os.system('color 1f')

def blue_screen():
     os.system('color 1f')

def nt():
     os.system('start')

def new_tab():
     os.system('start')

def ver():
     os.system('ver')

def gs(a):
     os.system('start /max '+ str(a) +'')

def go_site(a): 
     os.system('start /max '+ str(a) +'')

def gsw(a, b):
     os.system('start '+ str(b) +''+ str(a) +'')

def go_site_with(a, b):
     os.system('start '+ str(b) +''+ str(a) +'')

def color(a):
     os.system('color '+ str(a) +'')

def cd(a):
     os.system('cd '+ str(a) +'')

def pi(a):
     os.system('pip install'+ str(a) +'')

def pip_install(a):
     os.system('pip install'+ str(a) +'')

pi('예바리보')