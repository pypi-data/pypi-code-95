#      Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# -*- coding: utf-8 -*-

from crispy_forms.layout import Field
from django.forms.utils import flatatt
from django.forms.widgets import DateTimeInput, TimeInput
from django.utils import translation
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

try:
    import json
except ImportError:
    from django.utils import simplejson as json
try:
    from django.utils.encoding import force_unicode as force_text
except ImportError:  # python3
    from django.utils.encoding import force_text


class InlineCheckboxesImage(Field):
    """
    Layout object for rendering checkboxes inline::

    InlineCheckboxes('field_name')
    """
    template = "layout/checkboxselectmultiple_inline_image.html"
    TEMPLATE_PACK = "bootstrap3"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        return super(InlineCheckboxesImage, self).render(
            form, form_style, context, template_pack=template_pack,
            extra_context={'inline_class': 'inline'}
        )


class InlineRadiosImage(Field):
    """
    Layout object for rendering radiobuttons inline::

        InlineRadios('field_name')
    """
    template = "layout/radioselect_inline_image.html"
    TEMPLATE_PACK = "bootstrap3"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        return super(InlineRadiosImage, self).render(
            form, form_style, context, template_pack=template_pack,
            extra_context={'inline_class': 'inline'}
        )


class InlineRadiosCol(Field):
    """
    Layout object for rendering radiobuttons inline::

    InlineRadios('field_name')
    """
    template = "layout/radioselect_inline.html"
    TEMPLATE_PACK = "bootstrap3"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        return super(InlineRadiosCol, self).render(
            form, form_style, context, template_pack=template_pack,
            extra_context={'inline_class': 'inline col-lg-3 col-md-3 resetColLabel'}
        )


class InlineCheckboxesCol(Field):
    """
    Layout object for rendering radiobuttons inline::

    InlineRadios('field_name')
    """
    template = "layout/checkboxselectmultiple_inline.html"
    TEMPLATE_PACK = "bootstrap3"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        return super(InlineCheckboxesCol, self).render(
            form, form_style, context, template_pack=template_pack,
            extra_context={'inline_class': 'inline col-lg-4 col-md-4 resetColLabel'}
        )


class InlineCheckboxesColAct(Field):
    """
    Layout object for rendering radiobuttons inline::

    InlineRadios('field_name')
    """
    template = "layout/checkboxselectmultiple_inline_act.html"
    TEMPLATE_PACK = "bootstrap3"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        return super(InlineCheckboxesColAct, self).render(
            form, form_style, context, template_pack=template_pack,
            extra_context={'inline_class': 'inline col-lg-4 col-md-4 resetColLabel'}
        )


class DateTimePicker(DateTimeInput):
    class Media:
        js = ['pluginsRequired/bootstrap-datetimepicker/js/bootstrap-datetimepicker.min.js']
        css = {
            'all': ('css/bootstrap.min.css',
                    'pluginsRequired/bootstrap-datetimepicker/css/bootstrap-datetimepicker.min.css',
                    'pluginsRequired/bootstrap-datetimepicker/css/bootstrap-datetimepicker-standalone.css',),
        }

    # http://momentjs.com/docs/#/parsing/string-format/
    # http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    format_map = (
        ('DDD', r'%j'),
        ('DD', r'%d'),
        ('MMMM', r'%B'),
        ('MMM', r'%b'),
        ('MM', r'%m'),
        ('YYYY', r'%Y'),
        ('YY', r'%y'),
        ('HH', r'%H'),
        ('hh', r'%I'),
        ('mm', r'%M'),
        ('ss', r'%S'),
        ('a', r'%p'),
        ('ZZ', r'%z'),
    )

    @classmethod
    def conv_datetime_format_py2js(cls, format):
        for js, py in cls.format_map:
            format = format.replace(py, js)
        return format

    @classmethod
    def conv_datetime_format_js2py(cls, format):
        for js, py in cls.format_map:
            format = format.replace(js, py)
        return format

    html_template = """
    <div%(div_attrs)s>
      <input%(input_attrs)s/>
      <span class="input-group-addon">
        <span%(icon_attrs)s></span>
      </span>
    </div>"""

    js_template = """
    <script>
      $(function(){
        $("#%(picker_id)s:has(input:not([readonly],[disabled]))").datetimepicker(%(options)s);
      });
    </script>"""

    def __init__(self, attrs=None, format=None, options=None, div_attrs=None, icon_attrs=None):
        if not icon_attrs:
            icon_attrs = {'class': 'glyphicon glyphicon-calendar'}
        if not div_attrs:
            div_attrs = {'class': 'input-group date'}
        if format is None and options and options.get('format'):
            format = self.conv_datetime_format_js2py(options.get('format'))
        super(DateTimePicker, self).__init__(attrs, format)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'form-control'
        self.div_attrs = div_attrs and div_attrs.copy() or {}
        self.icon_attrs = icon_attrs and icon_attrs.copy() or {}
        self.picker_id = self.div_attrs.get('id') or None
        if not options:  # datetimepicker will not be initalized when options is False
            self.options = False
        else:
            self.options = options and options.copy() or {}
            if format and not self.options.get('format') and not self.attrs.get('date-format'):
                self.options['format'] = self.conv_datetime_format_py2js(format)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''

        extra_attrs = dict(type=self.input_type, name=name)
        if self.attrs:
            extra_attrs.update(self.attrs)
        input_attrs = self.build_attrs(attrs, extra_attrs=extra_attrs)

        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            input_attrs['value'] = force_text(self.format_value(value))
        input_attrs = {key: conditional_escape(val) for key, val in input_attrs.items()}
        if not self.picker_id:
            self.picker_id = (input_attrs.get('id', '') +
                              '_pickers').replace(' ', '_')
        self.div_attrs['id'] = self.picker_id
        picker_id = conditional_escape(self.picker_id)
        div_attrs = {key: conditional_escape(val) for key, val in self.div_attrs.items()}
        icon_attrs = {key: conditional_escape(val) for key, val in self.icon_attrs.items()}
        html = self.html_template % dict(div_attrs=flatatt(div_attrs),
                                         input_attrs=flatatt(input_attrs),
                                         icon_attrs=flatatt(icon_attrs))
        if self.options:
            js = self.js_template % dict(picker_id=picker_id, options=json.dumps(self.options or {}))
        else:
            js = ''
        return mark_safe(force_text(html + js))


