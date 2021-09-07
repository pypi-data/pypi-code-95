from __future__ import annotations
import sys, subprocess
from typing import Callable
from threading import Condition, Thread
from queue import Queue, Empty
import json
import uuid
import traceback

from limes_common.utils import current_time
from . import Connection
from limes_common import config
from limes_common.models import Model, Primitive, provider as Models, ssh

_QUOTE = '\\q'
def Serialize(model: Model) -> str:
    return Console_Encode(json.dumps(model.ToDict()))
def Console_Encode(serial: str) -> str:
    return '"%s"' % (serial.replace('"', _QUOTE))
def Console_Decode(serial: str) -> str:
    return serial.replace(_QUOTE, '"')
# M = TypeVar('M')
# def Console_Decode(string: str, constr: Callable[[str], M]) -> M:
    # return constr(string.replace(_QUOTE, '"'))

class MessageID:
    def __init__(self, uuid: str = uuid.uuid4().hex) -> None:
        self.__uuid = uuid

    def AsHex(self):
        return self.__uuid
        
class SshConnection(Connection):
    class _Pipe:
        def __init__(self, io:subprocess.IO[bytes], lock: Condition=Condition(), q: Queue=Queue()) -> None:
            self.IO = io
            self.Lock = lock
            self.Q = q

    class _SshConsole:
        def __init__(self, console: subprocess.Popen[bytes], onOut: Callable[[str], None], onErr: Callable[[str], None],
                timeout: float) -> None:
            ios = {}
            for name, io in [('in', console.stdin), ('out', console.stdout), ('err', console.stderr)]:
                if io is None:
                    raise ValueError('an io is missing')
                else:
                    ios[name] = io
            self._in = SshConnection._Pipe(ios['in'])
            self._out = SshConnection._Pipe(ios['out'])
            self._err = SshConnection._Pipe(ios['err'])
            self._onCloseLock = Condition()
            self._closed = False

            workers: list[Thread] = []
            def reader(pipe: SshConnection._Pipe, callback: Callable[[str], None]):
                io = iter(pipe.IO.readline, b'')
                while True:
                    try:
                        line = next(io)
                    except (StopIteration, ValueError):
                        break
                    chunk = bytes.decode(line, encoding=config.ENCODING)
                    callback(chunk)
                self.Dispose()
            workers.append(Thread(target=reader, args=[self._out, onOut]))
            workers.append(Thread(target=reader, args=[self._err, onErr]))

            def timeoutTask():
                self._onCloseLock.acquire()
                self._onCloseLock.wait(timeout)
                self._onCloseLock.release()
                self.Dispose()
            workers.append(Thread(target=timeoutTask))
                
            for w in workers:
                w.daemon = True # stop with program
                w.start()

        def IsClosed(self) -> bool:
            self._onCloseLock.acquire()
            closed = self._closed
            self._onCloseLock.release()
            return closed

        def __write(self, pipe: SshConnection._Pipe, statement: str):
            # msg = ' '.join([cmd] + [Console_Encode(arg) for arg in args])
            pipe.IO.write(bytes('%s\n' % (statement), encoding=config.ENCODING))

        def Send(self, statement:str):
            stdin = self._in
            stdin.Lock.acquire()
            self.__write(stdin, statement)
            stdin.IO.flush()
            stdin.Lock.release()

        def BatchSend(self, statements: list[str]):
            stdin = self._in
            stdin.Lock.acquire()
            for s in statements:
                self.__write(stdin, s)
            stdin.IO.flush()
            stdin.Lock.release()

        def Dispose(self):
            self._onCloseLock.acquire()
            if self._closed:
                self._onCloseLock.release()
                return
            self._closed = True
            self._onCloseLock.notify_all()
            self._onCloseLock.release()
            try:
                self.Send('logout')
            except BrokenPipeError:
                pass
            for p in [self._in, self._out, self._err]:
                p.Lock.acquire()
                try:
                    p.IO.close()
                except BrokenPipeError:
                    pass
                p.Lock.release()

    class _Transaction:
        def __init__(self) -> None:
            self.Lock = Condition()
            self.Packets: Queue[str] = Queue()
            self.Errors: Queue[str] = Queue()
        
        def _sync(self, fn):
            self.Lock.acquire()
            fn()
            self.Lock.release()

        def Notify(self):
            self._sync(lambda: self.Lock.notify_all())
        
        def Wait(self, timeout: float):
            self._sync(lambda: self.Lock.wait(timeout))

    def __init__(self,
            url:str, setup: list[str], cmd: str,
            transactionTimeout:float, keepAliveTime:float,
            identityFile: str = None) -> None:
        super().__init__()
        self._transactions: dict[str, SshConnection._Transaction] = {}
        self._transactionTimeout = transactionTimeout
        self._keepAliveTime = keepAliveTime
        self._url = url
        self._identityFile = identityFile
        self._setup = setup
        self._cmd = cmd
        self.__connection = self._getCon()

        self._onResponseSubscribers = []
        self._onErrorSubScribers = []

    def _getCon(self) -> _SshConsole:
        cmd = ['ssh', '-tt', self._url]
        if self._identityFile is not None:
            cmd += ['-i', self._identityFile]
        # print(cmd)
        p = subprocess.Popen(cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
                    # time.sleep(2)
        setup = self._setup
        
        def onOut(msg):
            for cb in self._onResponseSubscribers:
                cb(msg)

            # if self.x == 0: print('>%s' % msg)
            if msg.startswith(Handler.SEND_FLAG):
                msg = msg[len(Handler.SEND_FLAG):]
                parsed = ssh.Message.Parse(msg)
                if parsed.MessageID in self._transactions:
                    tr = self._transactions[parsed.MessageID]
                    if parsed.IsError:
                        print('provider error: %s' % parsed.Body)
                        tr.Notify()
                    else:
                        tr.Packets.put(parsed.Body)
                        tr.Notify()
                else:
                    # print(parsed.MessageID)
                    # print([self._transactions.keys()])
                    print('unregistered message: %s'%msg)

        def onErr(msg):
            for cb in self._onErrorSubScribers:
                cb(msg)
            # if self.x == 0: print('er>%s' % msg)
            if not msg.startswith('Connection to') and not msg.endswith('closed.'):
                print('Fatal error> ' + msg)

        con = SshConnection._SshConsole(p, onOut, onErr, self._keepAliveTime)
        con.BatchSend(setup)
        return con

    def _send(self, ep:str, model: Model|None = None) -> MessageID:
        if self.__connection.IsClosed():
            self.__connection = self._getCon()

        cmd = self._cmd
        mid = MessageID()
        ser = Console_Encode(json.dumps(model.ToDict())) if model is not None else ''
        statement = '%s %s %s %s' % (cmd, mid.AsHex(), ep, ser)
        self.__connection.Send(statement)
        return mid

    def _listenFor(self, mid: MessageID, timeout:float=0) -> tuple[bool, str]:
        if timeout==0:
            timeout = self._transactionTimeout
        tr = SshConnection._Transaction()
        self._transactions[mid.AsHex()] = tr
        tr.Wait(timeout)
        try:
            return True, tr.Packets.get_nowait()
        except Empty:
            return False, ''

    def _makeTransaction(self, ep: str, body: Model|None = None) -> tuple[bool, str]:
        mid = self._send(ep, body)
        return self._listenFor(mid)

    def AddOnResponseCallback(self, fn: Callable[[str], None]) -> None:
        self._onResponseSubscribers.append(fn)

    def AddOnErrorCallback(self, fn: Callable[[str], None]) -> None:
        self._onErrorSubScribers.append(fn)

    def RemoveOnResponseCallback(self, fn: Callable[[str], None]) -> None:
        self._onResponseSubscribers.remove(fn)

    def RemoveOnErrorCallback(self, fn: Callable[[str], None]) -> None:
        self._onResponseSubscribers.remove(fn)

    # def CheckStatus(self, echo: str) -> Models.Status.Response:
    #     success, res = self._makeTransaction(ProviderEndpoint.CHECK_STATUS, Models.Status.Request(echo))
    #     if success:
    #         return Models.Status.Response.Parse(res)
    #     else:
    #         return Models.Status.Response(False, res)

    def GetSchema(self) -> Models.Schema:
        success, res = self._makeTransaction(Models.Endpoints.GET_SCHEMA)
        if success:
            return Models.Schema.Parse(res)
        else:
            return Models.Schema()

    def MakeRequest(self, request: Models.ProviderRequest) -> Models.GenericResponse:
        success, res = self._makeTransaction(request.TargetEndpoint, request)
        if success:
            resModel = Models.GenericResponse.Parse(res)
            return resModel
        else:
            err = Models.GenericResponse()
            err.Code = 503
            err.Error = 'connection failed'
            return err

    # todo: remove redundancy with make request
    def Search(self, query: str) -> Models.Search.Response:
        req = Models.Search.Request()
        req.Query = query
        success, res = self._makeTransaction(Models.Endpoints.SEARCH, req)
        if success:
            resModel = Models.Search.Response.Parse(res)
            return resModel
        else:
            err = Models.Search.Response()
            err.Code = 503
            err.Error = 'connection failed'
            return err

    def Dispose(self):
        self.__connection.Dispose()

class BadRequestException(Exception):
    pass

class Handler:
    SEND_FLAG = 'From Handler > '
    def __init__(self) -> None:
        self._lastRawRequest = ''

    def HandleCommandLineRequest(self) -> None:
        self._lastRawRequest = sys.argv
        if len(sys.argv) == 4:
            rmid, endpoint, body = sys.argv[1:]
        else:
            rmid, endpoint = sys.argv[1:]
            body = '{}'
        mid = MessageID(rmid)
        body = Console_Decode(body)

        def getHandlerMethod():
            PREFIX = '_parse'
            SUFFIX = 'Request'
            getMethod = lambda path: '%s_%s_%s' % (PREFIX, path, SUFFIX)
            # self._send(MessageID(), endpoint, True)
            for ep in Models.Endpoints.Paths():
                candidate = ep
                if candidate != endpoint: continue
                method = getMethod(candidate.title())
                myMethods = [m for m in dir(self) if m.startswith(PREFIX)]
                for m in myMethods:
                    if method == m:
                        return getattr(self, m)
                return method
            return self._parse_Generic_Request
        handler = getHandlerMethod()

        if isinstance(handler, str):
            self._send(mid, 'expectd method [%s] for endpoint [%s] not implimented' % (handler, endpoint), True)
        else:
            try:
                res = handler(endpoint, body)
                self._send(mid, json.dumps(res.ToDict()))
            except Exception as e:
                self._send(mid, '\n%sendpoint: %s'%(str(traceback.format_exc()), endpoint), True)
        pass

    def _send(self, mid: MessageID, msg: str, isError:bool = False):
        serialized = json.dumps(ssh.Message(mid.AsHex(), msg, isError).ToDict())
        print(Handler.SEND_FLAG + serialized)

    # def _parseStatusRequest(self, raw: str):
    #     return self.OnStatusRequest(Models.Status.Request.Parse(raw))
    # def OnStatusRequest(self, req: Models.Status.Request) -> Models.Status.Response:
    #     return Models.Status.Response(False, req.Msg, 'This is an abstract Provider and must be implemented')

    def _parse_Schema_Request(self, ep:str, raw: str) -> Models.Schema:
        return self.On_Schema_Request()
    def On_Schema_Request(self) -> Models.Schema:
        example = Models.Service()
        example.Endpoint = 'Abstract_service_example'
        example.Input = {'a': str, 'b': bool}
        example.Output = {'x': int}
        sch = Models.Schema()
        sch.Services = [example]
        return sch

    def _parse_Generic_Request(self, ep: str, raw: str) -> Models.GenericResponse:
        req = Models.GenericRequest.Parse(raw) # todo: dedicated primitive model
        try:
            if ep == '':
                res = Models.GenericResponse()
                res.Code = 400
                res.Error = 'Endpoint can not be empty'
                return res
            return self.On_Generic_Request(ep, req.Body)
        except Exception as e:
            return Models.GenericResponse({}, 500, str(e))
        
    def On_Generic_Request(self, endpoint: str, body: Primitive) -> Models.GenericResponse:
        """
        @purpose: name of service being invoked
        @data: data dict expected to follow the schema described by Service.Input
        @return: performs service listed by OnSchemaRequest() and return in form of Service.Output
        """
        res = Models.GenericResponse()
        res.Code = 500
        res.Error = 'provider not implemented!'
        return res

    def _parse_Search_Request(self, ep: str, raw: str) -> Models.Search.Response:
        req = Models.Search.Request.Parse(raw)
        try:
            return self.On_Search_Request(req.Query)
        except Exception as e:
            res = Models.Search.Response()
            res.Code = 500
            res.Error = str(e)
            return res

    def On_Search_Request(self, query: str) -> Models.Search.Response:
        res = Models.Search.Response()
        res.Code = 500
        res.Error = 'search not implemented!'
        return res
