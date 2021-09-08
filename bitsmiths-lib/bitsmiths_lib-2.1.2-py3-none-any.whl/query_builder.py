# **************************************************************************** #
#                           This file is part of:                              #
#                                BITSMITHS                                     #
#                           https://bitsmiths.co.za                            #
# **************************************************************************** #
#  Copyright (C) 2015 - 2021 Bitsmiths (Pty) Ltd.  All rights reserved.        #
#   * https://bitbucket.org/bitsmiths_za/bitsmiths                             #
#                                                                              #
#  Permission is hereby granted, free of charge, to any person obtaining a     #
#  copy of this software and associated documentation files (the "Software"),  #
#  to deal in the Software without restriction, including without limitation   #
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
#  and/or sell copies of the Software, and to permit persons to whom the       #
#  Software is furnished to do so, subject to the following conditions:        #
#                                                                              #
#  The above copyright notice and this permission notice shall be included in  #
#  all copies or substantial portions of the Software.                         #
#                                                                              #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
#  DEALINGS IN THE SOFTWARE.                                                   #
# **************************************************************************** #

import datetime


def clean_str_crit(inp: str, max_len: int = 2018) -> str:
    """
    Cleans an input string ensuring it does not contain any weird characters.

    :param inp: The input string clean.
    :param max_len: The maximum possible length of the input string.
    :return: The cleaned string.
    """
    if not inp:
        return ''

    if len(inp) > 2048:
        raise Exception("Input string to large [length:%d > %d]" % (len(inp), max_len))

    return inp.replace('%', ' ')\
              .replace('\n', ' ')\
              .replace('\r', ' ')\
              .replace('\f', ' ')\
              .replace("'", "''")


def pattern_prep(pat: str, negative: bool = False, always_like: bool = False) -> tuple:
    """
    Preps a pattern search string.

    :param pat: The pattern to search for.
    :param negative: If true inverts the pattern search.
    :param always_like: If true, always use ilike
    :return: (pattern, cmpop) ... the final patterm and comp operator.
    """
    if always_like or pat.count('*') > 0 or pat.count('%') > 0:
        pat   = pat.replace('*', '%')
        cmpop = ' NOT ILIKE ' if negative else ' ILIKE '
    else:
        cmpop = '!=' if negative else '='

    return pat, cmpop


def make_pattern(pat: str, pre: bool, post: bool) -> str:
    """
    Preps a pattern to string to have % characters around it, strips *.

    :param pat: The pattern work with.
    :param pre: (bool) Request % in front of the pattern.
    :param post: (bool) Request % at the end of the pattren.
    :return: The result pattern string.
    """
    pat = pat.replace('*', '%')
    pat = pat.strip('%')

    if pre:
        if len(pat) == 0:
            pat = '%%'
        elif pat[0] != '%':
            pat = '%%%s' % pat

    if post and pat != '%':
        pat += '%'

    return pat


def dyn_crit(pat: str, tbl: str, col: str, negative: bool = False, always_like: bool = False) -> str:
    """
    Adds dynamic criteria if pattern is not empty.

    :param pat: The pattern to search for.
    :param tbl: The table identifier.
    :param col: The column identifier.
    :param negative: If true, inverts the check, ie not equals
    :return: The dynamic string.
    """
    if type(pat) not in (str, datetime.date, datetime.datetime):
        return " and %s.%s=%s" % (tbl, col, str(pat))

    if not pat:
        return ''

    srch, oper = pattern_prep(str(pat), negative, always_like)

    if not srch or not oper:
        return ''

    return " and %s.%s%s'%s'" % (tbl, col, oper, srch)


def dyn_list(in_list: list, tbl: str, col: str, join_str: str = None, join_wrap: str = None, negative: bool = False) -> str:
    """
    Adds dynamic string critiera to a string.

    :param in_list: The list to search on.
    :param tbl: The table identifier.
    :param col: The column identifier.
    :param join_str: The join string.
    :param join_wrap: The join wrapper.
    :param negative: If true does the inverted searhc, != or not in.
    :return: The dynamic list critiera.
    """
    if not in_list:
        return ''

    jlist = []

    if not join_str:
        if type(in_list[0]) in (str, datetime.date, datetime.datetime):
            join_str  = "','"
            join_wrap = "'"
        else:
            join_str  = ","
            join_wrap = ""


    for x in in_list:
        jlist.append(clean_str_crit(str(x)))

    oper = 'not in' if negative else 'in'

    return " and %s.%s %s (%s%s%s)" % (tbl, col, oper, join_wrap, join_str.join(jlist), join_wrap)
