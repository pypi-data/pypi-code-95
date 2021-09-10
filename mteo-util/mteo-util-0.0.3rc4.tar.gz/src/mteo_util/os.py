#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# mteo-util.git:/src/mteo_util/os.py
##

## {{{ ---- [ Header ] -----------------------------------------------------------------------------

##
# Copyright (c) 2021 Francis M <francism@destinatech.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2.0 as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to:
#
#   Free Software Foundation
#   51 Franklin Street, Fifth Floor
#   Boston, MA 02110
#   USA
##

## }}} ---- [ Header ] -----------------------------------------------------------------------------

import pwd
import grp

## {{{ class OsUser

class OsUser:

  # Username
  name = None

  # User UID/GID
  uid = None
  gid = None

  # Password
  passwd = None

  # GECOS (real name, comment/description etc.)
  gecos = None

  # Home directory
  dir = None

  # Login shell
  shell = None

  ## {{{ OsUser.__init__()
  def __init__(self, **kwargs):
    if len(kwargs) != 1:
      raise ValueError(f"one keyword required, {len(kwargs)} given")

    if 'name' in kwargs:
      user = pwd.getpwnam(kwargs['name'])
    elif 'uid' in kwargs:
      user = pwd.getpwuid(kwargs['uid'])
    else:
      raise ValueError(f"invalid keyword argument '{key}'")

    self.name = user.pw_name
    self.uid = user.pw_uid
    self.gid = user.pw_gid
    self.passwd = user.pw_passwd
    self.gecos = user.pw_gecos
    self.dir = user.pw_dir
    self.shell = user.pw_shell
  ## }}}

## class OsUser }}}

## {{{ class OsGroup

class OsGroup:

  # Group name
  name = None

  # Password
  passwd = None

  # GID
  gid = None

  # Group members
  members = None

  ## {{{ OsGroup.__init__()
  def __init__(self, **kwargs):
    if len(kwargs) != 1:
      raise ValueError(f"one keyword required, {len(kwargs)} given")

    if 'name' in kwargs:
      group = grp.getgrnam(kwargs['name'])
    elif 'gid' in kwargs:
      group = grp.getgrgid(kwargs['gid'])
    else:
      raise ValueError(f"invalid keyword argument '{key}'")

    self.name = group.gr_name
    self.passwd = group.gr_passwd
    self.gid = group.gr_gid
    self.members = group.gr_mem
  ## }}}

## class OsGroup }}}

##
# vim: ts=2 sw=2 tw=100 et fdm=marker :
##
