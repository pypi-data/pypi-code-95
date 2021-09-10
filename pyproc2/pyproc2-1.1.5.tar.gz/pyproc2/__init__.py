import os
import sys
from pwd import getpwuid as gpu
import subprocess
import time
import signal
import getpass
import platform
class pyproc2(object):
    class signals:
        def __init__(self):
            self.__dict__.update({n:int(getattr(signal,n)) for n in dir(signal) if n.startswith('SI')})

        class Signalled:
            def stop(self):
                self.kill(pyproc2.signals.SIGSTOP)
                
            def cont(self):
                self.kill(pyproc2.signals.SIGCONT)
            def chld(self):
                self.kill(pyproc2.signals.SIGCHLD)
            def hup(self):
                self.kill(pyproc2.signals.SIGHUP)
            def term(self):
                self.kill(pyproc2.signals.SIGTERM)
        
    class SLEEPING:
        def __repr__(self):
            return 'SLEEPING'
    class RUNNING:
        def __repr__(self):
            return 'RUNNING'
    class UNKNOWN:
        def __repr__(self):
            return 'UNKNOWN'
    class STOPPED:
        def __repr__(self):
            return 'STOPPED'
    class _Process(signals.Signalled):
        def __init__(self,pid,proc_rm=None):
            if proc_rm:
                proc_rm=str(proc_rm)
            self.pid=int(pid)
            self.path=os.path.join('/proc',str(pid))
            if not os.path.exists(self.path):
                raise ProcessLookupError("no such process: {}".format(self.pid))
            if not os.path.isdir(self.path):
                raise NotADirectoryError("not a directory")
            if 'status' not in os.listdir(self.path):
                raise FileNotFoundError
            self.raw=open(os.path.join(self.path,'status')).read()
            self.data=[l.split(':',1) for l in self.raw.splitlines()]
            self.data=dict(self.data)
            self.data={k.lower().strip():v.lower().strip().replace('\t',' ') for k,v in self.data.items()}
            self.name=self['name']
            #self.__dict__.update(self.data)
            self.uid=os.stat(self.path).st_uid
            try:
                self.user=gpu(int(self.uid)).pw_name
            except KeyError:
                self.user='root'
            self.owner=self.user   
            self.statusdata=open(os.path.join(self.path,'stat')).read().split()
            self.cmd=open(os.path.join(self.path,'cmdline')).read().strip().replace('\x00','')
            if 'state' not in self.data:
                self.state=pyproc2().UNKNOWN
            else:
                stletter=self['state'].split()[0]
                if stletter.lower()=='s':
                    self.state=pyproc2().SLEEPING
                elif stletter.lower()=='r':
                    self.state=pyproc2().RUNNING
                elif stletter.lower()=='t':
                    self.state=pyproc2().STOPPED
                else:
                    self.state=pyproc2().UNKNOWN
            self.parent=pyproc2().NotExistingProcess()
            if 'ppid' in self.data:
                try:
                    self.parent=pyproc2()._Process(self['ppid'],self.pid)
                except ProcessLookupError:
                    pass
            
        def __getitem__(self,i):
            return self.data[i]
        def __setitem__(self,n,i):
            self.data[n]=i
        def count_cpu(self):
            self.utime=int(self.statusdata[13])
            self.stime=int(self.statusdata[14])
            self.cutime=int(self.statusdata[15])
            self.cstime=int(self.statusdata[16])
            self.ttime=self.stime+self.utime+self.cutime+self.cstime
            self.startup=int(self.statusdata[21])
            secs=pyproc2().uptime - self.startup/pyproc2().CLK
            


            return 100*((self.ttime/pyproc2().CLK)/secs)

        def _cldrn(self):
            kids=open(os.path.join(self.path,'task',str(self.pid),'children')).read().split()
            return pyproc2().MakeProcessSet([pyproc2()._Process(int(p)) for p in kids])
        def child(self,ind=0):
            try:
                return self.children[ind]
            except IndexError:
                raise IndexError('child index overflow (maximum={})'.format(len(self.children)))
            except KeyError:
                return self.children
        def __getattr__(self,at):
            try:
                return pyproc2._Process(self.pid)[at]
            except KeyError:
                raise AttributeError(at)
        def __repr__(self):
            return str(self.pid)+r'{'+ self.name +r'}'
        def __eq__(self,sec):
            if sec.pid==self.pid:
                return True
            return False
        def kill(self,sig=9):
            try:
                os.kill(int(self.pid),sig)
            except PermissionError as err:
                reason=str(err)


                raise PermissionError("unable to kill process {}: {}".format(self,reason))
            except ProcessLookupError as err:
                self=pyproc2.NotExistingProcess()
                self.kill()
        def parentLevel(self,level):
            res=self
            for i in range(level):
                if not res.parent:
                    return res
                try:
                    res=res.parent
                except NotImplementedError:
                    return res
            return res

        cpu=property(count_cpu)
        children=property(_cldrn)
    class NotExistingProcess:
        def __getattr__(self,foo):
            raise NotImplementedError("trying to acess attribute {} on non-existing process".format(foo))
        def kill(self,*args,**kwargs):
            raise NotImplementedError("trying to kill a non-existing process")
        def __repr__(self):
            return '\r'
        def __bool__(self):
            return False
    
    class ProcessSet(signals.Signalled):
        def __init__(self,pcs,name="<unknown>",rs=False):
            self.pcs=pcs
            self.pci=iter(pcs)
            if len(self.pcs)==0:
                if rs:
                    raise ProcessLookupError("no such process:{}".format(name))
                self=None
        def kill(self,signal=9):
            for pc in self.pcs:
                try:
                    pc.kill(signal)
                except NotImplementedError:
                    pass
        def __repr__(self):
            return 'ProcessSet({})'.format(repr(self.pcs).replace("]","").replace("[",""))
        def __iter__(self):
            return self
        def __next__(self):
            return next(self.pci)
        def __getitem__(self,i):
            return self.pcs[i]
        def __setitem__(self,i,w):
            self.pcs[i]=w
        def __getattr__(self,at):
            return getattr(self.pcs[0],at)
        def __len__(self):
            return len(self.pcs)
    def Process(self,a=None,**kwargs):
        if (a is None or a == NotImplemented) and kwargs=={}:
            raise TypeError(
                "you need either to specify process by first argument(PID or name) or by second argument(other properties)")
        if isinstance(a,int):
            return self._Process(a)
        elif isinstance(a,str):
            pcs=self.rescan(t=list)
            rs=[]
            for proc in pcs:
                if proc.name==a:
                     rs.append(self._Process(proc.pid))
            if kwargs:
                rs=self._buildList(rs,self.filter(**kwargs))
            return self.MakeProcessSet(rs)
        elif a is None or a == NotImplemented:
            return self.filter(caseNone=self.NotExistingProcess(),**kwargs)
        else:
            raise TypeError(
                            "Bad type of first argument. Avalaible types are: str (name), int (pid) , None or NotImplemented (check only for other properties)"
                            )
                
    def _buildList(self,a1,a2):
        a1=list(a1)
        a2=list(a2)
        g=[]
        for item in a1:
            if item in a2:
                g.append(item)
        return g
    def rescan(self,t=ProcessSet):
        _running=os.listdir('/proc')
        run=[]
        for proc in _running:
            try:
                proc=int(proc)
                try:
                    run.append(self.Process(proc))
                except NotADirectoryError:pass

            except ValueError:pass
            
        return t(run)
    def kill(self,proc=None,sig=9,*args,**kwargs):
        a=self.Process(proc,*args,**kwargs)
        a.kill(sig)
    def get_total_cpu(self=None):
        cr=open('/proc/stat').readline().split()[1:4]
        return sum([int(a) for a in cr])
    def MakeProcessSet(self,u,caseNone=NotExistingProcess()):
        if len(u)==0:
            return caseNone
        elif len(u)==1:
            return self.Process(u[0].pid)
        return self.ProcessSet(u)
    def filter(self,caseNone=[],**fields):
        if fields=={}:
            return self.running
        res=[]
        for item in self.running:
            for fieldname,w in fields.items():
                if not hasattr(item,fieldname):
                    raise ValueError("no such field : {}").format(fieldname)
                if getattr(item,fieldname)==w:
                    res.append(item)
        return self.MakeProcessSet(res,caseNone=caseNone)
    def find(self,*args,**kwargs):
        return self.Process(*args,**kwargs)
    def _cpu(self,pc):
        return -pc.cpu
    def runningTop(self):
        return self.MakeProcessSet(sorted(self.running,key=self._cpu))
    def ticks(self=NotImplemented):
        return int(subprocess.getoutput("getconf CLK_TCK"))
    def logout(self,signal=9,user=getpass.getuser()):
        self.kill(sig=signal,user=user)
    def _current(self):
        return self.find(os.getpid())
    CLK = ticks()
    uptime=property(lambda foo:float(open("/proc/uptime").read().split()[0]))
    totalcpu=property(get_total_cpu)
    running=property(rescan)
    top=property(runningTop)
    current=property(_current)
    signals=signals()
    RUNNING=RUNNING()
    SLEEPING=SLEEPING()
    UNKNOWN=UNKNOWN()
    STOPPED=STOPPED()
if platform.system()!='Linux':

    raise OSError("the pyproc2 package works only on Linux")
sys.modules[__name__]=pyproc2()
