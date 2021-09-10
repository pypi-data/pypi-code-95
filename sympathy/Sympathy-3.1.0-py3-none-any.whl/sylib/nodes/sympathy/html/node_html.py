# This file is part of Sympathy for Data.
# Copyright (c) 2019, Combine Control Systems AB
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

import os
import tempfile
import uuid
import sys
from urllib.parse import urlparse

import jinja2
from PySide2 import QtWidgets

try:
    import bokeh
    BOKEH_VERSION = bokeh.__version__
except ImportError:
    BOKEH_VERSION = '1.0.4'

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import ParameterView

from sylib.calculator import calculator_model
import sylib.calculator.plugins

from sympathy.api import qt2 as qt_compat
from sympathy.utils.prim import localuri

from sylib.html.html import Html
from sylib.html.geojson import GeoJSON

QtCore = qt_compat.QtCore
QtGui = qt_compat.QtGui


def webengine():
    import sylib.html.webengine as _webengine
    return _webengine


TEMPLATE_DIR = os.path.join(
  os.path.dirname(sylib.html.html.__file__), 'templates')


_htmlark = None


def htmlark():
    global _htmlark
    if _htmlark is None:
        import htmlark as _htmlark
        get_resource = _htmlark._get_resource
        urljoin = _htmlark.urljoin

        def is_local_path_with_drive(url_or_path):
            scheme = urlparse(url_or_path).scheme
            if scheme and len(scheme) == 1 and (
                    'a' <= scheme.lower() and scheme.lower() <= 'z'):
                return True
            return False

        def maybe_long_filename(url):
            if is_local_path_with_drive(url):
                url = f'\\\\?\\{os.path.abspath(url)}'
            return url

        def htmlark_get_resource_monkeypatch(resource_url):
            # Workaround for windows driveletter being confused with url
            # scheme: https://github.com/BitLooter/htmlark/issues/10.
            # Using long filename prefix: https://docs.microsoft.com/en-us/windows/desktop/fileio/naming-a-file#maximum-path-length-limitation  # NOQA
            # to create non confusable paths.
            resource_url = maybe_long_filename(resource_url)
            return get_resource(resource_url)

        def htmlark_urljoin_monkeypatch(base, url):
            if is_local_path_with_drive(base):
                res = os.path.join(os.path.dirname(base), url)
            else:
                res = urljoin(base, url)
            return res

        if sys.platform == 'win32':
            _htmlark._get_resource = htmlark_get_resource_monkeypatch
            _htmlark.urljoin = htmlark_urljoin_monkeypatch
    return _htmlark


def create_html_tempfile():
    fd1, tmp_html = tempfile.mkstemp(
        prefix='report-', suffix='.html')
    os.close(fd1)

    return tmp_html


def create_rel_or_temp_html_file(parameters, template_filename):
    if parameters['relative_tempfile'].value:
        template_dir = os.path.dirname(template_filename)
        # HACK(alexander): Handle situation when a relative path is used.
        # Need full path for preview browser.
        if not template_dir:
            template_dir = os.getcwd()
        return os.path.join(template_dir, 'report_tempfile.html')

    return create_html_tempfile()


def render_template_from_file(template_filename):
    with open(template_filename, 'r') as template_file:
        template_string = template_file.read()

    selected_template_path = os.path.dirname(template_filename)

    jinja_env = jinja2.Environment(
      loader=jinja2.FileSystemLoader(
        [TEMPLATE_DIR, selected_template_path]))
    template = jinja_env.get_template(template_filename)

    env = {}

    css_dir = os.path.join(TEMPLATE_DIR, 'css')
    env['css_links'] = [os.path.join(css_dir, 'styles.css')]

    rendered_template = template.render(env)

    return rendered_template


