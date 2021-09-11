#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This file is part of psprint.
#
# psprint is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# psprint is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with psprint.  If not, see <https://www.gnu.org/licenses/>.
#
'''
Information- Prepended Print object
'''

from collections.abc import Iterable
from sys import stderr, stdout
from types import GeneratorType
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
from warnings import warn

from .ansi import ANSI
from .errors import BadMark, DeepIterWarning, LongIterWarning
from .mark_types import InfoMark


class PrintSpace():
    """
    Fancy Print class that also prints the type of message

    Args:
        conf: parsed configuration
        name: name of configuration file (to report errors)

    Attributes:
        pref_max: int: maximum length of prefix string
        info_style; dict: pre-configured prefix styles
        info_index: list: keys of `info_style` mapped to int
        print_kwargs: dict : library of kwargs_accepted by print_function
        switches: dict: user-customizations: pad, short, bland, disabled

            pad: bool: prefix is padded to start text at the same level
            short: bool: display short, 1 character- prefix
            bland: bool: do not show ANSI color/styles for prefix/text
            disabled: bool: behave like python default print_function

    """
    def __init__(self, conf: Dict[str, dict] = None, name: str = None) -> None:
        # Standard info styles
        self.switches = {
            'pad': False,
            'short': False,
            'bland': False,
            'iterate': False,
            'disabled': False
        }
        self.print_kwargs = {
            'file': stdout,
            'sep': "\t",
            'end': "\n",
            'flush': False
        }
        self.pref_max = None
        self.info_style: Dict[str, InfoMark] = {}
        self.info_index: List[str] = []
        if conf is not None:
            self.set_opts(conf, name or 'unnamed config file')

    def __repr__(self) -> str:
        """
        Returns:
            Formatted summary of info_style
        """
        outstr = '\nid\tmark\tlong\tshort\ttext\n\n'
        outstr += "\n".join((f'{i}' + '\t' + f'{k}:{v}' for i, k, v in self))
        return outstr

    def __contains__(self, mark: Union[str, int, InfoMark] = None) -> bool:
        """
        is mark defined?
        """
        if mark is None:
            return False
        if isinstance(mark, str):
            return mark in self.info_style.keys()
        if isinstance(mark, int):
            return len(self.info_index) > mark
        return mark in self.info_style.values()

    def __getitem__(self, mark: Union[int, str]) -> InfoMark:
        """
        Returns:
            Infomark corresponding to mark
        """
        try:
            # check if mark can be converted to int index
            mark = int(mark)
        except ValueError:
            if isinstance(mark, str):
                return self.info_style.get(mark, self.info_style['cont'])
        except Exception:
            raise KeyError(mark)
        if 0 <= mark < len(self.info_index):
            return self.info_style[self.info_index[mark]]
        return self.info_style[self.info_index[0]]

    def __iter__(self) -> Generator[Tuple[int, str, InfoMark], None, None]:
        for index_int, mark in enumerate(self.info_index):
            yield index_int, mark, self.info_style[mark]
        return

    def __eq__(self, value: 'PrintSpace') -> bool:
        """
        Equate
        """
        if any(
                getattr(self, child) != getattr(value, child)
                for child in ('pref_max', 'info_style', 'info_index',
                              'print_kwargs', 'switches')):
            return False
        return True

    def set_opts(self, conf: Dict[str, dict], name: str) -> None:
        """
        configuration from rcfile

        Args:
            conf: parsed configuration
            name: name of configuration file (to report errors)

        Raises:
            BadMark

        """
        if not conf:
            return
        info_index: Optional[Dict[str, str]] = None
        for mark, settings in conf.items():
            if mark == "FLAGS":
                # switches / flags
                self.pref_max = settings.get("pref_max", None)

                # update psprint switches
                self.switches.update(
                    dict(
                        filter(lambda x: x[0] in self.switches,
                               settings.items())))

                # update __builtin__,print kwargs
                self.print_kwargs.update(
                    dict(filter(lambda x: x[0] in self.print_kwargs,
                                settings)))

                # standard output file
                fname = settings.get("file", None)  # Discouraged
                if fname is not None:  # pragma: no cover
                    self.print_kwargs['file'] = open(fname, "a")

            elif mark == 'order':
                info_index = settings
            else:
                # New mark definition
                try:
                    self.edit_style(mark=mark, **settings)
                except (ValueError, TypeError):  # pragma: no cover
                    raise BadMark(str(mark), name) from None
        if info_index is not None:
            self.info_index = list(
                filter(lambda x: x in self.info_style, info_index))

    def edit_style(self,
                   pref: str,
                   index_int: int = None,
                   mark: str = None,
                   **kwargs) -> str:
        """
        Edit loaded style

        Args:
            pref: str: prefix string long [length < 10 characters]
            index_int: Index number that will call this InfoMark
            mark: Mark string that will call this ``InfoMark``
            **kwargs:
                * pref_s: str: prefix string short [1 character]
                * code:

                    * color: {[0-15],[[l]krgybmcw],[[light] <color_name>]}
                    * gloss: {[0-3],[rcdb],{reset,normal,dim,bright}}

                * for-

                    * pref_color: color of of prefix
                    * pref_gloss: gloss of prefix
                    * pref_bgcol: background color of prefix
                    * text_color: color of of text
                    * text_gloss: gloss of text
                    * text_bgcol: background color of text

        Returns
            Summary of new (updated) ``PrintSpace``

        """
        # correct pref
        if mark is None:
            mark = pref[:4]
        kwargs['pref'] = pref
        if index_int is None or \
           not 0 <= index_int <= len(self.info_index):
            self.info_index.append(mark)
        else:
            self.info_index.insert(index_int, mark)
        self.info_style[mark] = InfoMark(pref_max=self.pref_max, **kwargs)
        return str(self)

    def remove_style(self, mark: Union[str, int, InfoMark]) -> str:
        """
        Args:
            mark: is popped out of defined styles
            index_int: is used to locate index_str if it is not provided

        Returns
            Summary of new (updated) ``PrintSpace``

        """
        _idx = None
        _mark = None
        if mark not in self:
            raise KeyError(mark)
        if isinstance(mark, int):
            _idx = mark
            _mark = self.info_index[mark]
        elif isinstance(mark, str):
            _idx = self.info_index.index(mark)
            _mark = mark
        elif isinstance(mark, InfoMark):
            for idx, t_mark, info_mark in self:
                if info_mark == mark:
                    _idx = idx
                    _mark = t_mark
                    break
        if _idx is None or _mark is None:
            # This should never happen
            raise KeyError(mark)  # pragma: no cover
        del self.info_style[_mark]
        del self.info_index[_idx]
        return repr(self)

    def _which_mark(self,
                    mark: Union[str, int, InfoMark] = None,
                    **kwargs) -> InfoMark:
        """
        Define a mark based on arguments supplied

            * may be a pre-defined mark OR
            * mark defined on the fly

        Args:
            mark: mark that identifies a defined prefix
            **kwargs:
                * pref: str: prefix string long [length < 10 characters]
                * pref_s: str: prefix string short [1 character]
                * code:

                    * color: {[0-15],[[l]krgybmcw],[[light] <color_name>]}
                    * gloss: {[0-3],[rcdb],{reset,normal,dim,bright}}

                * for-

                    * pref_color: color of of prefix
                    * pref_gloss: gloss of prefix
                    * pref_bgcol: background color of prefix
                    * text_color: color of of text
                    * text_gloss: gloss of text
                    * text_bgcol: background color of text

        """
        base_mark: InfoMark = self.info_style['cont']
        if mark is not None:
            # mark was supplied
            if isinstance(mark, InfoMark):
                # ready-made mark was served
                base_mark = mark
            elif isinstance(mark, (str, int)):
                # mark supplied as index int
                base_mark = self[mark]
            else:
                raise BadMark(mark=str(mark), config="**kwargs")
        if any(arg in kwargs for arg in [
                'pref',
                'pref_s',
                'pref_color',
                'pref_gloss',
                'pref_bgcol',
                'text_color',
                'text_gloss',
                'text_bgcol',
        ]):
            return InfoMark(parent=base_mark, pref_max=self.pref_max, **kwargs)
        return base_mark

    def _iter_print(self,
                    args: Any,
                    mark: Union[str, int, InfoMark] = None,
                    **kwargs):
        # sub-section head
        arg_type = type(args)
        sub_head = {
            list: 'list:',
            dict: 'dict:',
            tuple: 'tuple:',
            GeneratorType: 'generator:'
        }.get(arg_type, str(arg_type))
        self.psprint(sub_head, mark=mark, **kwargs)

        # Check if args can be easily converted to a dict
        if isinstance(args, GeneratorType):
            args = {idx: val for idx, val in enumerate(args)}
        else:
            try:
                # generator consumes an argument here
                args = dict(args)
            except (TypeError, ValueError):
                # create dictionary of args
                args = {idx: val for idx, val in enumerate(args)}

        # Alter kwargs
        if 'pref' in kwargs:
            del kwargs['pref']
        if 'end' in kwargs:
            del kwargs['end']
        kwargs['indent'] = kwargs.get('indent', 0) + 1
        if kwargs['indent'] > 10:
            self.psprint('...deep stack...', mark='warn', **kwargs)
            warn('...deep stack...', category=DeepIterWarning)
            return

        _num_elements = 0
        for key, value in args.items():
            _num_elements += 1
            if _num_elements > 100:
                self.psprint('...long stack...',
                             mark='warn',
                             **kwargs,
                             file=stderr)
                warn('...long stack...', category=LongIterWarning)
                return
            if isinstance(value, Iterable) and not isinstance(value, str):
                self.psprint(f'{key}:', mark='list', end='', **kwargs)
                self.psprint(value, **kwargs)
            else:
                self.psprint(f'{key}: {value}',
                             mark='list',
                             **kwargs,
                             file=stderr)

    def psfmt(self,
              *args,
              mark: Union[str, int, InfoMark] = None,
              fmt_sep: str = None,
              **kwargs) -> Union[List[str], str]:
        """
        Prefix String represenattion.

        Args:
            *args: passed to print_function for printing
            mark: pre-configured `InfoMark` defaults:

                * cont or 0 or anything else: nothing
                * info or 1: [INFO]
                * act  or 2: [ACTION]
                * list or 3: [LIST]
                * warn or 4: [WARNING]
                * error:or 5: [ERROR]
                * bug:  or 6 [DEBUG]
                * `Other marks defined in .psprintrc`

            fmt_sep: If not ``None``, return `*args` joined by separator.

            **kwargs:
                * pref: str: prefix string long [length < 10 characters]
                * pref_s: str: prefix string short [1 character]
                * code:

                    * color: {[0-15],[[l]krgybmcw],[[light] <color_name>]}
                    * gloss: {[0-3],[rcdb],{reset,normal,dim,bright}}

                * for-

                    * pref_color: color of of prefix
                    * pref_gloss: gloss of prefix
                    * pref_bgcol: background color of prefix
                    * text_color: color of of text
                    * text_gloss: gloss of text
                    * text_bgcol: background color of text

                * pad: bool: prefix is padded to start text at the same level
                * short: bool: display short, 1 character- prefix
                * bland: bool: do not show ANSI color/styles for prefix/text
                * disabled: bool: behave like python default print_function
                * indent: indent level of print statement (1 indent =2 spaces)

        Raises:

            BadMark: mark couldn't be interpreted

        Returns:

            * PSPRINT-like represented args. When `these` args is printed
              using standard print, PSPRINT-like output appears.
            * If a fmt_sep is provided,
              it is used to join args and return a string

        """
        switches = {
            key: {
                **self.switches,
                **kwargs
            }[key]
            for key in self.switches
        }

        # typecast to list[str]
        args_l = list(str(arg) for arg in args)
        if switches['disabled'] or not args_l:
            if fmt_sep is not None:
                return fmt_sep.join(args_l)
            return args_l

        mark = self._which_mark(mark=mark, **kwargs)

        # add indentation
        args_l[0] = '  ' * max(int(kwargs.get('indent', 0)), 0) + args_l[0]

        # add prefix to *args[0]
        if not switches.get('bland'):  # pragma: no cover
            args_l[0] = str(mark.text) + str(args_l[0])
            args_l[-1] = str(args_l[-1]) + ANSI.RESET_ALL
        args_l[0] = mark.pref.to_str(**switches) + str(args_l[0])
        if fmt_sep is not None:
            return fmt_sep.join(args_l)
        return args_l

    def psprint(self,
                *args,
                mark: Union[str, int, InfoMark] = None,
                **kwargs) -> None:
        """
        Prefix String PRINT

        Args:
            *args: passed to print_function for printing
            mark: pre-configured `InfoMark` defaults:

                * cont or 0 or anything else: nothing
                * info or 1: [INFO]
                * act  or 2: [ACTION]
                * list or 3: [LIST]
                * warn or 4: [WARNING]
                * error:or 5: [ERROR]
                * bug:  or 6 [DEBUG]
                * `Other marks defined in .psprintrc`

            **kwargs:
                * pref: str: prefix string long [length < ``pref_max``]
                * pref_s: str: prefix string short [1 character]
                * code:

                    * color: {[0-15],[[l]krgybmcw],[[light] <color_name>]}
                    * gloss: {[0-3],[rcdb],{reset,normal,dim,bright}}

                * for-

                    * pref_color: color of of prefix
                    * pref_gloss: gloss of prefix
                    * pref_bgcol: background color of prefix
                    * text_color: color of of text
                    * text_gloss: gloss of text
                    * text_bgcol: background color of text

                * pad: bool: prefix is padded to start text at the same level
                * short: bool: display short, 1 character- prefix
                * bland: bool: do not show ANSI color/styles for prefix/text
                * disabled: bool: behave like python default print_function
                * indent: int: indent level of print statement (1 indent =2 spaces)
                * iterate: int: Resolve recursively if

                  - only 1 ``*args`` is supplied,
                  - it is iterable
                  - it is not ``str``

                * file: IO: passed to print function
                * sep: str: passed to print function
                * end: str: passed to print function
                * flush: bool: passed to print function

        Raises:
            BadMark: mark couldn't be interpreted

        """
        # Extract print-kwargs
        print_kwargs = {
            key: {
                **self.print_kwargs,
                **kwargs
            }[key]
            for key in self.print_kwargs
        }

        if len(args) == 1:
            if all(condition for condition in (
                    kwargs.get('iterate', self.switches['iterate']),
                    isinstance(args[0], Iterable),
                    not isinstance(args[0], str))):
                self._iter_print(args[0], mark=mark, **kwargs)
                return

        print(*self.psfmt(*args, mark=mark, **kwargs), **print_kwargs)
