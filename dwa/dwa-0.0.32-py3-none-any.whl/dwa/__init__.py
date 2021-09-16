__version__ = "0.0.32"
__keywords__ = ["tornado ajax wrapper framework"]


# if not __version__.endswith(".0"):
#     import re
#     print("version {} is deployed for automatic commitments only".format(__version__), flush=True)
#     print("install version " + re.sub(r"([0-9]+\.[0-9]+\.)[0-9]+", r"\g<1>0", __version__) + " instead")
#     import os
#     os._exit(1)


import os
import sys
sys.path.extend([os.path.dirname(os.path.abspath(__file__))])


import threading
import time
import re
import unicodedata
import traceback
import tornado
import tornado.web
import tornado.gen
import tornado.escape
import tornado.concurrent
import tornado.template
import core
import handlers
import workers
import requests
import aescipher
import sqlq
import filehandling
import unencryptedsocket
import threadwrapper
import omnitools
import lxml



class DWA(object):
    app_root = None
    app_settings = None
    app_workers = None
    ta = None

    def __init__(self, domain=None, port=None, cookies_expires_day=None):
        self.port = port
        self.domain = domain
        self.cookies_expires_day = cookies_expires_day
        self.clear()
        self.app_root = filehandling.abs_main_dir(2)
        sys.path.append(self.app_root)
        print("app root:", self.app_root)
        self.setup()

    def start_app_worker(self, raise_backend_errors):
        tw = threadwrapper.ThreadWrapper(threading.Semaphore(2**3))
        for app_worker in self.app_workers:
            tw.add(app_worker.start)
        tw.wait()
        p = threading.Thread(target=self.check_app_worker, args=(raise_backend_errors,))
        p.daemon = True
        p.start()

    def stop_app_worker(self):
        tw = threadwrapper.ThreadWrapper(threading.Semaphore(2**3))
        for app_worker in self.app_workers:
            tw.add(app_worker.stop)
        tw.wait()

    def check_app_worker(self, raise_backend_errors):
        def notify(app_worker):
            header = "Worker {} Exception".format(app_worker.__class__.__name__)
            reason = app_worker.exploded_reason
            handlers.BaseResponse.internal_error = True
            handlers.BaseResponse.internal_error_header = header
            handlers.BaseResponse.internal_error_reason = reason
            try:
                raise_backend_errors(header, reason)
            except:
                print(header)
                print(reason)
        stop = False
        while not stop:
            for app_worker in self.app_workers:
                if app_worker.exploded:
                    stop = True
                    notify(app_worker)
            if self.ta.sqlqueue:
                if self.ta.sqlqueue.ioerror:
                    stop = True
                    notify(self.ta.sqlqueue)
            if stop:
                break
            time.sleep(1)

    def setup(self):
        exec(open(os.path.join(self.app_root, "app.py"), "rb").read().decode(), globals())
        self.app_settings = globals()["app_settings"](self.app_root)
        self.app_settings["port"] = self.port or self.app_settings["port"]
        self.app_settings["domain"] = self.domain or self.app_settings["domain"]
        self.app_settings["cookies_expires_day"] = self.cookies_expires_day or self.app_settings["cookies_expires_day"]
        self.app_workers = globals()["app_workers"]()
        raise_backend_errors = self.app_settings["raise_backend_errors"]
        handlers.BaseResponse.app_root = self.app_root
        workers.base_worker.app_root = self.app_root
        handlers.BaseResponse.port = self.app_settings["port"]
        handlers.BaseResponse.cookies_domain = "." + self.app_settings["domain"]
        handlers.BaseResponse.cookies_expires_day = self.app_settings["cookies_expires_day"]
        handlers.BaseResponse.extra_headers = self.app_settings["extra_headers"]
        handlers.BaseResponse.under_maintenance = True
        handlers.BaseResponse.admin_contact = self.app_settings["admin_contact"]
        handlers.BaseResponse.grr_secret = self.app_settings["grr_secret"]
        workers.base_worker.under_maintenance = True
        if not os.path.isabs(self.app_settings["db"]):
            self.app_settings["db"] = os.path.join(self.app_root, self.app_settings["db"])
        def export_functions(k, *args, **kwargs):
            for app_worker in self.app_workers:
                f = app_worker.export_functions or {}
                if k in f:
                    try:
                        return f[k](*args, **kwargs)
                    except:
                        return traceback.format_exc()
            raise Exception("no function named: {}".format(k))
        class_export_functions = staticmethod(export_functions)
        self.ta = core.TA(
            self.app_settings["domain"],
            self.app_settings["servers"],
            self.app_settings["db"],
            self.app_settings["db_port"],
            self.app_settings["writer_port"],
            omnitools.sha3_512hd(self.app_settings["cookie_secret"]),
            self.app_settings["port"],
            export_functions=export_functions
        )
        @staticmethod
        def sql(*args, **kwargs):
            if self.ta.sqlqueue:
                result = self.app_settings["sql_watcher"](*args, sql=self.ta.sqlqueue.sql, **kwargs)
                if result != True:
                    if isinstance(result, Exception):
                        raise result
                    else:
                        raise Exception(result)
                result = self.ta.sqlqueue.sql(*args, **kwargs)
                if isinstance(result, str):
                    raise Exception(result)
                elif isinstance(result, Exception):
                    raise result
                return result
            else:
                return False
        @staticmethod
        def writer(*args, **kwargs):
            if self.ta.writer:
                return self.ta.writer.write(*args, **kwargs)
            else:
                return False
        handlers.BaseResponse.sql = sql
        handlers.BaseResponse.writer = writer
        workers.base_worker.sql = sql
        workers.base_worker.writer = writer
        handlers.BaseResponse.export_functions = class_export_functions
        self.ta.start()
        self.start_app_worker(raise_backend_errors)
        print("[server] started")
        self.interactive_input()

    @staticmethod
    def printTable(result, columns=None):
        def _len(s):
            length = 0
            for c in s:
                status = unicodedata.east_asian_width(c)
                if status in ["W", "F", "A"]:
                    length += 2
                else:
                    length += 1
            return length
        if not columns:
            columns = list(result[0].keys() if result else [])
        table = [columns]
        for row in result:
            table.append([str(row[column] if row[column] is not None else "") for column in columns])
        column_width = [max(map(_len,column)) for column in zip(*table)]
        table.insert(1, ["-" * i for i in column_width])
        for row in table:
            print("|".join([" {}{} ".format(column, " "*(column_width[i]-_len(column))) for i, column in enumerate(row)]))

    @staticmethod
    def clear():
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")

    def interactive_input(self):
        while True:
            print()
            print("Enter 'help' for commands.")
            command = input("> ")
            if not command:
                continue
            elif command == "help":
                print('''Commands:
        backup: Backup sqlite database
        commit: Commit sqlite database
        maintenance: Render server as '503 Service Unavailable'
        resume: Resume server from maintenance
        sql <SQL statement>: Execute SQL statement
        stop: Stop server and commit
        terminate: Force stop server''')
            elif command == "backup":
                self.ta.sqlqueue.backup()
                print("[sqlite] backup")
            elif command == "clear":
                self.clear()
            elif command == "commit":
                self.ta.sqlqueue.commit()
                print("[sqlite] committed")
            elif command == "maintenance":
                handlers.BaseResponse.under_maintenance = True
                workers.base_worker.under_maintenance = True
                print("[maintenance] True")
            elif command == "resume":
                handlers.BaseResponse.under_maintenance = False
                workers.base_worker.under_maintenance = False
                print("[maintenance] False")
            elif command.startswith("sql"):
                sql = command[4:]
                try:
                    while not sql.endswith(";"):
                        sql += " "+input("> ... ")
                except KeyboardInterrupt:
                    print()
                    continue
                data = []
                if "?" in sql:
                    last = sql.count("?")
                    for i in range(0, last):
                        _data = input("> data ({}/{}) ".format(i+1, last))
                        if _data.isdigit():
                            _data = int(_data)
                        data.append(_data)
                try:
                    result = self.ta.sqlqueue.sql(sql, tuple(data))
                    self.printTable(result)
                except:
                    pass
            elif command == "stop":
                print("[server] stopping")
                self.ta.stop(lambda : self.stop_app_worker())
                print("[server] exiting")
                time.sleep(2)
                return
            elif command == "terminate":
                print("[server] terminating")
                return
            else:
                print("! unknown command")
            print()