def reload_html(node_context, parameters, template_filename, tmp_html_path=None):
    infile = node_context.input.group('in')
    with open(template_filename, 'r') as template_file:
        template_string = template_file.read()

    if not parameters['custom_base'].value:
        base_template_dir = TEMPLATE_DIR
    else:
        base_template_dir = ''
    macros_template_path = os.path.join(TEMPLATE_DIR, 'macros')

    selected_template_path = os.path.dirname(template_filename)
    jinja_env = jinja2.Environment(
      loader=jinja2.FileSystemLoader(
        [base_template_dir, selected_template_path, macros_template_path]))

    @jinja2.contextfilter
    def tag_id(context, x):
        return 'a' + str(uuid.uuid4())

    env = calculator_model.context

    bokeh_version = BOKEH_VERSION

    if len(infile) > 0:
        env['arg'] = infile[0]
        css_dir = os.path.join(TEMPLATE_DIR, 'css')
        env['css_links'] = [os.path.join(css_dir, 'styles.css')]
        try:
            bokeh_version = infile[0][0].get()['bokeh_version']
        except Exception:
            pass

    jinja_env.filters['image_path'] = lambda x: os.path.join(
        TEMPLATE_DIR, 'img', x)

    jinja_env.filters['bokeh_version'] = lambda x: bokeh_version
    jinja_env.filters['to_result_table'] = lambda t: {col.name: col.data[0]
                                                      for col in t.cols()}
    jinja_env.filters['get_json'] = lambda x: x.get()
    jinja_env.filters['tag_id'] = tag_id
    jinja_env.filters['uuid'] = lambda x: str(uuid.uuid4())
    jinja_env.filters['zip_with_uuid'] = lambda x: list(zip(x, ['a' + str(uuid.uuid4())
                                                                for _ in range(len(x))]))
    template = jinja_env.get_template(os.path.basename(template_filename))

    plugins = sylib.calculator.plugins.available_plugins()
    for plugin in plugins:
        env.update(sylib.calculator.plugins.get_globals_dict(plugin))

    rendered_template = template.render(env)

    if tmp_html_path:
        with open(tmp_html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_template)

    return rendered_template


class HtmlReportWidget(ParameterView):
    def __init__(self, node_context, parent=None):
        super(HtmlReportWidget, self).__init__(parent)

        self.node_context = node_context
        self.parameters = node_context.parameters

        self.template_filename = None
        if node_context.input['in_ds'].is_valid():
            self.template_filename = node_context.input['in_ds'].decode_path()

        self.html_text = ''

        self.tmp_html = None
        self.tmp_url = None
        self.set_temp_paths()

        self._init_gui()

        if self.template_filename and os.path.isfile(self.template_filename):
            self.reload()
        else:
            self.preview.setHtml('')

    def _init_gui(self):
        self.template = self.parameters['template'].gui()
        #self.filename = self.parameters['template_filename'].gui()
        self.custom_base = self.parameters['custom_base'].gui()
        self.standalone = self.parameters['standalone'].gui()
        self.relative_tempfile = self.parameters['relative_tempfile'].gui()
        self.reload_button = QtWidgets.QPushButton("&Reload")
        self.preview_button = QtWidgets.QPushButton("&Preview")

        self.preview = webengine().QWebEngineView()
        self.preview_page = webengine().GraphJSWebPageView()
        self.preview_page.profile().clearHttpCache()
        self.preview.setPage(self.preview_page)
        self.error_textedit = QtWidgets.QTextEdit()

        progressbar = QtWidgets.QProgressBar()
        self.preview_page.loadProgress.connect(progressbar.setValue)

        self.lineedit = QtWidgets.QLineEdit()

        vlayout = QtWidgets.QVBoxLayout()
        main_vlayout = vlayout

        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalStretch(0)
        policy.setVerticalStretch(0)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)

        self.lineedit.setText(self.tmp_html)
        #vlayout.addWidget(self.template)
        #vlayout.addWidget(self.filename)

        if self.missing_template:
            vlayout.addWidget(QtWidgets.QLabel(
                'Configuration requires available input template '
                '(datasource)!'))
            widget = QtWidgets.QWidget()
            main_vlayout.addWidget(widget)
            vlayout = QtWidgets.QVBoxLayout()
            widget.setLayout(vlayout)
            widget.setDisabled(True)

        vlayout.addWidget(self.custom_base)
        vlayout.addWidget(self.standalone)
        vlayout.addWidget(self.relative_tempfile)
        self.preview.setSizePolicy(policy)
        #vlayout.addWidget(self.lineedit)
        #vlayout.addWidget(self.reload_button)
        vlayout.addWidget(self.preview_button)
        #vlayout.addWidget(self.web)
        vlayout.addWidget(self.preview)
        vlayout.addWidget(progressbar)
        #vlayout.addWidget(self.error_textedit)
        #vlayout.addStretch(1)
        self.setLayout(main_vlayout)

        self.preview_button.clicked[bool].connect(self.reload)
        self.reload_button.clicked[bool].connect(self.reload)
        self.relative_tempfile.stateChanged[int].connect(
            self.relative_tempfile_changed)
        #self.page.export[str].connect(self.on_click)
        # self.template.valueChanged[str].connect(
        #   self.set_value)

    @property
    def missing_template(self):
        return self.template_filename is None

    def relative_tempfile_changed(self, state):
        self.set_temp_paths()

    def set_temp_paths(self):
        self.tmp_html = create_rel_or_temp_html_file(
            self.parameters, self.template_filename)
        self.tmp_url = QtCore.QUrl(localuri(self.tmp_html))

    def on_click(self, html):
        #self.lineedit.setText(html)
        self.html_text = html
        self.reload()

    def preview_click(self):
        rendered_template = reload_html(self.node_context, self.parameters,
                                        self.template_filename)
        self.preview_page.update_html(rendered_template)

    def reload(self):
        try:
            reload_html(self.node_context, self.parameters,
                        self.template_filename, self.tmp_html)
            self.preview.setUrl(self.tmp_url)
        except Exception as e:
            self.preview.setHtml('<div>Error generating template: {}</div>'.format(str(e)))

    def set_value(self, text):
        self.parameters['template'].set_value(text)


