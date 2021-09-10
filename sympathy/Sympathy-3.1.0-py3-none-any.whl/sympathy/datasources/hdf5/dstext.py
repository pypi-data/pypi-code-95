# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""Text Data source module."""
import numpy as np

from . import dsgroup


class Hdf5Text(dsgroup.Hdf5Group):
    """Abstraction of an HDF5-text."""
    def __init__(self, factory, **kwargs):
        super().__init__(
            factory, **kwargs)

    def read(self):
        """Return stored text, or '' if nothing is stored."""
        try:
            return self.group['text'][...].tolist()[0].decode('utf8')
        except KeyError:
            return ''

    def write(self, text):
        """
        Stores text in the hdf5 file, at path,
        with data from the given text
        """
        self.group.create_dataset('text', data=np.array([text.encode('utf8')]))

    def transferable(self, other):
        return False

    def transfer(self, name, other, other_name):
        return self.group.create_dataset('text', other.read('text'))

    def write_link(self, name, other, other_name):
        return False
