#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# mteo-util.git:/src/mteo_util/socket.py
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

import socket

from . import tlv

## {{{ class TcpSocket

class TcpSocket:

  # Instance of socket
  _socket = None

  # Underlying file descriptor
  _fd = None

  ## {{{ TcpSocket.__init__()
  def __init__(self, sock=None):
    if sock:
      tlv.assert_type(sock, 'socket', arg='sock')

    if sock is None:
      self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
      self._socket = sock

    self._fd = self._socket.fileno()
  ## }}}

  ## {{{ TcpSocket.fileobj()
  def fileobj(self):
    return self._socket
  ## }}}

  ## {{{ TcpSocket.fileno()
  def fileno(self):
    return self._fd
  ## }}}

  ## {{{ TcpSocket.blocking()
  def blocking(self, block=True):
    tlv.assert_type(block, 'bool', arg='block')

    self._socket.setblocking(block)
  ## }}}

  ## {{{ TcpSocket.bind()
  def bind(self, address, port, reuse_addr=False):
    tlv.assert_type(address, 'str', arg='address')
    tlv.assert_type(port, 'int', arg='port')
    tlv.assert_type(reuse_addr, 'bool', arg='reuse_addr')

    if reuse_addr:
      self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    self._socket.bind((address, port))
  ## }}}

  ## {{{ TcpSocket.listen()
  def listen(self, backlog=10):
    tlv.assert_type(backlog, 'int', arg='backlog')

    self._socket.listen(backlog)
  ## }}}

  ## {{{ TcpSocket.accept()
  def accept(self):
    return self._socket.accept()
  ## }}}

  ## {{{ TcpSocket.connect()
  def connect(self, address, port):
    tlv.assert_type(address, 'str', arg='address')
    tlv.assert_type(port, 'int', arg='port')

    return self._socket.connect((address, port))
  ## }}}

  ## {{{ TcpSocket.recv()
  def recv(self, size, flags=0):
    tlv.assert_type(size, 'int', arg='size')
    tlv.assert_type(flags, 'int', arg='flags')

    if flags != 0:
      return self._socket.recv(size)
    else:
      return self._socket.recv(size, flags)
  ## }}}

  ## {{{ TcpSocket.shutdown()
  def shutdown(self, how=socket.SHUT_RDWR):
    self._socket.shutdown(how)
  ## }}}

  ## {{{ TcpSocket.close()
  def close(self):
    self._socket.close()
    self._socket = None
    self._fd = None
  ## }}}

## class TcpSocket }}}

##
# vim: ts=2 sw=2 tw=100 et fdm=marker :
##
