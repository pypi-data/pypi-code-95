# -*- coding: utf-8 -*-


import json
import re

import bottle


class HttpRequestDetector:
    """
    Helper class that retrieves parameters from HTTP requests.
    """

    @staticmethod
    def detect_platform(req: bottle.Request) -> str:
        """
        Detects the platform (using "user-agent") from which the given HTTP request was made.

        :param req: an HTTP request to process.
        :return: the detected platform and version. Detectable platforms: "mobile", "iphone",
        "ipad",  "macosx", "android",  "webos", "mac", "windows". Otherwise - "unknown" will
        be returned.
        """
        ua = req.headers['user-agent']
        if re.search(r'mobile', ua, re.I):
            return 'mobile'
        if re.search(r'like Mac OS X', ua):
            version = re.sub(r'_', '.', re.search(r'CPU( iPhone)? OS ([0-9._]+) like Mac OS X', ua)[2])
            if re.search(r'iPhone', ua):
                return 'iphone ' + version
            if re.search(r'iPad', ua):
                return 'ipad ' + version
            return 'macosx ' + version
        if re.search(r'Android', ua):
            version = re.search(r'Android ([0-9.]+)[);]', ua)[1]
            return 'android ' + version
        if re.search(r'webOS/', ua):
            version = re.search(r'webOS/([0-9.]+)[);]', ua)[1]
            return 'webos ' + version
        if re.search(r'(Intel|PPC) Mac OS X', ua):
            version = re.sub(r'_', '.', re.search(r'(Intel|PPC) Mac OS X ?([0-9._]*)[);]', ua)[2])
            return 'mac ' + version

        if re.search(r'Windows NT', ua):
            version = re.search(r'Windows NT ([0-9._]+)[);]', ua)[1]
            return 'windows ' + version
        else:
            return 'unknown'

    @staticmethod
    def detect_browser(req: bottle.Request) -> str:
        """
        Detects the browser (using "user-agent") from which the given HTTP request was made.

        :param req: an HTTP request to process.
        :return: the detected browser. Detectable browsers: "chrome", "msie", "firefox",
        "safari". Otherwise - "unknown" will be returned.
        """
        ua = req.headers['user-agent']
        if re.search(r'chrome', ua, re.I):
            return 'chrome'
        if re.search(r'msie', ua, re.I):
            return 'msie'
        if re.search(r'firefox', ua, re.I):
            return 'firefox'
        if re.search(r'safari', ua, re.I):
            return 'safari'

        return ua or 'unknown'

    @staticmethod
    def detect_address(req: bottle.Request) -> str:
        """
        Detects the IP address from which the given HTTP request was received.

        :param req: an HTTP request to process.
        :return: the detected IP address (without a port). If no IP is detected -
        **None** will be returned.
        """
        ip = None
        if req.get_header('x-forwarded-for'):
            ip = req.get_header('x-forwarded-for').split(',')[0]

        json_data = req.json

        if not isinstance(json_data, dict) and json_data is not None:
            json_data = json.loads(str(json_data))

        if ip is None and json_data and 'connection' in json_data.keys():
            try:
                ip = json_data['connection']['remoteAddress']
            except KeyError:
                try:
                    ip = json_data['connection']['socket']['remoteAddress']
                except KeyError:
                    pass

        if ip is None:
            try:
                ip = json_data['socket']['remoteAddress']
            except KeyError:
                pass

        if ip is not None:
            ip = str(ip)
            index = ip.find(':')
            if index > 0:
                ip = ip[0:index]

        return ip

    @staticmethod
    def detect_server_host(req: bottle.Request) -> str:
        """
        Detects the host name of the request's destination server.

        :param req: an HTTP request to process.
        :return: the destination server's host name.
        """
        return '' + req.get_header('host').split(':')[0]

    @staticmethod
    def detect_server_port(req: bottle.Request) -> str:
        """
        Detects the request's destination port number.

        :param req: an HTTP request to process.
        :return: the detected port number or **80** (if none are detected).
        """
        return req.get_header('host').split(':')[1]
