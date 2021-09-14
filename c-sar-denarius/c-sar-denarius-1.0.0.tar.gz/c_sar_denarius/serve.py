#
# Copyright (c) 2021 Genome Research Ltd
#
# Author: CASM/Cancer IT <cgphelp@sanger.ac.uk>
#
# This file is part of c-sar-denarius.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# 1. The usage of a range of years within a copyright statement contained within
# this distribution should be interpreted as being equivalent to a list of years
# including the first and last year specified and all consecutive years between
# them. For example, a copyright statement that reads ‘Copyright (c) 2005, 2007-
# 2009, 2011-2012’ should be interpreted as being identical to a statement that
# reads ‘Copyright (c) 2005, 2007, 2008, 2009, 2011, 2012’ and a copyright
# statement that reads ‘Copyright (c) 2005-2012’ should be interpreted as being
# identical to a statement that reads ‘Copyright (c) 2005, 2006, 2007, 2008,
# 2009, 2010, 2011, 2012’.
import logging
import os
import sys
from stat import S_IROTH
from stat import S_IWOTH
from stat import S_IXOTH

import yaml
from sauth import serve_http
from sauth import SimpleHTTPAuthHandler

from c_sar_denarius.constants import DEFAULT_GRP
from c_sar_denarius.constants import DEFAULT_PW

PERMISSIONS_FLAG: int = S_IROTH | S_IWOTH | S_IXOTH


def check_permissions(filename):
    # Check Unix permissions
    if os.name == "posix" and os.stat(filename).st_mode & PERMISSIONS_FLAG:
        logging.critical(f"'{filename}' is unprotected (run 'chmod o-rwx {filename}')!")
        sys.exit(1)


def load_auth(filename):
    check_permissions(filename)
    (group, pw) = (None, None)
    with open(filename, "r") as fo:
        y = yaml.safe_load(fo)
        group = y["group"]
        pw = y["pw"]
    return (group, pw)


def site(target, authfile, port, https):
    start_dir = os.path.join(target, "site")
    if authfile:
        (group, pw) = load_auth(authfile)
    else:
        logging.warning("Site running with, default user/pw values for authentication")
        (group, pw) = (DEFAULT_GRP, DEFAULT_PW)
    SimpleHTTPAuthHandler.username = group  # as that's how we restrict
    SimpleHTTPAuthHandler.password = pw
    serve_http(
        ip="0.0.0.0",
        port=port,
        https=https,
        start_dir=start_dir,
        handler_class=SimpleHTTPAuthHandler,
    )
