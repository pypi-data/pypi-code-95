"""
Created on 21 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

https://www.pythonforbeginners.com/modules-in-python/python-secure-ftp-module
https://github.com/paramiko/paramiko/issues/1369
"""

import pysftp


# --------------------------------------------------------------------------------------------------------------------

class SFTPClient(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, host):
        """
        Constructor
        """
        self.__host = host
        self.__conn = None


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self, username=None, private_key=None, password=None, port=22, private_key_pass=None, ciphers=None,
                cnopts=None, default_path=None):

        # cnopts = pysftp.CnOpts()
        # cnopts.log = True

        self.__conn = pysftp.Connection(self.__host, username=username, private_key=private_key, password=password,
                                        port=port, private_key_pass=private_key_pass, ciphers=ciphers,
                                        cnopts=cnopts, default_path=default_path)


    def close(self):
        if self.__conn:
            self.__conn.close()
            self.__conn = None

    # ----------------------------------------------------------------------------------------------------------------

    def chdir(self, remote_path):
        if not self.__conn:
            raise RuntimeError('no connection')

        self.__conn.chdir(remote_path)


    def cwd(self):
        if not self.__conn:
            raise RuntimeError('no connection')

        return self.__conn.getcwd()


    def exists(self, remote_path):
        if not self.__conn:
            raise RuntimeError('no connection')

        return self.__conn.exists(remote_path)


    def get(self, remote_path, local_path=None, callback=None):
        if not self.__conn:
            raise RuntimeError('no connection')

        self.__conn.get(remote_path, local_path, callback=callback)


    def listdir(self, remote_path='.'):
        if not self.__conn:
            raise RuntimeError('no connection')

        return self.__conn.listdir(remote_path)


    def mkdir(self, remote_path):
        if not self.__conn:
            raise RuntimeError('no connection')

        self.__conn.mkdir(remote_path)


    def put(self, local_path, remote_path=None, callback=None, confirm=True):
        if not self.__conn:
            raise RuntimeError('no connection')

        return self.__conn.put(local_path, remote_path, callback=callback, confirm=confirm)


    def rmdir(self, remote_path):
        if not self.__conn:
            raise RuntimeError('no connection')

        self.__conn.rmdir(remote_path)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        cwd = None if self.__conn is None else self.cwd()

        return "SFTPClient:{host:%s, cwd:%s}" % (self.__host, cwd)
