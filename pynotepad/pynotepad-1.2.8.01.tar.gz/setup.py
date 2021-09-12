import pynotepad,sys,os
from setuptools import setup

try:os.chdir(os.path.split(__file__)[0])
except:pass

try:
    long_desc=open("README.rst").read()
except OSError:
    long_desc=pynotepad.__doc__

setup(
  name='pynotepad',
  version=pynotepad.__version__,
  description="A simple text editor made by tkinter.一款使用tkinter编写的文本编辑器程序。",
  long_description=long_desc,
  author=pynotepad.__author__,
  author_email=pynotepad.__email__,
  py_modules=['pynotepad'], #这里是代码所在的文件名称
  keywords=["simple","text","editor","notepad","tkinter","pynotepad","文本编辑器"],
  classifiers=[
      'Programming Language :: Python',
      "Topic :: Text Editors",
      "Natural Language :: Chinese (Simplified)"],
)
