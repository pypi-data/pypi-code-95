# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-07-19 15:35:14
# @Last Modified by:   hang.zhang
# @Last Modified time: 2017-07-19 19:14:25
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ConfigParser
import argparse
import json
import re
import os

class log_monitor_server(FileSystemEventHandler):


    def on_modified(self, events):
        modified_file = events.src_path
        if os.path.abspath(str(modified_file)) in self.get_ignore_file():
            print "SKIP, modified file %s in ignore file list" % modified_file
            return
        print "file %s modified" % modified_file



    def start_monitor_server(self):
        self.args = self.parse_args()
        self.cfg = ConfigParser.ConfigParser()
        observer = Observer()
        observer.schedule(self, path=self.args.d, recursive=self.args.r)
        observer.start()
        # 这个会导致cpu的使用激增
        while True:
            pass
        observer.join()

    def parse_args(self):
        parser = argparse.ArgumentParser(description="日志监控服务")
        parser.add_argument("-d", help="监控目录，默认为当前目录", default="./")
        parser.add_argument("-r", help="递归监控目录", default=True)
        parser.add_argument("-cfg_file", help="监控目录，默认为当前目录", default="log_monitor.cfg")
        args = parser.parse_args()
        return args

    def get_ignore_file(self):
        self.cfg.read(self.args.cfg_file)
        return [os.path.abspath(ignore_file) for ignore_file in self.cfg.options("ignore")]


if __name__ == '__main__':
    log_monitor_server().start_monitor_server()
