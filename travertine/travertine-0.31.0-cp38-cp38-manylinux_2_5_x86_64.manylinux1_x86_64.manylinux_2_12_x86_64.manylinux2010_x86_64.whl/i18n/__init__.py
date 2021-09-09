#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Implements the i18n services for travertine.

.. note:: Implementation note.

   While running `extract_messages`; the function `_`:func: below is just the
   identity function.  While actually running code `_` is the bound method
   `gettext.translations.gettext`:meth:.

   We rely on the environment variable `TRAVERTINE_I18N_CLI` to be set to
   distiguish both cases.

See docs/i18n.rst for a more narrative documentation.

"""
import os


def _(msgid):
    return msgid


if not os.environ.get("TRAVERTINE_I18N_CLI", False):
    import contextlib
    import gettext
    from collections import OrderedDict

    import pkg_resources
    from xotl.tools.context import context

    domain = "travertine"
    locale_dir = os.path.dirname(
        pkg_resources.resource_filename(__name__, "locale/travertine.pot")
    )
    gettext.bindtextdomain(domain, locale_dir)

    def _(msgid):
        locale = context[_TRAVERTINE_LOCALE_CTX].get("locale", None)
        if locale:
            d = _t.get(locale, gettext.NullTranslations())
            return d.gettext(msgid)
        else:
            return gettext.dgettext(domain, msgid)

    @contextlib.contextmanager
    def locale(locale: str):
        """Make `_`:func: lookup for translations in the given locale."""
        with context(_TRAVERTINE_LOCALE_CTX) as ctx:
            ctx["locale"] = locale
            yield

    class TranslationsCache:
        def __init__(self, maxsize=5):
            self._cache = LRU(maxsize)

        def get(self, lang, default=None):
            try:
                return self._cache[lang]
            except KeyError:
                pass
            try:
                result = gettext.translation(
                    domain, localedir=locale_dir, languages=[lang]
                )
            except FileNotFoundError:
                return default
            else:
                self._cache[lang] = result
                return result

        def reset(self):
            self._cache.clear()

    class LRU(OrderedDict):
        "Limit size, evicting the least recently looked-up key when full"

        def __init__(self, maxsize=12, /, *args, **kwds):
            self.maxsize = maxsize
            super().__init__(*args, **kwds)

        def __getitem__(self, key):
            value = super().__getitem__(key)
            self.move_to_end(key)
            return value

        def __setitem__(self, key, value):
            if key in self:
                self.move_to_end(key)
            super().__setitem__(key, value)
            if len(self) > self.maxsize:
                oldest = next(iter(self))
                del self[oldest]

    _t = TranslationsCache()
    _TRAVERTINE_LOCALE_CTX = object()
