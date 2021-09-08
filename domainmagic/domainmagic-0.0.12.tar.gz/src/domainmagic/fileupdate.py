# -*- coding: UTF-8 -*-
#   Copyright 2012-2020 Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#

import logging
import threading
import time
import os
import tempfile
import zlib
import zipfile
import tarfile
from io import BytesIO
from domainmagic.filelock import FileLock, FileLockException
from urllib.request import urlopen
from urllib import parse as urlparse


class FileTooSmallException(Exception):
    pass

class FileExtractionException(Exception):
    pass


class FileUpdaterMultiproc(object):
    """
    Make sure this object exist only once per process
    """

    instance = None
    procPID = None

    def __init__(self):
        FileUpdaterMultiproc.check_replace_instance()

    @classmethod
    def check_replace_instance(cls):
        pid = os.getpid()
        logger = logging.getLogger("%s.FileUpdater" % __package__)
        if pid == cls.procPID and cls.instance is not None:
            #logger.debug("Return existing FileUpdater Singleton for process with pid: %u"%pid)
            pass
        else:
            if cls.instance is None:
                logger.debug("Create FileUpdater Singleton for process with pid: %u"%pid)
            elif cls.procPID != pid:
                logger.debug("Replace FileUpdater Singleton(created by process %u) for process with pid: %u"%(cls.procPID, pid))

            cls.instance = FileUpdater()
            cls.procPID = pid


    def __getattr__(self, name):
        """Pass all queries to FileUpdater instance"""
        FileUpdaterMultiproc.check_replace_instance()
        return getattr(FileUpdaterMultiproc.instance, name)