class HtmlReport(synode.Node):
    """
    Create and render a Jinja2 template. See `Jinja2
    <http://jinja.pocoo.org/>`_ for full syntax of the template engine.

    Input data can be of any type and is accessed using {{arg}}.

    In order to make use of the built-in report API the template needs to consist of::

        {% import 'macros.html' as macros %}
        {% extends 'base.html' %}

        {% block contents %}
        {% endblock contents %}

    These lines will import a small report builidng API as **macros**.
    base.html is used as a base template (see Jinja2) and includes
    *bootstrap.css* and *boostrap.js* (via CDN) among other things.

    In *{% block contents %}* the user's layout is supposed to go.
    To add a report header the following code will do that::

        {% block contents %}
          {{ macros.header('Report header', 'sy_logo.png'|image_path) }}
        {% endblock contents %}

    This code uses a macro called *header*. The first argument is the
    title and the second is the path to a file. The filter **image_path**
    (Jinja2 feature) is used to select the package's image path.

    If a section with a title is needed this can be achieved by using the macro
    *section*, that takes a title and html as a string::

        {% block contents %}
          {{ macros.section('Section title', '<strong>test</strong>') }}
        {% endblock contents %}

    This makes it possible to combine multiple macros to create advanced reports.
    It is also possible to import a custom macro file to add even more functionality
    to easily customize reports.

    To see more advanced examples please look at the example flow Html.syx. That
    will include interactive Bokeh plots in the report (and more). Making your own
    interactive plots requires having bokeh installed.

    Some more examples below of how to incude data. Assume that the first input is a table.

    Example of iterating over each column::

       {% for name in arg.column_names() %}
          The column name is: {{name}}
          The column data is: {% for value in arg.col(name).data %} {{value}} {% endfor %}
       {% endfor %}

    Example of iterating over one specific column::

       {% for value in arg.col('Foo').data %}
          {{ value }}
       {% endfor %}

    Example of iterating over each row::

       {% for row in arg.to_rows() %}
          {% for value in row %} {{value}} {% endfor %}
       {% endfor %}

    The examples below assume that you have created a tuple or list of tables
    as input::

       {% for tbl in arg %}
          Table name: {{ tbl.name }}
          {% for col in tbl.cols() %}
             {{ col.name }}: {% for x in col.data %} {{x}} {% endfor %}
          {% endfor %}
       {% endfor %}

    Finally, you can connect complex datatypes such as an ADAF to the node::

       {% for name, col in arg.sys['system0']['raster0'].items() %}
          Signal: {{name}}
          Time: {{ col.t }}
          Value:  {{ col.y }}
       {% endfor %}

    Have a look at the :ref:`Data type APIs<datatypeapis>` to see what methods
    and attributes are available on the data type that you are working with.
    """

    name = 'Html Report'
    nodeid = 'org.sysess.sympathy.html.report'
    author = 'Alexander Busck'
    version = '0.1'
    icon = 'html_report.svg'
    #Update!!!!!!!
    description = (
        'Create and render a Jinja2 template. Use "{{arg name}}" for access '
        'to the data.')

    tags = Tags(Tag.Visual.Html)

    parameters = synode.parameters()
    jinja_code_editor = synode.Util.code_editor(language="jinja").value()
    parameters.set_string(
        'template', label="Template:", description='Select the Jinja2 template.',
        editor=jinja_code_editor)
    parameters.set_boolean('standalone', value=False, label='Standalone HTML',
                           description='Include all dependencies in one single HTML file.')
    parameters.set_boolean('custom_base', value=False, label='Use custom base',
                           description='Use a custom base.html located next to '
                                       'the template file.')
    parameters.set_boolean('relative_tempfile', value=False, label='Relative tempfile',
                           description='Put the preview tempfile in the same directory '
                                       'as the template file.')

    inputs = Ports([
        Port.Datasource('Datasource input', name='in_ds'),
        Port.Custom('<a>', 'Input', 'in', n=(0,1,1))])
    outputs = Ports([Html('HTML output', name='out')])

    def exec_parameter_view(self, node_context):
        widget = HtmlReportWidget(node_context)
        #widget.setMinimumWidth(1200)
        return widget

    def execute(self, node_context):
        infile = node_context.input.group('in')
        outfile = node_context.output['out']
        parameters = node_context.parameters

        template_filename = node_context.input['in_ds'].decode_path()
        if parameters['standalone'].value:
            tmp_html = create_rel_or_temp_html_file(parameters, template_filename)
            reload_html(node_context, parameters, template_filename, tmp_html)
            rendered_template = htmlark().convert_page(tmp_html)
        else:
            rendered_template = reload_html(node_context, parameters,
                                            template_filename)
        outfile.set(rendered_template)


