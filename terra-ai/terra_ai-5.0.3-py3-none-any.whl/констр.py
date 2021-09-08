from . import датасет
import subprocess, os, warnings, time
from subprocess import STDOUT, check_call
from IPython.display import display, HTML, IFrame

def выполнить_команду(команда='!ls'):
  proc = subprocess.Popen(f'{команда}', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=STDOUT, executable="/bin/bash")
  proc.wait()
  pass

def конструктор():
  датасет.загрузить_базу_конструктора()
  files = ['del.png', 'funstions.js', 'header.jpg','radio-1.png','radio-2.png','style.css']
  for f in files:
    выполнить_команду('cp /content/'+f + ' /usr/local/share/jupyter/nbextensions/google.colab/'+f)
    выполнить_команду('rm /content/'+f)
  выполнить_команду('rm /content/UI.zip')
  f2 = open('terra_ai.html')
  my_HTML = f2.read()
  display(HTML(my_HTML))
