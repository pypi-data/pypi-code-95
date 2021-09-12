import notepad,sys,os
from setuptools import setup

try:os.chdir(os.path.split(__file__)[0])
except:pass

try:
    long_desc=open("README.rst").read()
except OSError:
    long_desc=pyobject.__doc__

setup(
  name='notepad',
  version=notepad.__version__,
  description="A simple text editor made by tkinter.一款使用tkinter编写的文本编辑器程序(该包内容与包pynotepad相同)。",
  long_description=long_desc,
  author=notepad.__author__,
  author_email=notepad.__email__,
  py_modules=['notepad'], #这里是代码所在的文件名称
  keywords=["simple","text","editor","notepad","tkinter","gui","中文","记事本"],
  classifiers=[
      'Programming Language :: Python',
      "Topic :: Text Editors",
      "Natural Language :: Chinese (Simplified)"],
)
