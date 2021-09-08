# -*- coding: utf-8 -*-
import logging
import os
import socket


class AddMessageSourceInfo(logging.Filter):
    def filter(self, record):
        pid = os.getpid()
        ip = socket.gethostbyname(socket.gethostname())
        record.pid = pid
        record.ip = ip
        return True
