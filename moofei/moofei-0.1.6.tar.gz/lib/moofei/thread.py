#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''
__all__ = ['Thread', 'is_threading_patch']

import time
import threading
import traceback
import os
import sys
import signal
import ctypes
import functools
from threading import Thread as _Thread
from time import sleep

try:
    import fcntl
except:
    fcntl = None

try:
    from gevent import monkey, Greenlet, sleep
    is_threading_patch = monkey.is_module_patched('threading')    
except:
    monkey = Greenlet = None
    is_threading_patch = False
        
class Thread(_Thread):
    fncall = None #回调函数
    is_end = 0
    is_error = None
    fncall_result = None
    
    def __init__(self, fncall=None, thread_id=None, *args, **awgs):
        self.is_end = 0
        _Thread.__init__(self)
        self.args = args
        self.awgs = awgs
        self.daemon = True
        if fncall: self.fncall=fncall
        self.thread_id = thread_id
        self._pid = os.getpid()
        
    def get_id(self): 
        # returns id of the respective thread 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: return id
        return self.ident
        
    def kill(self, thread_id=None, is_force=False):
        #os.kill(self._pid, signal.SIGKILL)  # kill子进程
        thread_id = thread_id or self.get_id() 
        #精髓就是这句话，给线程发过去一个exceptions，线程就那边响应完就停了
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
        elif is_force:
            if 'win' in sys.platform.lower():
                cmd = 'taskkill -f -pid %s' % thread_id
            else:
                cmd = 'kill -9 %s' % thread_id
            result = os.popen(cmd)
            #print(result)
        return res
            
    def run(self):
        try:
            if self.fncall is None and self.awgs.get('target'):
                self.fncall = self.awgs.pop('target')
                self.fncall_result = self.fncall(*self.args, **self.awgs)
            else:
                self.fncall_result = self.fncall(self.thread_id, *self.args, **self.awgs)
        except Exception as e:
            self.is_error = traceback.format_exc()
            raise
        finally:
            self.is_end = 1
    
    @classmethod
    def lockfile(cls, pidfile, error=None, cache={}):
        '''
        >>> @Thread.lockfile('./temp.pid')
        ... @valid.func(['thread_id:int'])
        ... def test(thread_id=0, *args):print(thread_id, *args)
        >>> Thread.main(5, test, 11111)
        '''
        def wrap(fn):
            @functools.wraps(fn)
            def func(*args, **awgs):
                if pidfile in cache:
                    if error is None:
                        return {'error':{'message':'%s Is Started!'%pidfile}}
                    return error
                if fcntl:
                    fd = os.open(pidfile, os.O_RDWR | os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR)
                    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
                    assert flags != -1
                    flags |= fcntl.FD_CLOEXEC
                    r = fcntl.fcntl(fd, fcntl.F_SETFD, flags)
                    assert r != -1
                    #fcntl.lockf(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
                    fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB, 0, 0, os.SEEK_SET)
                else:
                    if os.path.isfile(pidfile): os.remove(pidfile)
                    fd = os.open(pidfile, os.O_CREAT|os.O_EXCL|os.O_RDWR)
                
                cache[pidfile] = fd
                pid = str(os.getpid())
                if bytes is str: #py2
                    os.write(fd, bytes(pid))
                else:
                    os.write(fd, bytes(pid, encoding="utf8"))
                
                try:    
                    rs = fn(*args, **awgs)
                finally:
                    cache.pop(pidfile, None)
                    if fcntl: fcntl.lockf(fd, fcntl.LOCK_UN)
                    os.close(fd)
                return rs    
            return func
        return wrap
    
    @classmethod    
    def main(cls, num, fncall, *args,  **awgs):
        """
        >>> rs = []            
        >>> def fncall(thread_id,L):
        >>>     while 1:
        >>>         time.sleep(0.5)
        >>>         if not L: break
        >>>         rs.append([thread_id,L.pop()])
        >>> Thread.main(10, fncall, range(10,100)) 
        >>> for e in rs: print(e)
        """
        threads = []
        for i in range(1,num+1):
            t = cls(fncall, i, *args,  **awgs)
            threads.append(t)

        for i in range(len(threads)):
            threads[i].start()

        for i in range(len(threads)):
            threads[i].join()


            
        


    
            