class TimePicker(DateTimeInput):
    class Media:
        js = ['pluginsRequired/bootstrap-datetimepicker/js/bootstrap-datetimepicker.min.js']
        css = {
            'all': ('css/bootstrap.min.css',
                    'pluginsRequired/bootstrap-datetimepicker/css/bootstrap-datetimepicker.min.css',
                    'pluginsRequired/bootstrap-datetimepicker/css/bootstrap-datetimepicker-standalone.css',),
        }

    # http://momentjs.com/docs/#/parsing/string-format/
    # http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    format_map = (
        ('HH', r'%H'),
        ('hh', r'%I'),
        ('mm', r'%M'),
        ('ss', r'%S'),
        ('a', r'%p'),
        ('ZZ', r'%z'),
    )

    @classmethod
    def conv_datetime_format_py2js(cls, format):
        for js, py in cls.format_map:
            format = format.replace(py, js)
        return format

    @classmethod
    def conv_datetime_format_js2py(cls, format):
        for js, py in cls.format_map:
            format = format.replace(js, py)
        return format

    html_template = """
    <div%(div_attrs)s>
      <input%(input_attrs)s/>
      <span class="input-group-addon">
        <span%(icon_attrs)s></span>
      </span>
    </div>"""

    js_template = """
    <script>
      $(function(){
        $("#%(picker_id)s:has(input:not([readonly],[disabled]))").datetimepicker(%(options)s);
      });
    </script>"""

    def __init__(self, attrs=None, format=None, options=None, div_attrs=None, icon_attrs=None):
        if not icon_attrs:
            icon_attrs = {'class': 'glyphicon glyphicon-time'}
        if not div_attrs:
            div_attrs = {'class': 'input-group date'}
        if format is None and options and options.get('format'):
            format = self.conv_datetime_format_js2py(options.get('format'))
        super(TimePicker, self).__init__(attrs, format)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'form-control'
        self.div_attrs = div_attrs and div_attrs.copy() or {}
        self.icon_attrs = icon_attrs and icon_attrs.copy() or {}
        self.picker_id = self.div_attrs.get('id') or None
        if not options:  # datetimepicker will not be initalized when options is False
            self.options = False
        else:
            self.options = options and options.copy() or {}
            if format and not self.options.get('format') and not self.attrs.get('date-format'):
                self.options['format'] = self.conv_datetime_format_py2js(format)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''

        extra_attrs = dict(type=self.input_type, name=name)
        if self.attrs:
            extra_attrs.update(self.attrs)
        input_attrs = self.build_attrs(attrs, extra_attrs=extra_attrs)

        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            input_attrs['value'] = force_text(self.format_value(value))
        input_attrs = {key: conditional_escape(val) for key, val in input_attrs.items()}
        if not self.picker_id:
            self.picker_id = (input_attrs.get('id', '') +
                              '_pickers').replace(' ', '_')
        self.div_attrs['id'] = self.picker_id
        picker_id = conditional_escape(self.picker_id)
        div_attrs = {key: conditional_escape(val) for key, val in self.div_attrs.items()}
        icon_attrs = {key: conditional_escape(val) for key, val in self.icon_attrs.items()}
        html = self.html_template % dict(div_attrs=flatatt(div_attrs),
                                         input_attrs=flatatt(input_attrs),
                                         icon_attrs=flatatt(icon_attrs))
        if self.options:
            js = self.js_template % dict(picker_id=picker_id, options=json.dumps(self.options or {}))
        else:
            js = ''
        return mark_safe(force_text(html + js))


