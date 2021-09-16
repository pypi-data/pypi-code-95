# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-07-19 12:00:42
# @Last Modified by:   hang.zhang
# @Last Modified time: 2017-07-19 15:25:33

"""
日志监控,可以重载参数以指定变更内容写入到哪里


CREATE TABLE `easyspider_log` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `spider` varchar(100) DEFAULT NULL,
  `logging_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `logger` varchar(100) DEFAULT NULL,
  `logging_level` varchar(20) DEFAULT NULL,
  `info` text,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `state` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `spider` (`spider`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;


"""

from watchdog.observers import Observer
# from watchdog_file_modify_handler import watchdog_file_modify_handler
from watchdog.events import FileSystemEventHandler
import argparse
import json
import re
import os


monitor_log_file = "file_monitor_log.rate"

log_file_re_check = re.compile(".*\.log$")

log_parser_rex = re.compile("(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\[[\w\.]+\]) (\w+): (.*?)(?=\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\n*")

# def log_parser(content):
#     result = log_parser_rex.findall(content, re.S)
#     return result
def log_parser(content):
    result = re.findall(
        "(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\[[\w\.]+\]) (\w+): (.*?)(?=\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", content, re.S)
    return result

#class base_log_monitor(watchdog_file_modify_handler):
class base_log_monitor(FileSystemEventHandler):

    def modified_callback(self, modified_file_name, modified_content):
        if not self.is_target_file_type(modified_file_name):
            print "not target file %s" % modified_file_name
            return
        # print "file %s modified, content is %s \n\n\n re content is %s" % (modified_file_name, modified_content, log_parser(modified_content))
        # log_content = log_parser(modified_content)
        # if not log_content:
        #     print "no log parse content is %s" % modified_content
        #     return
        
        # print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        # with open("../xxx.test", "a") as f:
        #     for log in log_content:
        #         logging_time, logger, logging_level, info = log
        #         f.write("%s %s %s %s" % (logging_time, logger, logging_level, info))
        print "is target file %s" % modified_file_name
        with open("../xxx.test", "a") as f:
            f.write(modified_content)

    def is_target_file_type(self, file_name):
        return log_file_re_check.findall(file_name)

    def parse_args(self):
        parser = argparse.ArgumentParser(description="日志监控服务")
        parser.add_argument("-d", help="监控目录，默认为当前目录", default="./")
        args = parser.parse_args()

        return args

    def start_monitor(self):
        args = self.parse_args()
        monitor_path = args.d
        observer = Observer()
        print monitor_path
        observer.schedule(self, path=monitor_path, recursive=True)
        observer.start()
        while True:
            pass
        observer.join()

    def on_modified(self, events):
        modified_file = str(events.src_path)
        if os.path.abspath(modified_file) == os.path.abspath(monitor_log_file) or os.path.isdir(modified_file):
            #print "SKIP, %s" % modified_file
            return
        #print "type is %s %s" % (type(modified_file), type(monitor_log_file))
        #print "moified file name %s, %s == %s is %s" % (modified_file, modified_file, monitor_log_file, os.path.abspath(modified_file)==os.path.abspath(monitor_log_file))
        modified_content = get_last_modify_content(modified_file)
        self.modified_callback(modified_file, modified_content)



def record_file_tail(f, monitor_file_name, record_file=monitor_log_file):
    with open(record_file, "w") as recorder:
        recorder.write(json.dumps(
            {monitor_file_name: f.tell()}, ensure_ascii=False, indent=2))


def resume_last_node(file_name, monitor_file_name=monitor_log_file):
    if not os.path.exists(monitor_file_name):
        print "no monitor_file_name file"
        return 0
    with open(monitor_file_name) as f:
        try:
            monitor_log = json.load(f)
        except Exception, e:
            print e,"file_name %s" % file_name
            return 0
    last_node = monitor_log.get(file_name, 0)
    print "monitor_log.get(%s, 0)  = %s" % (file_name, last_node)
    return last_node


def get_last_modify_content(modified_file):
    last_node = resume_last_node(modified_file)
    modify_content = ""
    with open(modified_file) as f:
        print "seek %s" % last_node
        f.seek(last_node)
        modify_content = f.read()
        record_file_tail(f, modified_file)
    return modify_content




if __name__ == '__main__':
    base_log_monitor().start_monitor()