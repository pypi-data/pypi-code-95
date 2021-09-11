#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Copyright © 2020-2021 Pradyumna Paranjape
#
# This file is part of pspvis.
#
# pspvis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pspvis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details. #
# You should have received a copy of the GNU Lesser General Public License
# along with pspvis. If not, see <https://www.gnu.org/licenses/>.
#
"""
structure classes
"""

from types import GeneratorType
from typing import Dict, List, Mapping, Optional, Tuple, Union

from pspvis.errors import VisKeyError


class DataAnnot():
    """
    Data Annotation structure class

    Attributes:
        rows: Names of rows
        schemes: collection schemes, each scheme groups rows in a way

    Args:
        annot: information annot file

    """
    def __init__(self, annot: Mapping = None):
        self._rows: Dict[str, str] = {}
        self._cols: Dict[str, str] = {}
        self.schemes: Dict[str, Dict[Union[str, int], List[str]]] = {
            'None': {}
        }
        if annot:
            self.fill_data(annot)

    @property
    def cols(self):
        return self._cols

    @cols.setter
    def cols(self, val):
        self._cols = val
        self.schemes['None'].update({acc: [acc] for acc in self._cols})

    @cols.deleter
    def cols(self):
        self._cols = {}

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, val):
        self._rows = val
        self.schemes['None'].update({acc: [acc] for acc in self._rows})

    @rows.deleter
    def rows(self):
        self._rows = {}

    def __bool__(self):
        """
        if DataAnnot
        """
        if self._rows or self._cols:
            return True
        return False

    def update(self, template: 'DataAnnot'):
        """
        Update from template
        Args:
            template: object to immitate
        """
        # Update scope
        self.rows.update(template.rows)
        self.cols.update(template.cols)

        # update groups
        for name, data in template.schemes.items():
            if name not in self.schemes:
                self.schemes[name] = data
            else:
                # the following line will **replace** accession list,
                # which is the intended behaviour
                self.schemes[name].update(data)

    def fill_data(self, annot: Mapping):
        """
        Parse annot and create structure
        """
        config_rows = annot.get('ROWS', {})
        config_cols = annot.get('COLUMNS', {})
        if isinstance(config_rows, list):
            config_rows = {acc: '' for acc in config_rows}
        if isinstance(config_cols, list):
            config_cols = {acc: '' for acc in config_cols}
        self.rows.update(config_rows)
        self.cols.update(config_cols)
        for name, data in annot.get('SCHEMES', {}).items():
            if name not in self.schemes:
                assert isinstance(name, str)
                self.schemes[name] = {}
            if isinstance(data, GeneratorType):
                scheme_dict = {idx: grp for idx, grp in enumerate(data)}
            else:
                try:
                    # can we easily convert data into a dict?
                    scheme_dict = dict(data)
                except ValueError:
                    scheme_dict = {idx: grp for idx, grp in enumerate(data)}
            for grp, acc_list in scheme_dict.items():
                assert isinstance(grp, (int, str))
                assert isinstance(acc_list, list)
            self.schemes[name].update(scheme_dict)  # type: ignore

    def __repr__(self) -> str:
        """
        Represent data
        """
        output = ['Scope:']
        output.extend(('  ' + acc for acc in self.rows))
        output.append('Scheme')
        for name, scheme in self.schemes.items():
            output.append('  ' + name)
            for grp, acc_l in scheme.items():
                output.append('  ' * 2 + str(grp))
                for sr_no, acc in enumerate(acc_l):
                    output.append('  ' * 3 + str(sr_no) + ': ' + acc)
        return '\n'.join(output)

    def __getitem__(
        self, args: Union[str, Tuple[str,
                                     Union[int,
                                           str]]]) -> List[Union[str, int]]:
        """
        Args:
            args: if args is single argument
                    accession is assumed, annotation is returned

                else, args is to be a tuple of following args
                    scheme: scheme in use
                    group_name: return all elements of group
                    accession [row/col]: return all groups that contain the row
        """
        if not isinstance(args, (list, tuple)):
            if args in self.rows:
                return [self.rows[args]]
            if args in self.cols:
                return [self.cols[args]]
            raise VisKeyError(f'Accession key {args} is unknown]')
        scheme, key = args
        if scheme not in self.schemes:
            raise VisKeyError(f'Bad index {scheme}')
        group_scheme = self.schemes[scheme]
        if key in (*self.rows, *self.cols):
            # key is a known element
            return list(gid for gid, group in group_scheme.items()
                        if key in group)
        if key in group_scheme:
            return group_scheme[key]
        raise VisKeyError(f'Bad index {key}')

    def __contains__(self, key) -> bool:
        """
        Key is a known row or column index
        But NOT scheme or group

            * for scheme, use self.schemes.__contains__
            * for group, use self.schemes[scheme_idx].__contains__
        """
        if key in self.rows:
            return True
        if key in self.cols:
            return True
        return False

    def get(self, args, default=None) -> Optional[List[Union[str, int]]]:
        try:
            return self.__getitem__(args)
        except VisKeyError:
            return default