class FileUpdater(object):

    def __init__(self):
        # key: local absolute path
        # value: dict:
        # - update_url
        # - refresh_time
        # - minimum_size
        # - lock (threading.Lock object, created by add_file)
        self.defaults = {
            'refresh_time': 86400,
            'minimum_size': 0,
        }
        self.filedict = {}
        self.logger = logging.getLogger('%s.fileupdater' % __package__)

    def id(self):
        """Small helper function go get id of of actual instance in FileUpdaterMultiproc"""
        return id(self)

    def add_file(self, local_path, update_url, refresh_time=None, minimum_size=None, unpack=False, filepermission=None):
        if local_path not in self.filedict:
            self.filedict[local_path] = {
                'refresh_time': refresh_time or self.defaults['refresh_time'],
                'minimum_size': minimum_size or self.defaults['minimum_size'],
                'unpack': unpack,
                'update_url': update_url,
                'filepermission': filepermission,
            }

            self.update_in_thread(local_path)
        else:
            self.logger.debug("adding file %s -> already registered, not doing anything" % local_path)
    
    def file_modtime(self, local_path):
        """returns the file modification timestamp"""
        statinfo = os.stat(local_path)
        return max(statinfo.st_ctime, statinfo.st_mtime)
    
    
    def file_age(self, local_path):
        """return the file age in seconds"""
        return time.time() - self.file_modtime(local_path)

    
    def is_recent(self, local_path):
        """returns True if the file mod time is within the configured refresh_time"""
        if not os.path.exists(local_path):
            return False

        return self.file_age(local_path) < self.filedict[local_path]['refresh_time']
    
    
    def has_write_permission(self, local_path):
        perm = True
        if os.path.exists(local_path):
            if not os.access(local_path, os.W_OK):
                perm = False
            else:
                uid = os.getuid()
                stats = os.stat(local_path)
                if stats.st_uid != uid:
                    perm = False
        else:
            dirname = os.path.dirname(local_path)
            if not os.path.exists(dirname) or not os.access(dirname, os.W_OK):
                perm = False
        return perm


    def update(self, local_path, force=False):
        # still use update in thread, but apply a timeout
        # so the code can not get stuck
        self.update_in_thread(local_path, force=force, timeout=66.0)


    def _unpack_tar(self, archive_content, archive_name, local_path):
        mode = 'r'
        if archive_name.endswith('.tar.gz') or archive_name.endswith('.tgz'):
            mode = 'r:gz'
        if archive_name.endswith('.tar.bz2'):
            mode = 'r:bz2'
        if archive_name.endswith('.tar.xz'): # python 3 only
            mode = 'r:xz'

        content = None
        payload = BytesIO(archive_content)
        zf = tarfile.open(fileobj=payload, mode=mode)
        filenames = zf.getnames()
        for filename in filenames:
            if os.path.basename(filename) == os.path.basename(local_path):
                f = zf.extractfile(filename)
                content = f.read()
                f.close()
                break
        zf.close()
        return content


    def _unpack_zip(self, archive_content, local_path):
        content = None
        payload = BytesIO(archive_content)
        zf = zipfile.ZipFile(payload)
        filenames = zf.namelist()
        for filename in filenames:
            if os.path.basename(filename) == os.path.basename(local_path):
                content = zf.read(filename)
                break
        zf.close()
        return content


    def try_update_file(self, local_path, force=False):
        # if the file is current, do not update
        if self.is_recent(local_path) and not force:
            self.logger.debug("File %s is current - not updating" % local_path)
            return
        
        if not self.has_write_permission(local_path):
            self.logger.debug("Can't write file %s - not updating" % local_path)
            return

        filelock_timeout = 60
        filedownload_timeout = filelock_timeout/2
        filelock_delay = 0.5    # time to wait before trying a lock again
        filelock_stale = 70.0  # lock file older than this are stale and will be removed
        try:
            self.logger.debug("Updating %s - try to acquire lock" % local_path)
            with FileLock(local_path+".lock", timeout=filelock_timeout, delay=filelock_delay,
                          stale_timeout=filelock_stale):

                self.logger.debug("Updating %s - lock acquire successfully" % local_path)
                # check again in case we were waiting for the lock before and some
                # other thread just updated the file
                if self.is_recent(local_path) and not force:
                    self.logger.debug(
                        "File %s got updated by a different thread - not updating" % local_path)
                    # no need to release lock because (automatic because of the with-context)
                    return

                try:
                    # TODO: we could optimize here, if-modified-since for example
                    update_url = self.filedict[local_path]['update_url']
                    self.logger.debug("open url: %s with timeout: %u" % (update_url, filedownload_timeout))
                    response = urlopen(update_url, timeout=filedownload_timeout)
                    content = response.read()
                    response.close()
                    content_len = len(content)
                    self.logger.debug("%s bytes downloaded from %s" % (content_len, update_url))
                    handle, tmpfilename = tempfile.mkstemp()
                    if len(content) < self.filedict[local_path]['minimum_size']:
                        raise FileTooSmallException(
                            "file size %s downloaded from %s is smaller than configured minimum of %s bytes" %
                            (content_len, update_url, self.filedict[local_path]['minimum_size']))

                    # TODO: add rar etc here
                    # http://stackoverflow.com/questions/3122145/zlib-error-error-3-while-decompressing-incorrect-header-check
                    if self.filedict[local_path]['unpack']:
                        u = urlparse.urlparse(update_url)
                        path = u.path.lower()

                        if path.endswith('.tar') or path.endswith('.tar.gz') or path.endswith('.tgz') \
                                or path.endswith('.tar.bz2') or path.endswith('.tar.xz'):
                            content = self._unpack_tar(content, path, local_path)
                            print(len(content))
                        elif path.endswith('.gz'):
                            content = zlib.decompress(content, zlib.MAX_WBITS | 16)
                        elif path.endswith('.zip'):
                            content = self._unpack_zip(content, local_path)
                        else:
                            self.logger.debug('URL %s does not seem to be a (supported) archive, not unpacking' % update_url)

                    if content is None:
                        raise FileExtractionException(
                            'failed to extract file %s as %s from file downloaded from %s' %
                            (os.path.basename(local_path), local_path, update_url))

                    with os.fdopen(handle, 'wb') as f:
                        f.write(content)

                    # now change file permission
                    filepermission = self.filedict[local_path]['filepermission']
                    if filepermission is not None:
                        self.logger.debug("Set filepermission: %s" % bin(filepermission)[2:])
                        try:
                            os.chmod(tmpfilename, filepermission)
                        except OSError:
                            pass
                    else:
                        self.logger.debug("Default file permission")

                    try:
                        os.rename(tmpfilename, local_path)
                    except OSError:
                        if os.path.exists(tmpfilename):
                            os.remove(tmpfilename)

                except Exception as e:
                    self.logger.exception(e)

        except FileLockException:
            self.logger.debug(
                "File %s currently seems being updated by a different thread/process - not updating" % local_path)
        else:
            self.logger.debug("%s - lock released" % local_path)
    
    
    def update_in_thread(self, local_path, force=False, timeout=None):
        th = threading.Thread(target=self.try_update_file, args=(local_path, force))
        th.daemon = True
        th.start()

        complete = True
        # wait for thread to complete if there's a timeout
        if timeout:
            th.join(timeout)
            try:
                complete = not th.is_alive()
            except AttributeError:
                # deprecated routine
                complete = not th.isAlive()
            if not complete:
                self.logger.error("Could not finish thread update_in_tread process to update %s" % local_path)
        return complete

    def wait_for_file(self, local_path, force_recent=False):
        """make sure file :localpath exists locally.
        if it doesn't exist, it will be downloaded immediately and this call will block
        if it exists and force_recent is false, the call will immediately return
        if force_recent is true the age of the file is checked und the file will be re-downloaded in case it's too old"""
        

        if local_path not in self.filedict:
            raise ValueError(
                "File not configured for auto-updating - please call add_file first!")

        logger = logging.getLogger("domainmagic.fileupdate.wait_for_file")
        if os.path.exists(local_path):
            if self.is_recent(local_path):
                logger.debug("File exists and recent: %s" % local_path)
                return
            else:
                if force_recent:
                    logger.debug("File exists but not recent -> force update: %s" % local_path)
                    self.update(local_path)
                else:
                    logger.debug("File exists but not recent -> thread updater: %s" % local_path)
                    self.update_in_thread(local_path)
        else:
            logger.debug("File does not exits -> force update: %s" % local_path)
            self.update(local_path)


fileupdater = None


def updatefile(local_path, update_url, **outer_kwargs):
    """decorator which automatically downlads/updates required files
    see fileupdate.Fileupdater.add_file() for possible arguments
    """
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            global fileupdater
            if fileupdater is None:
                fileupdater = FileUpdaterMultiproc()

            force_recent = False

            if 'force_recent' in outer_kwargs:
                force_recent = True
                del outer_kwargs['force_recent']

            # add file if not already present
            fileupdater.add_file(local_path, update_url, **outer_kwargs)

            # wait for file
            fileupdater.wait_for_file(local_path, force_recent)
            return f(*args, **kwargs)

        return wrapped_f

    return wrap

