#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020, 2021 Pradyumna Paranjape
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
test print
'''

import tempfile
import unittest
from pathlib import Path

from psprint import DEFAULT_PRINT, errors, init_print
from psprint.mark_types import InfoMark
from psprint.printer import PrintSpace


class TestPrintSpace(unittest.TestCase):
    """
    Test basic functions
    """
    def setUp(self):
        self.test_print = init_print()

    def test_eq(self):
        self.assertEqual(self.test_print, self.test_print)

    def test_ne(self):
        mod_print = init_print()
        mod_print.edit_style('test', mark='test')
        self.assertNotEqual(self.test_print, mod_print)

    def test_defaults_load(self):
        """
        print all default marks
        """
        print(self.test_print)

    def test_eq_compare_marks(self):
        """
        compare InfoMarks
        """
        self.assertEqual(self.test_print[0], self.test_print[0])

    def test_eq_compare_ansi(self):
        """
        compare text of marks
        """
        self.assertEqual(self.test_print[0].text, self.test_print[0].text)

    def test_ne_compare_marks(self):
        """
        compare InfoMarks
        """
        self.assertNotEqual(self.test_print[0], self.test_print[1])

    def test_ne_compare_ansi(self):
        """
        compare text of marks
        """
        self.assertNotEqual(self.test_print[6].text, self.test_print[1].text)

    def test_disabled(self):
        """
        Disable fancy
        """
        self.test_print.psprint('Disabled', disabled=True)

    def test_default_mark(self):
        """
        Default print
        """
        self.test_print.psprint("Info Mark", mark='info')

    def test_new_mark(self):
        """
        Test kwarg
        """
        configuration = '\n'.join([
            'FLAGS:',
            '  short: No',
            '  pad: Yes',
            '',
            'TEST:',
            '  pref: TEST',
            '  pref_s: t',
            '  pref_color: y',
            '  pref_bgcol: blue',
            '  pref_gloss: 1',
            '  text_color: k',
            '  text_bgcol: 7',
            '  text_gloss: d',
            '',
        ])
        with tempfile.NamedTemporaryFile('wt', delete=False) as config:
            config.write(configuration)
        my_print = init_print(Path(config.name))
        my_print.psprint("Test Text", mark='TEST')
        my_print.psprint("Info Test", mark='info')
        my_print.set_opts({}, '')
        config.close()
        my_print.remove_style('TEST')
        PrintSpace({})

    def test_not_in(self):
        self.assertNotIn('badkey', self.test_print)

    def test_mark_in(self):
        self.assertIn(self.test_print.info_style['info'], self.test_print)
        self.assertIn('info', self.test_print)

    def test_on_the_fly(self):
        """
        Test definition on the fly
        """
        self.test_print.psprint("OTF text",
                                pref="OTF",
                                pref_s="o",
                                text_bgcol='lg',
                                pref_color='r',
                                short=True)

    def test_mod_mark(self):
        """
        Test a modified mark
        """
        self.test_print.psprint("MOD MARK test",
                                mark=2,
                                pref_color="lg",
                                pref=None,
                                pref_s=None)

    def test_edit(self):
        """
        test edit style
        """
        self.test_print.edit_style(pref="my_test", index_int=4)

    def test_int_pref(self):
        """
        int/float as prefix
        """
        self.test_print.psprint("bad prefix", pref=1234)

    def test_pop_style(self):
        """
        test edit style
        """
        self.test_print.remove_style(4)

    def test_remove_style_mark(self):
        """
        test removal by passing InfoMark object
        """
        rem_mark = self.test_print[0]
        print(rem_mark)
        self.test_print.remove_style(rem_mark)

    def test_allow_unknown_mark(self):
        """
        allow an unknown mark (interpret as 0/cont)
        """
        self.test_print.psprint("Test Unknown", mark=88)

    def test_precreated_mark(self):
        mark = InfoMark(pref='prepref')
        self.test_print.psprint("pass mark", mark=mark)

    def test_precreated_inherit(self):
        mark = InfoMark(parent=self.test_print.info_style['info'])
        self.test_print.psprint("pass mark", mark=mark)


class TextErrors(unittest.TestCase):
    def test_warns(self):
        """
        Check that warnings are thrown
        """
        self.assertWarns(errors.PSPrintWarning,
                         DEFAULT_PRINT.psprint,
                         "warn_text",
                         mark=5,
                         pref="SOME LONG TEXT",
                         pref_s="LONG SHORT")

    def test_bad_pref(self):
        """
        trigger a bad prefix
        """
        self.assertRaises((errors.BadPrefix, errors.BadShortPrefix),
                          DEFAULT_PRINT.psprint,
                          "bad prefix",
                          pref=["bad list prefix"])

    def test_bad_col(self):
        """
        trigger a bad color error
        """
        self.assertRaises(errors.BadColor,
                          DEFAULT_PRINT.psprint,
                          "bad color",
                          pref_color=77)
        self.assertRaises(errors.BadBGCol,
                          DEFAULT_PRINT.psprint,
                          "bad color",
                          pref_bgcol=77)
        self.assertRaises(errors.BadGloss,
                          DEFAULT_PRINT.psprint,
                          "bad gloss",
                          pref_gloss=77)

    def test_bad_rm_mark(self):
        """
        test mark removal error
        """
        self.assertRaises(KeyError, DEFAULT_PRINT.remove_style, None)

    def test_bad_mark(self):
        """
        test bad mark creation
        """
        self.assertRaises(errors.BadMark,
                          DEFAULT_PRINT.psprint,
                          "bad mark",
                          mark=[])

    def test_no_file(self):
        """
        custom-supplied file missing
        """
        self.assertRaises(FileNotFoundError, init_print, "bad_file_name")

    def test_nokey(self):
        """
        bad key not in PrintSpace
        """
        self.assertRaises(KeyError, DEFAULT_PRINT.__getitem__, list())


class TestIter(unittest.TestCase):
    @staticmethod
    def test_iter_list():
        DEFAULT_PRINT.psprint([1, [2, 20, 200], 3, 4], mark="info")

    @staticmethod
    def test_iter_gen():
        DEFAULT_PRINT.psprint(
            (k for k in (1, (t for t in (2, 20, 200)), 3, 4)), mark="info")

    @staticmethod
    def test_iter_dict():
        DEFAULT_PRINT.psprint(
            {
                "a": 1,
                "b": 2,
                3: {
                    "int": 3,
                    "bool": bin(3),
                    "hex": hex(3)
                }
            },
            mark="info")

    @staticmethod
    def test_iter_all():
        DEFAULT_PRINT.psprint((k for k in [[], {
            "a": 1,
            "b": [2, "b"],
            3: {
                "int": 3,
                "bool": bin(3),
                "hex": hex(3)
            }
        }, {1, 2, 3, 4}]),
                              mark="info")
