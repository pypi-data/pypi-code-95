# **************************************************************************** #
#                           This file is part of:                              #
#                                BITSMITHS                                     #
#                           https://bitsmiths.co.za                            #
# **************************************************************************** #
#  Copyright (C) 2015 - 2021 Bitsmiths (Pty) Ltd.  All rights reserved.        #
#   * https://bitbucket.org/bitsmiths_za/bitsmiths                             #
#                                                                              #
#  Permission is hereby granted, free of charge, to any person obtaining a     #
#  copy of this software and associated documentation files (the "Software"),  #
#  to deal in the Software without restriction, including without limitation   #
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
#  and/or sell copies of the Software, and to permit persons to whom the       #
#  Software is furnished to do so, subject to the following conditions:        #
#                                                                              #
#  The above copyright notice and this permission notice shall be included in  #
#  all copies or substantial portions of the Software.                         #
#                                                                              #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
#  DEALINGS IN THE SOFTWARE.                                                   #
# **************************************************************************** #

import os
import os.path
import logging
import time

from .                 import common
from .                 import IProvider
from .sentinel_process import SentinelProcess
from .sentinel_thread  import SentinelThread


class SentinelManager:
    """
    The object that managers the sub threads and sub processes.
    """

    def __init__(self, cfg: dict, log: "logging.Logger", prov: "IProvider"):
        """
        Constructor.

        :param cfg: Configuration dictionary to use, {port, home_path, timeout}.
        :param log: The logger to use.
        :param prov: The provider object to use.
        """
        self._cfg       = cfg
        self._log       = log
        self._provider  = prov

        self._kill      = False
        self._term      = False
        self._pluggins  = {}
        self._processes = {}


    def __del__(self):
        """
        Destructor.
        """
        self.destroy()


    def shutting_down(self) -> bool:
        """
        Check to see if the SentinelManager is shutting down.

        :return: True if the sentinel manager is shutting down.
        """
        return self._term or self._kill


    def initialize(self, sent_config: dict):
        """
        Initialize the sentinel manager.

        :param sent_config: A dictionary or path of configuration file.
        """
        self.destroy()

        self._kill = False
        self._term = False

        self._log.info('Sentinal Manager initializing...')

        if type(sent_config) == str:
            scfg = common.read_config_dict_from_file(sent_config)
        elif type(sent_config) == dict:
            scfg = sent_config
        else:
            raise Exception('Cannot initialize sentinel with sent_config param of type [%s]' % (str(type(sent_config))))

        self._load_pluggins(scfg)
        self._load_processes(scfg)


    def destroy(self, max_time: float = 5.0):
        """
        Cleanup the manager, freeing all resrouces.
        """
        xt   = 0.0
        sec1 = max_time - 1.0
        kill = False

        while self.monitor_services():
            self.shutdown_services(kill=kill)
            xt += 0.2

            if xt >= max_time:
                break

            time.sleep(0.2)

            if not kill and xt >= sec1:
                kill = True

        self._pluggins  = {}
        self._processes = {}


    def kill(self):
        """
        Tell the manager to kill all processes.
        """
        self._kill = True
        self.shutdown_services(True)


    def shutdown(self):
        """
        Tell the manager to shutdown all processes.
        """
        self._term = True
        self.shutdown_services()


    def _import_dyn_pluggin(self, mpath: str):
        """
        Import a dyanmic plugging to be managed.

        :param mpath: Fully qaualified pluging path, eg: sysX.sentinel.pluggins.Fug.
        :return: (type, exception), if failure returns (None, Exception) else (type, None).
        """
        import importlib

        mparts = mpath.split('.')

        try:
            if len(mparts) == 1:
                raise Exception('Module path not valid, no path seperation.')
            else:
                fromList = '.'.join(mparts[0:-1])

                mod = importlib.import_module(fromList)
                obj = getattr(mod, mparts[-1])

            if type(obj) != type:
                raise Exception('Object is not a type.')

        except Exception as x:
            return None, x

        return obj, None


    def _load_pluggins(self, scfg: dict):
        """
        Loads all the pluggins that are to be managed.

        :param scfg: Sentinel dictionary config.
        """
        sentd = common.read_dict(scfg, 'sentinel', dict)
        plugs = sentd.get('pluggins')

        if not plugs:
            return

        if list != type(plugs):
            raise Exception('Config not valid, [sentinel:pluggins] not a list.')

        idx       = 0
        name_list  = []
        mpath_list = []

        self._log.debug('Loading pluggins [%d]' % len(plugs))

        for pl in plugs:
            par   = 'sentinel:pluggins[%d]:' % idx
            name  = common.read_dict(pl, 'name',          str,    par)
            mpath = common.read_dict(pl, 'module-path',   str,    par)
            rcnt  = common.read_dict(pl, 'run-count',     int,    par)
            pint  = common.read_dict(pl, 'proc-interval', float,  par)
            act   = common.read_dict(pl, 'active',        None,   par)

            if act is not None and not act:
                self._log.debug(' - Skipping in-active plugin [namd:%s, mpath:%s]'  % (name, mpath))
                continue

            if name in name_list:
                raise Exception('Duplicate name [name:%s] detected at idx [%d]' % (name, idx))

            if mpath in mpath_list:
                raise Exception('Duplicate module path [mpath:%s] detected, [name:%s, idx:%d]' % (mpath, name, idx))

            if rcnt < 1 or rcnt > 256:
                raise Exception('Run count [%d] is not valid, [name:%s, mpath:%s, idx:%d]' % (rcnt, name, mpath, idx))

            self._log.debug(' - importing pluggin [name:%s, mpath:%s, idx:%d]' % (name, mpath, idx))

            obj, err = self._import_dyn_pluggin(mpath)

            if err:
                self._log.error('Error while loading pluggin [name:%s, mpath:%s, error:%s]' % (name, mpath, str(err)))
                raise err

            plug  = {
                'name'      : name,
                'cls'       : obj,
                'mpath'     : mpath,
                'run-count' : rcnt,
                'proc-int'  : pint,
                'threads'   : [],
                'errors'    : [],
                'pods'      : [],
            }

            self._pluggins[name] = plug

            for tx in range(rcnt):
                o = obj()

                if not isinstance(o, SentinelThread):
                    raise Exception('Plugging is not of type [SentinelThread] - [name:%s, mpath:%s, idx:%d]' % (
                        name, mpath, idx))

                plug['threads'].append(o)
                plug['errors'].append(None)

            name_list.append(name)
            mpath_list.append(mpath)
            idx += 1


    def _load_processes(self, scfg):
        """
        Loads all the processes that are to be managed.

        :param scfg: Sentinel dictionary config.
        """
        sentd     = common.read_dict(scfg, 'sentinel', dict)
        procs     = sentd.get('processes')
        next_port = self._cfg['port'] + 1

        if not procs:
            return

        if list != type(procs):
            raise Exception('Config not valid, [sentinel:processes] not a list.')

        idx       = 0
        name_list  = []
        ppathList = []

        self._log.debug('Loading processes [%d]' % len(procs))

        for pl in procs:
            par   = 'sentinel:process[%d]:' % idx
            name  = common.read_dict(pl, 'name',          str,    par)
            ppath = common.read_dict(pl, 'proc-path',     str,    par)
            pargs = common.read_dict(pl, 'proc-args',     str,    par, optional=True)
            rcnt  = common.read_dict(pl, 'run-count',     int,    par)
            mport = common.read_dict(pl, 'manage-port',   bool,   par)
            port  = common.read_dict(pl, 'port',          int,    par, optional=True)
            act   = common.read_dict(pl, 'active',        bool,   par, optional=True)

            if not act:
                self._log.debug(' - Skipping in-active process [name:%s, ppath:%s]'  % (name, ppath))
                continue

            if name in name_list:
                raise Exception('Duplicate name [name:%s] detected at idx [%d]' % (name, idx))

            if rcnt < 1 or rcnt > 256:
                raise Exception('Run count [%d] is not valid, [name:%s, ppath:%s, idx:%d]' % (rcnt, name, ppath, idx))

            if mport:
                port      = next_port
                next_port += 1
            else:
                if port:
                    if type(port) != int:
                        raise Exception('Port [%s] is not a valid int, [name:%s, ppath:%s, idx:%d]' % (
                            str(port), name, ppath, idx))

            if port and (port < 1 or port > 65535):
                raise Exception('Port [%d] is out of range, [name:%s, ppath:%s, idx:%d]' % (
                    port, name, ppath, idx))

            ppath = os.path.expandvars(ppath)

            self._log.debug(' - adding process [name:%s, ppath:%s, idx:%d]' % (name, ppath, idx))

            if not os.path.exists(ppath):
                raise Exception('Process path [%s] not found, [name:%s, idx:%d]' % (ppath, name, idx))

            if not os.path.isfile(ppath):
                raise Exception('Process path [%s] is not a file, [name:%s, idx:%d]' % (ppath, name, idx))

            proc = {
                'name'      : name,
                'ppath'     : ppath,
                'pargs'     : pargs,
                'run-count' : rcnt,
                'mport'     : mport,
                'port'      : port,
                'procs'     : [],
                'ret-codes' : [],
                'msock'     : None,
            }
            self._processes[name] = proc

            procArgs = [ppath]

            if pargs:
                pargs     = os.path.expandvars(pargs)
                procArgs += str(pargs).split(' ')

            if mport:
                procArgs += ['--port', '%d:managed' % port]
            elif port:
                procArgs += ['--port', str(port)]

            procStr = ' '.join(procArgs)

            if procStr in ppathList:
                raise Exception('Duplicate process [%s] detected, [name:%s, idx:%d]' % (procStr, name, idx))

            for px in range(rcnt):
                o = SentinelProcess(name, procArgs, self._log, True, False)
                proc['procs'].append(o)
                proc['ret-codes'].append(None)

            name_list.append(name)
            ppathList.append(procStr)
            idx += 1


    def shutdown_services(self, pluggins: bool = True, processes: bool = True, kill: bool = False) -> None:
        """
        Shutdown all the services.

        :param pluggins: If true, shuts down all pluggins.
        :param processes: If true, shuts down all the processes.
        :param kill: If true kills the services instead of shutting them down.
        :return: Actual number of services shut down.
        """
        self._log.info('shutdown_services(kill:%s, pluggins:%s, processes:%s)' % (str(kill), str(pluggins), str(processes)))
        totdown = 0

        if pluggins:
            totdown += self.shutdown_pluggin(None, kill)

        if processes:
            totdown += self.shutdown_process(None, kill)

        return totdown


    def shutdown_pluggin(self, name: str = None, kill: bool = False) -> int:
        """
        Shutdown all or one pluggin.

        :param name: If not None, shuts down a specific plugging else it shuts them all down.
        :param kill: If true kills the pluggin instead of shutting them down.
        :return: The number of pluggins actually shut down.
        """
        totdown = 0

        for pname, pobj in self._pluggins.items():
            if name and name != pobj['name']:
                continue

            idx = 0

            for pt in pobj['threads']:
                idx += 1

                if not pt or not pt.is_alive():
                    continue

                if kill:
                    self._log.debug(' - killing thread [tid:%s, name:%s, idx:%d]' % (pt.tid(), pname, idx))
                    pt.kill()
                else:
                    self._log.debug(' - shutting down thread [tid:%s, name:%s, idx:%d]' % (pt.tid(), pname, idx))
                    pt.shutdown()

                totdown += 1

                if name:
                    break

        return totdown


    def shutdown_process(self, name: str = None, kill: bool = False) -> int:
        """
        Shutdown all or one pluggin.

        :param name: If not None, shuts down a specific processes else it shuts them all down.
        :param kill: If true kills the process instead of shutting them down.
        :return:  The number of processess actually shut down.
        """
        totdown = 0

        for pname, pobj in self._processes.items():
            if name and name != pobj['name']:
                continue

            idx = 0

            for pt in pobj['procs']:
                idx += 1

                if not pt or not pt.is_alive():
                    continue

                if kill:
                    self._log.debug(' - killing process [pid:%s, name:%s, idx:%d]' % (pt.pid(), pname, idx))
                    pt.kill()
                else:
                    self._log.debug(' - shutting down process [pid:%s, name:%s, idx:%d]' % (pt.pid(), pname, idx))
                    pt.shutdown()

                totdown += 1

                if name:
                    break

        return totdown


    def start_services(self, pluggins: bool = True, processes: bool = True):
        """
        Start all the services.

        :param pluggins: If true, start all the pluggins.
        :param processes: If true, start all the processes.
        """
        if pluggins:
            self.start_pluggings(None, req_only=True)

        if processes:
            self.start_processes(None, req_only=True)

        if pluggins:
            self.start_pluggings(None)

        if processes:
            self.start_processes(None)


    def start_pluggings(self, name: str = None, req_only: bool = False):
        """
        Start pluggins.

        :param name: The name of the specific pluggin to start, else all pluggins are started.
        :param req_only: If true, don't start the pluggin, just allocate the requirements for the pluggin.
        """
        self._log.info('Starting sentinel pluggins [name:%s, req_only:%s]' % (str(name), str(req_only)))

        for pname, pobj in self._pluggins.items():
            self._log.debug(' - Starting [name:%s, module:%s, run-count:%d, procInterval:%lf]' % (
                pobj['name'], pobj['mpath'], pobj['run-count'], pobj['proc-int']))

            cnt = 0

            for idx in range(len(pobj['threads'])):
                pt = pobj['threads'][idx]

                if pt:
                    if pt.is_alive():
                        continue

                    if pt.ident:
                        pt                   =\
                        pobj['threads'][idx] = None

                if not pt or not pt.ident:
                    pt = pobj['cls']()
                    pobj['errors'][idx]  = None
                    pobj['threads'][idx] = pt

                if pobj['proc-int'] > 0.0:
                    pt.set_process_interver(pobj['proc-int'])

                if pt.pod_required():
                    while len(pobj['pods']) <= idx:
                        pobj['pods'].append(None)

                    if not pobj['pods'][idx]:
                        pobj['pods'][idx] = self._new_pod(pname, pobj)

                    pt.set_pod(pobj['pods'][idx])

                if not req_only:
                    pt.start()
                    cnt += 1

            self._log.debug('   ...started [%d] pluggins.' % cnt)


    def start_processes(self, name: str = None, req_only: bool = False):
        """
        Start processes.

        :param name: The name of the specific process to start, else all processes are started.
        :param req_only: If true, don't start the process, just allocate the requirements for the process.
        """
        self._log.info('Starting sentinel processes [name:%s, req_only:%s]' % (str(name), str(req_only)))

        for pname, pobj in self._processes.items():
            self._log.debug(' - Starting [name:%s, ppath:%s, run-count:%d]' % (pobj['name'], pobj['ppath'], pobj['run-count']))

            self._port_manage(pobj)

            cnt = 0

            for idx in range(len(pobj['procs'])):
                pp = pobj['procs'][idx]

                if not pp:
                    procArgs = [pobj['ppath']]

                    if pobj['pargs']:
                        pobj['pargs'] = os.path.expandvars(pobj['pargs'])

                        procArgs += str(pobj['pargs']).split(' ')

                    if pobj['mport'] and pobj['msock']:
                        procArgs += ['--port', '%d:%d' % (pobj['port'], pobj['msock']._sock.fileno())]
                    elif pobj['port']:
                        procArgs += ['--port', str(pobj['port'])]

                    pp = SentinelProcess(pobj['name'], procArgs, self._log, True, False)
                    pobj['procs'][idx]     = pp
                    pobj['ret-codes'][idx] = None

                if pp.is_alive():
                    continue

                if not req_only:
                    if pobj['msock']:
                        pp.start([pobj['msock']._sock.fileno()])
                    else:
                        pp.start()
                    cnt += 1

            self._log.debug('   ...started [%d] processes.' % cnt)


    def _new_pod(self, pname: str, pobj: dict):
        """
        Virtual Method to initialize your pods.

        :param pname: The pluggin name.
        :param pobj: The pluggin dictionary object.
        :return:  The newly created pod.
        """
        dbcon = None
        pod   = None

        try:
            dbcon = self._provider.new_db_connector(self._cfg)
            pod   = self._provider.new_pod(self._cfg, self._log, dbcon)

            return pod

        except Exception:
            del pod
            del dbcon
            raise


    def _port_manage(self, pobj: dict):
        """
        Open the port for the process object and manage it if required.

        :param pobj: The processes object.
        """
        if not pobj['mport'] or pobj['msock']:
            return

        from mettle.braze.tcp.SocketTcpServer import SocketTcpServer

        po = SocketTcpServer(self._cfg.get('timeout') or 5.0, 5)  # timeout and retrys
        po.open(str(pobj['port']), 5, True)

        pobj['msock'] = po

        self._log.debug('Opened port (name:%s, port:%s, fd:%d)' % (
            pobj['name'], str(pobj['port']), pobj['msock']._sock.fileno()))


    def _port_close(self, pobj: dict):
        """
        Closes the managed port for the pobj.

        :param pobj: the processes object.
        """
        if not pobj['msock']:
            return

        self._log.debug('Closing port (name:%s, port:%s, fd:%d)' % (
            pobj['name'], str(pobj['port']), pobj['msock']._sock.fileno()))

        pobj['msock'].close()
        pobj['msock'] = None


    def monitor_services(self, wait: bool = False) -> int:
        """
        Monitors all the services.

        :param wait: If True, wait for all the threads to join.
        :return: Number of services still running.
        """
        alive = 0
        alive += self.monitor_pluggins()
        alive += self.monitor_processes()

        return alive


    def monitor_pluggins(self, wait: bool = False) -> int:
        """
        Monitors the pluggins to see if they have failed or not.

        :param wait: If True, wait for all the threads to join.
        :return: The number of alive pluggings.
        """
        while True:
            alive = 0

            for pname, pobj in self._pluggins.items():
                for idx in range(len(pobj['threads'])):
                    pt = pobj['threads'][idx]

                    if not pt:
                        continue

                    if pt.is_alive():
                        alive += 1
                        continue

                    if not pt._shutdown:
                        continue

                    pt.join()

                    if len(pobj['pods']) > idx:
                        pod = pobj['pods'][idx]

                        if pod:
                            if pod.dbcon:
                                del pod.dbcon
                            pobj['pods'][idx] = None

                    errs = pt.get_errors()

                    return {'errorCode' : self._err_code, 'exception' : self._err_except, 'message' : self._err_msg}

                    if errs:
                        self.notify_child_ended(errs['errorCode'],
                                                None,
                                                pt.tid(),
                                                pt.name,
                                                f"{errs['exception']} : {errs['message']}")

                    else:
                        self.notify_child_ended(0, None, pt.tid(), pt.name, None),

                    pobj['errors'][idx]  = errs
                    pobj['threads'][idx] = None

            if alive == 0 or not wait:
                break

        return alive


    def monitor_processes(self, wait: bool = False) -> int:
        """
        Monitors the processes to see if they have failed or not.

        :param  wait: If True, wait for all the processes to end.
        :return: The number of alive processes.
        """
        while True:
            alive = 0

            for pname, pobj in self._processes.items():
                palive = 0
                for idx in range(len(pobj['procs'])):
                    pp = pobj['procs'][idx]

                    if not pp:
                        continue

                    if pp.is_alive():
                        alive  += 1
                        palive += 1
                        continue

                    self.notify_child_ended(pp._rc, pp.pid(), None, pp.name, pp.proc_std_err())

                    pobj['ret-codes'][idx] = pp._rc
                    pobj['procs'][idx]     = None

                if palive < 1:
                    self._port_close(pobj)

            if alive == 0 or not wait:
                break

        return alive


    def notify_child_ended(self, ec: int, pid: str, tid: str, name: str, error_msg: str = None) -> None:
        """
        Virtual method, this is called when a pluggin or process ends.

        :param ec: Error code. Zero means success, any non zero is a failure.
        :param pid: The process id if the child was a process.
        :param tid: The thread id if child was a pluggin.
        :param name: The name of the process/pluggin.
        :param error_msg: Optionally error message if there is one.
        """
        if ec == 0:
            if pid:
                self._log.info(f"Process [name:{name}, pid:{pid}] completed without errors.")
            elif tid:
                self._log.info(f"Thread [name:{name}, tid:{tid}] completed without errors.")
            else:
                self._log.warning(f"Something [name:{name}] completed without errors.")

            return

        if pid:
            self._log.warning(f"Process [name:{name}, pid:{pid}] failed with errors [rc:{ec}, msg:{error_msg}]")
        elif tid:
            self._log.warning(f"Thread [name:{name}, tid:{tid}] failed with errors [ec:{ec}, msg:{error_msg}]")
        else:
            self._log.warning(f"Something [name:{name}] failed with errors [rc:{ec}, msg:{error_msg}]")