class GeoJSONWidget(ParameterView):
    def __init__(self, json_dict, parent=None):
        super(GeoJSONWidget, self).__init__(parent)
        self.json_dict = json_dict

        self._init_gui()
        self.center_and_resize(QtWidgets.QApplication.instance())

    def center_and_resize(self, qapp):
        available_size = qapp.desktop().availableGeometry().size()
        width = available_size.width()
        height = available_size.height()
        new_size = QtCore.QSize(width*0.8, height*0.9)

        style = QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            new_size,
            qapp.desktop().availableGeometry()
        )
        self.setGeometry(style)

    def _init_gui(self):
        self.preview = webengine().QWebEngineView()
        self.preview_page = webengine().GeoJSONWebPageView()
        self.preview_page.data = self.json_dict
        self.preview_page.profile().clearHttpCache()
        self.preview.setPage(self.preview_page)

        self.error_textedit = QtWidgets.QTextEdit()

        leaflet_html_filepath = os.path.join(
            os.path.dirname(__file__), 'leaflet', 'index.html')

        self.preview.setUrl(QtCore.QUrl(localuri(leaflet_html_filepath)))
        progressbar = QtWidgets.QProgressBar()
        self.preview_page.loadProgress.connect(progressbar.setValue)

        self.lineedit = QtWidgets.QLineEdit()

        vlayout = QtWidgets.QVBoxLayout()

        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalStretch(0)
        policy.setVerticalStretch(0)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)

        self.preview.setSizePolicy(policy)
        vlayout.addWidget(self.preview)
        vlayout.addWidget(progressbar)

        self.setLayout(vlayout)


class GeoJSONNode(synode.Node):
    """
    Import a dict of GeoJSON data and show on a map.

    In order to use this node an account at `mapbox <https://www.mapbox.com/>`
    is required (it is free). Create an access token and use it in the
    environment variable MAPBOX_API_KEY when starting Sympathy in order to see
    the map properly.

    Linux and OSX:

    .. code-block:: bash

        MAPBOX_API_KEY="<TOKEN>" python -m sympathy gui

    Windows:

    .. code-block:: bat

        set MAPBOX_API_KEY=<TOKEN>
        python -m sympathy gui

    """
    name = 'GeoJSON'
    description = 'Import a dict of GeoJSON data and show on a map.'
    icon = 'geojson.svg'

    nodeid = 'org.sysess.sympathy.html.dicttogeojson'
    author = 'Alexander Busck'
    version = '1.0'

    tags = Tags(Tag.Visual.Html)

    inputs = Ports([Port.Custom('{json}', 'Dict of JSON', name='dict')])
    outputs = Ports([GeoJSON('GeoJSON', name='geojson')])

    parameters = synode.parameters()

    def execute(self, node_context):
        json_dict = node_context.input['dict']
        json_output = {k: v.get() for k, v in json_dict.items()}
        node_context.output['geojson'].set(json_output)


class HTMLToText(synode.Node):
    """
    HTML to text.
    """
    name = 'HTML to Text'
    description = 'Convert HTML to text.'
    icon = 'html_to_text.svg'

    nodeid = 'org.sysess.sympathy.html.htmltotext'
    author = 'Alexander Busck'
    version = '1.0'

    tags = Tags(Tag.Visual.Html)

    inputs = Ports([Html('HTML input', name='in')])
    outputs = Ports([Port.Text('Text output', name='out')])

    def execute(self, node_context):
        node_context.output['out'].set(
            node_context.input['in'].get())