class DateTimePicker2(DateTimeInput):
    class Media:
        js = ['js/jquery-2.2.1.min.js', 'js/moment.min.js',
              'pluginsRequired/bootstrap-datetimepicker/bootstrap-datetimepicker.min.js']

        lang = translation.get_language()
        if lang:
            lang = lang.lower()
            # There is language name that length>2 *or* contains uppercase.
            lang_map = {
                'ar-ma': 'ar-ma',
                'en-au': 'en-au',
                'en-ca': 'en-ca',
                'en-gb': 'en-gb',
                'en-us': 'en-us',
                'fa-ir': 'fa-ir',
                'fr-ca': 'fr-ca',
                'fr': 'fr',
                'fr-ch': 'fr-ch',
                'ms-my': 'ms-my',
                'pt-br': 'bt-BR',
                'rs-latin': 'rs-latin',
                'tzm-la': 'tzm-la',
                'tzm': 'tzm',
                'zh-cn': 'zh-CN',
                'zh-tw': 'zh-TW',
                'zh-hk': 'zh-TW',
            }
            if len(lang) > 2:
                lang = lang_map.get(lang, 'en-us')
            if lang not in ('en', 'en-us'):
                js.append('pluginsRequired/bootstrap-datetimepicker/locale/%s.js' % (lang))
        # js = JsFiles()
        css = {
            'all': ('pluginsRequired/bootstrap-datetimepicker/bootstrap-datetimepicker.min.css',
                    'css/font-awesome.min.css',),
        }

    # http://momentjs.com/docs/#/parsing/string-format/
    # http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    format_map = (('DDD', r'%j'),
                  ('DD', r'%d'),
                  ('MMMM', r'%B'),
                  ('MMM', r'%b'),
                  ('MM', r'%m'),
                  ('YYYY', r'%Y'),
                  ('YY', r'%y'),
                  ('HH', r'%H'),
                  ('hh', r'%I'),
                  ('mm', r'%M'),
                  ('ss', r'%S'),
                  ('a', r'%p'),
                  ('ZZ', r'%z'),
                  )

    @classmethod
    def conv_datetime_format_py2js(cls, format):
        for js, py in cls.format_map:
            format = format.replace(py, js)
        return format

    @classmethod
    def conv_datetime_format_js2py(cls, format):
        for js, py in cls.format_map:
            format = format.replace(js, py)
        return format

    html_template = '''
        <div%(div_attrs)s>
            <input%(input_attrs)s/>
            <span class="input-group-addon">
                <span%(icon_attrs)s></span>
            </span>
        </div>'''

    js_template = """
        <script>
            $(function () {
                $("#%(picker_id)s").datetimepicker(%(options)s);});
        </script>
    """

    def __init__(self, attrs=None, format=None, options=None, div_attrs=None, icon_attrs=None):
        if not icon_attrs:
            icon_attrs = {'class': 'fa fa-calendar'}
        if not div_attrs:
            div_attrs = {'class': 'input-group date'}
        if format is None and options and options.get('format'):
            format = self.conv_datetime_format_js2py(options.get('format'))
        super(DateTimePicker, self).__init__(attrs, format)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'form-control'
        self.div_attrs = div_attrs and div_attrs.copy() or {}
        self.icon_attrs = icon_attrs and icon_attrs.copy() or {}
        self.picker_id = self.div_attrs.get('id') or None
        if not options:  # datetimepicker will not be initalized only when options is False
            self.options = False
        else:
            self.options = options and options.copy() or {}
            self.options['locale'] = translation.get_language()
            if format and not self.options.get('format') and not self.attrs.get('date-format'):
                self.options['format'] = self.conv_datetime_format_py2js(format)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        input_attrs = self.build_attrs(attrs)

        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            input_attrs['value'] = force_text(self.format_value(value))
        input_attrs = dict([(key, conditional_escape(val)) for key, val in input_attrs.items()])  # python2.6 compatible
        if not self.picker_id:
            self.picker_id = input_attrs.get('id', '') + '_picker'
        self.div_attrs['id'] = self.picker_id
        picker_id = conditional_escape(self.picker_id)
        div_attrs = dict(
            [(key, conditional_escape(val)) for key, val in self.div_attrs.items()])  # python2.6 compatible
        icon_attrs = dict([(key, conditional_escape(val)) for key, val in self.icon_attrs.items()])
        html = self.html_template % dict(div_attrs=flatatt(div_attrs),
                                         input_attrs=flatatt(input_attrs),
                                         icon_attrs=flatatt(icon_attrs))
        if not self.options:
            js = ''
        else:
            js = self.js_template % dict(picker_id=picker_id,
                                         options=json.dumps(self.options or {}))
        return mark_safe(force_text(html + js))


