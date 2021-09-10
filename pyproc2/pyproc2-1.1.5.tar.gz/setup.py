import setuptools
setuptools.setup(
                name='pyproc2',
                description='Python library for reading data from UNIX /proc/ directory',
                long_description=
'''
## Short intro
**pyproc2** is Python library for reading data from /proc/ directory.
Of course, it works only on Linux.
### Installation
```
pip install pyproc2
```
## What can it do?
### Find processes
There is only one method for all filters (PID, process name, user name,etc.)
It is called `find()`.
Here are few examples:
**1. By PID**:
```python
import pyproc2
pyproc2.find(1)

```
**2. By process name (can return multiple results)**
```python
import pyproc2
pyproc2.find("python")

```
**3. By user name (or UID or whatever)**
```python
import pyproc2
pyproc2.find(user="root")#Replace "user" to filter  by other properties
```
### Doing things with selected process(es)
**1.Sending signals**
Simple kill:
```python
import pyproc2
pr=pyproc2.find("python")
pr.kill()
```
For other signals, pass `kill()` an argument.
Most common signals have defined own methods:
```python
import pyproc2
pr=pyproc2.find("python")
pr.term() #Or stop() or cont() or whatever
```
**2.Acessing attributes**
```python
import pyproc2
pr=pyproc2.find("python")
cpu=pr.cpu
uid=pr.uid
#etc.
```
**3.Accessing children and parent processes**
```python
import pyproc2
pr=pyproc2.find(1)
cdr=pr.children #get all children
parent=pr.parent #get parent process
p4=pr.parentLevel(4) #equivalent of pr.parent.parent.parent.parent
kid=pr.child(3) #fourth children(sorted by PID)(negative indexes are working,too)
```
### Acess predefined process sets
**1.All processes**
```python
import pyproc2
rn=pyproc2.running
```
**2.All processes, sorted by CPU rate**
```python
import pyproc2
t=pyproc2.top
```
## License
**pyproc2** is licensed under **GPL License**
## Changelog
### 1.0.2
Initial
### 1.0.3
Improved documentation
### 1.0.4
Improved documentation
### 1.0.5
Bug fixes
### 1.1.0
Speed increased
### 1.1.1
Added `owner` property as equivalent to `user`
### 1.1.2
Added changelog
### 1.1.3
Fixed `ProcessSet.kill()` NotImplementedError bug
### 1.1.4
Added `STOPPED` state
### 1.1.5
Added `current` property
           ''',
                packages=['pyproc2'],
                version='1.1.5',
                long_description_content_type='text/markdown',
                author='Adam Jenca',
                author_email='jenca.adam@gmail.com',
                url='http://pypi.org/project/pyproc2',
                classifiers=[
                    "Development Status :: 3 - Alpha",
                    "Environment :: Console",
                    "License :: OSI Approved :: GNU General Public License (GPL)",
                    "Operating System :: POSIX :: Linux",
                    "Programming Language :: Python :: 3",
                    "Topic :: System",
                    ])
