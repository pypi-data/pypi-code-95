import tornado.web
import tornado.ioloop
import tornado.platform.asyncio
import asyncio
import threading
import time
import filehandling
import sqlq
import re
import handlers


__ALL__ = ["TA"]


asyncio.set_event_loop_policy(tornado.platform.asyncio.AnyThreadEventLoopPolicy())


class TA(object):
    sqlqueue = None
    writer = None

    def __init__(
            self, domain: str, servers: dict,
            db: str, db_port: int, writer_port: int,
            cookie_secret: str,
            port: int = 8888,
            xsrf_cookies: bool = True, compress_response: bool = True,
            export_functions = None
    ):
        def _translate_host(server, pages, i):
            NotFound_page = handlers.NotFound
            if server == "" or server == "root":
                host = domain
            elif re.search(r"[0-9]{1,3}(\.[0-9]{1,3}){3}", server):
                host = server
            elif server == "*":
                host = ".*\.?"+domain
            else:
                NotFound_page = type("NotFound_{}".format(server), (handlers.NotFound,), {"server": server})
                host = server+"."+domain
            print("Server {}.1: {}".format(i+1, host))
            servers = [(tornado.web.HostMatches(host), pages+[(r"/(.*)", NotFound_page)])]
            if host != server and server != "*":
                print("Server {}.2: {}".format(i+1, "test."+host))
                File_page = type("File_test_{}".format(server), (handlers.File,), {"server": server})
                servers.append((tornado.web.HostMatches("test."+host), pages+[(r"/(.*\.(?:html|css|js|png|jpeg|jpg|svg|bmp))", File_page)]))
            return servers
        _handlers = []
        for i, (k, v) in enumerate(servers.items()):
            _handlers += _translate_host(k, v, i)
        _handlers.append((tornado.web.HostMatches(r".*"), [(r"/(.*)", handlers.NotFound)]))
        self.app = tornado.web.Application(
            _handlers,
            cookie_secret=cookie_secret,
            xsrf_cookies=xsrf_cookies,
            compress_response=compress_response,
        )
        self.port = port
        if db_port > 0:
            self.sqlqueue = sqlq.SqlQueueU(server=True, db=db, db_port=db_port, timeout_commit=30*1000, auto_backup=False, export_functions=export_functions)
        if writer_port > 0:
            self.writer = filehandling.WriterU(server=True, writer_port=writer_port)

    def _start(self) -> None:
        self.server = self.app.listen(self.port)
        self.server_loop = tornado.ioloop.IOLoop.instance()
        self.server_loop.start()

    def start(self) -> None:
        p = threading.Thread(target=self._start)
        p.daemon = True
        p.start()

    def stop(self, stop_app_worker) -> None:
        self.server_loop.stop()
        self.server.stop()
        while True:
            if len(handlers.SuccessHandler.rh) == 0:
                break
            print("no. of requests remaining:", len(handlers.SuccessHandler.rh), flush=True)
            time.sleep(0.5)
        stop_app_worker()
        if self.sqlqueue:
            self.sqlqueue.commit()
            self.sqlqueue.stop()
        if self.writer:
            self.writer.stop()