# As a TimeInput


class TimePicker2(TimeInput):
    class Media:
        class JsFiles(object):
            def __iter__(self):
                yield 'js/jquery-2.2.1.min.js'
                yield 'js/moment.min.js'
                yield 'pluginsRequired/bootstrap-datetimepicker/bootstrap-datetimepicker.min.js'
                lang = translation.get_language()
                if lang:
                    lang = lang.lower()
                    # There is language name that length>2 *or* contains uppercase.
                    lang_map = {
                        'ar-ma': 'ar-ma',
                        'en-au': 'en-au',
                        'en-ca': 'en-ca',
                        'en-gb': 'en-gb',
                        'en-us': 'en-us',
                        'fa-ir': 'fa-ir',
                        'fr-ca': 'fr-ca',
                        'ms-my': 'ms-my',
                        'pt-br': 'bt-BR',
                        'rs-latin': 'rs-latin',
                        'tzm-la': 'tzm-la',
                        'tzm': 'tzm',
                        'zh-cn': 'zh-CN',
                        'zh-tw': 'zh-TW',
                        'zh-hk': 'zh-TW',
                    }
                    if len(lang) > 2:
                        lang = lang_map.get(lang, 'en-us')
                    if lang not in ('en', 'en-us'):
                        yield 'pluginsRequired/bootstrap-datetimepicker/locale/%s.js' % (lang)

        js = JsFiles()
        css = {
            'all': ('pluginsRequired/bootstrap-datetimepicker/bootstrap-datetimepicker.min.css',
                    'css/font-awesome.min.css',),
        }

    # http://momentjs.com/docs/#/parsing/string-format/
    # http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    format_map = (('HH', r'%H'),
                  ('hh', r'%I'),
                  ('mm', r'%M'),
                  ('ss', r'%S'),
                  ('a', r'%p'),
                  ('ZZ', r'%z'),
                  )

    @classmethod
    def conv_datetime_format_py2js(cls, format):
        for js, py in cls.format_map:
            format = format.replace(py, js)
        return format

    @classmethod
    def conv_datetime_format_js2py(cls, format):
        for js, py in cls.format_map:
            format = format.replace(js, py)
        return format

    html_template = '''
        <div%(div_attrs)s>
            <input%(input_attrs)s/>
            <span class="input-group-addon">
                <span%(icon_attrs)s></span>
            </span>
        </div>'''

    js_template = """
        <script>
            $(function () {
                $("#%(picker_id)s").datetimepicker(%(options)s);});
        </script>
    """

    def __init__(self, attrs=None, format=None, options=None, div_attrs=None, icon_attrs=None):
        if not icon_attrs:
            icon_attrs = {'class': 'fa fa-clock-o'}
        if not div_attrs:
            div_attrs = {'class': 'input-group date'}
        if format is None and options and options.get('format'):
            format = self.conv_datetime_format_js2py(options.get('format'))
        super(TimePicker, self).__init__(attrs, format)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'form-control'
        self.div_attrs = div_attrs and div_attrs.copy() or {}
        self.icon_attrs = icon_attrs and icon_attrs.copy() or {}
        self.picker_id = self.div_attrs.get('id') or None
        if not options:  # datetimepicker will not be initalized only when options is False
            self.options = False
        else:
            self.options = options and options.copy() or {}
            self.options['locale'] = translation.get_language()
            if format and not self.options.get('format') and not self.attrs.get('date-format'):
                self.options['format'] = self.conv_datetime_format_py2js(format)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        input_attrs = self.build_attrs(attrs, extra_attrs=self.input_type)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            input_attrs['value'] = force_text(self.format_value(value))
        input_attrs = dict([(key, conditional_escape(val)) for key, val in input_attrs.items()])  # python2.6 compatible
        if not self.picker_id:
            self.picker_id = input_attrs.get('id', '') + '_picker'
        self.div_attrs['id'] = self.picker_id
        picker_id = conditional_escape(self.picker_id)
        div_attrs = dict(
            [(key, conditional_escape(val)) for key, val in self.div_attrs.items()])  # python2.6 compatible
        icon_attrs = dict([(key, conditional_escape(val)) for key, val in self.icon_attrs.items()])
        html = self.html_template % dict(div_attrs=flatatt(div_attrs),
                                         input_attrs=flatatt(input_attrs),
                                         icon_attrs=flatatt(icon_attrs))
        if not self.options:
            js = ''
        else:
            js = self.js_template % dict(picker_id=picker_id,
                                         options=json.dumps(self.options or {}))
        return mark_safe(force_text(html + js))
