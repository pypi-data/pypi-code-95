"""
Created on 20 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import pycurl

import urllib.parse


# --------------------------------------------------------------------------------------------------------------------

class HTTPStreamingClient(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__listener = None
        self.__conn = None


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self, listener, host, path, payload):
        # listener...
        self.__listener = listener

        # data...
        params = urllib.parse.urlencode(payload) if payload else None
        query = path + '?' + params if params else path

        url = 'https://' + host + query

        self.__conn = pycurl.Curl()
        self.__conn.setopt(pycurl.URL, url)
        self.__conn.setopt(pycurl.WRITEFUNCTION, self.__local_listener)

        self.__conn.perform()


    def close(self):
        if not self.__conn:
            return

        self.__conn.close()
        self.__conn = None


    # ----------------------------------------------------------------------------------------------------------------

    def __local_listener(self, response):
        if not self.__listener:
            return

        message = response.decode().strip()

        if len(message) == 0:
            return

        self.__listener(message)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "HTTPStreamingClient:{listener:%s}" % self.__listener
