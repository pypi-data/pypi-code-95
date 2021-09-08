#####################################################################
# Copyright (c) The Caleydo Team, http://caleydo.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#####################################################################


import phovea_server.security
import logging
import hashlib
import uuid
import sqlite3

__author__ = 'Samuel Gratzl'
_log = logging.getLogger(__name__)


def hash_password(password, salt):
  return hashlib.sha512((password + salt).encode('utf-8')).hexdigest()


def ensure_dir(path):
  import errno
  import os

  path = os.path.dirname(path)
  try:
    os.makedirs(path)
  except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise


class FakeUser(phovea_server.security.User):
  def __init__(self, id, password, salt, roles):
    super(FakeUser, self).__init__(id)
    self.name = id
    self.password = password
    self.salt = salt
    self.roles = roles

  @property
  def is_authenticated(self):
    return True

  @property
  def is_active(self):
    return True

  def is_password(self, given):
    given_h = hash_password(given, self.salt)
    return given_h == self.password


class FakeStore(object):
  def __init__(self):
    from phovea_server.config import view as configview
    self._config = configview('phovea_security_store_generated')
    ensure_dir(self._config.file)
    self._db = sqlite3.connect(self._config.file)
    self._db.execute("""CREATE TABLE IF NOT EXISTS user (username TEXT, password TEXT, salt TEXT, roles TEXT, creation_date TEXT, last_login_date TEXT)""")
    self._db.commit()

    self._users = list(self._load_users())

  def _load_users(self):
    for row in self._db.execute("""SELECT username, password, salt, roles FROM user"""):
      yield FakeUser(row[0], row[1], row[2], row[3].split(';'))

  def _flag_logged_in(self, user):
    self._db.execute("""UPDATE user SET last_login_date = date('now') WHERE username = ?""", (user.name,))
    self._db.commit()

  def _persist_user(self, user):
    self._db.execute("""
INSERT INTO user(username, password, salt, roles, creation_date, last_login_date) VALUES(?,?,?,?,date('now'),date('now'))
""", (user.name, user.password, user.salt, ';'.join(user.roles)))
    self._db.commit()

  def logout(self, user):
    pass

  def load(self, id):
    return next((u for u in self._users if u.id == id), None)

  def load_from_key(self, api_key):
    try:
      api_key = api_key.decode()  # Convert to string if bytes-like
    except (UnicodeDecodeError, AttributeError):
      pass

    parts = api_key.split(':')
    if len(parts) != 2:
      return None
    return self.login(parts[0], dict(password=parts[1]))

  def _find_user(self, username, password):
    return next((u for u in self._users if u.id == username and u.is_password(password)), None)

  def login(self, username, extra_fields=None):
    if extra_fields is None:
      extra_fields = {}
    password = extra_fields['password']

    user = next((u for u in self._users if u.id == username), None)
    if user:
      # existing user
      if user.is_password(password):
        self._flag_logged_in(user)
        return user
      else:
        return None

    # create a new one on the fly given the new values
    user = self._add_user(username, password)
    return user

  def _add_user(self, username, password):
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512((password + salt).encode('utf-8')).hexdigest()
    user = FakeUser(username, hashed_password, salt, [username])
    self._users.append(user)
    _log.info('registering new user: ' + username)
    self._persist_user(user)
    return user


def create():
  return FakeStore()
