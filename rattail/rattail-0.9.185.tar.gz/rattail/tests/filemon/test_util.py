# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import os
import shutil
import tempfile

from six.moves import queue
from unittest import TestCase

from rattail.config import make_config
from rattail.filemon import util
from rattail.filemon.config import Profile


class TestQueueExisting(TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.config = make_config([])
        self.config.set(u'rattail.filemon', u'monitor', u'foo')
        self.config.set('rattail.filemon', 'foo.dirs', self.tempdir)
        self.config.set(u'rattail.filemon', u'foo.actions', u'noop')
        self.config.set(u'rattail.filemon', u'foo.action.noop.func', u'rattail.filemon.actions:noop')
        self.profile = Profile(self.config, u'foo')
        self.profile.queue = queue.Queue()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def write_file(self, fname, content):
        path = os.path.join(self.tempdir, fname)
        with open(path, 'wt') as f:
            f.write(content)
        return path

    def test_nothing_queued_if_no_files_exist(self):
        util.queue_existing(self.profile, self.tempdir)
        self.assertTrue(self.profile.queue.empty())

    def test_normal_files_are_queued_but_not_folders(self):
        self.write_file('file', '')
        os.makedirs(os.path.join(self.tempdir, 'folder'))
        util.queue_existing(self.profile, self.tempdir)
        self.assertEqual(self.profile.queue.qsize(), 1)
        self.assertEqual(self.profile.queue.get_nowait(), os.path.join(self.tempdir, 'file'))
        self.assertTrue(self.profile.queue.empty())

    def test_if_profile_watches_locks_then_normal_files_are_queued_but_not_lock_files(self):
        self.profile.watch_locks = True
        self.write_file('file1.lock', '')
        self.write_file('file2', '')
        util.queue_existing(self.profile, self.tempdir)
        self.assertEqual(self.profile.queue.qsize(), 1)
        self.assertEqual(self.profile.queue.get_nowait(), os.path.join(self.tempdir, 'file2'))
        self.assertTrue(self.profile.queue.empty())
