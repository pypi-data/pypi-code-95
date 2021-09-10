# This file is part of Sympathy for Data.
# Copyright (c) 2020 Combine Control Systems AB
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
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets
import urllib
import tempfile
import os
import shutil
from urllib.parse import ParseResult

from sympathy.platform import widget_library as sywidgets
from sympathy.platform.parameter_types import (
    Connection, Credentials, CredentialsMode)


def _web_engine_view(parent):
    # Unsupported by Qt.py.
    from PySide2.QtWebEngineWidgets import QWebEngineView
    return QWebEngineView(parent=parent)


def _web_engine_profile(storage_name, parent):
    # Unsupported by Qt.py.
    from PySide2.QtWebEngineWidgets import QWebEngineProfile
    return QWebEngineProfile(storage_name)


def _web_engine_page(profile, parent):
    # Unsupported by Qt.py.
    from PySide2.QtWebEngineWidgets import QWebEnginePage
    return QWebEnginePage(profile, parent)


class PasswordLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setEchoMode(self.EchoMode.Password)


class LineValueMixin:
    def __init__(self, value=None, **kwargs):
        super().__init__(**kwargs)
        self.set_value(value)

    def get_value(self):
        return self.text()

    def set_value(self, value):
        self.setText(value)

    def clear(self):
        self.setText('')


class CredentialMixin(LineValueMixin):
    type = None

    def __init__(self, value=None, parent=None):
        super().__init__(parent=parent)

        self._reset = False
        if value is None:
            self.setPlaceholderText('Not set')
        elif value:
            self.set_value(value)

        self.textEdited.connect(self._handle_value_edited)

    def _handle_value_edited(self, value):
        if not self._reset:
            self.value_edited.emit(value)

    def clear(self):
        self.from_dict({self.type: ''})

    def to_dict(self):
        return {
            self.type: self.get_value(),
        }

    def from_dict(self, data):
        try:
            self._reset = True
            self.set_value(data[self.type])
        finally:
            self._reset = False


class ShowPasswordLineEdit(QtWidgets.QWidget):
    """
    Works as a QLineEdit for passwords with a button to show the text
    temporarily. The button state is cleared on setText for convenience since
    setText in all current uses means showing a new password. This could be
    made explicit if it causes problems.

    Implements the current required subset of QLineEdit interface. Add more
    operations when needed.
    """

    textEdited = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._show_widget = sywidgets.ShowButton()
        self._show_widget.setFocusPolicy(QtCore.Qt.NoFocus)
        self._password_widget = PasswordLineEdit()
        layout.addWidget(self._password_widget)
        layout.addWidget(self._show_widget)
        self.setLayout(layout)
        self._show_widget.toggled.connect(self._handle_show_widget_toggled)
        self._password_widget.textEdited.connect(self.textEdited)

    def _handle_show_widget_toggled(self, checked=False):
        if checked:
            self._password_widget.setEchoMode(
                self._password_widget.EchoMode.Normal)
        else:
            self._password_widget.setEchoMode(
                self._password_widget.EchoMode.Password)

    def text(self):
        return self._password_widget.text()

    def setText(self, value):
        self._show_widget.setChecked(False)
        return self._password_widget.setText(value)

    def get_value(self):
        return self.text()

    def set_value(self, value):
        self.setText(value)

    def setPlaceholderText(self, text):
        self._password_widget.setPlaceholderText(text)


class SecretWidget(CredentialMixin, ShowPasswordLineEdit):
    type = 'secret'
    value_edited = QtCore.Signal(str)

    def __init__(self, value='', parent=None):
        super().__init__(value=value, parent=parent)


class UsernameWidget(CredentialMixin, QtWidgets.QLineEdit):
    type = 'username'
    value_edited = QtCore.Signal(str)

    def __init__(self, value='', parent=None):
        super().__init__(value=value, parent=parent)


class PasswordWidget(CredentialMixin, ShowPasswordLineEdit):
    type = 'password'
    value_edited = QtCore.Signal(str)

    def __init__(self, value='', parent=None):
        super().__init__(value=value, parent=parent)


class ResourceEditWidget(LineValueMixin, QtWidgets.QLineEdit):
    pass


class ResourceWidget(LineValueMixin, sywidgets.ReadOnlyLineEdit):
    pass


class NullCredentialsWidget(QtWidgets.QWidget):
    def secrets(self):
        return {}


class DenyCredentialsWidget(NullCredentialsWidget):

    def __init__(self, resource, parent=None):
        super().__init__(parent=parent)
        layout = sywidgets.FormLayout()
        self.setLayout(layout)
        deny_label = QtWidgets.QLabel(
            'Credential requests are denied by current settings')
        self.setToolTip(
            'Set to Allow in preferences to use Credentials')
        layout.addRow(deny_label)

        self._resource_widget = ResourceWidget(resource)
        layout.addRow('Resource', self._resource_widget)

    def secrets(self):
        return {}

    def set_resource(self, resource):
        self._resource_widget.set_value(resource)


class EditCredentialWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = sywidgets.FormLayout()
        self.setLayout(layout)
        self._resource_widget = ResourceWidget('')
        layout.addRow('Resource', self._resource_widget)
        hline = sywidgets.HLine()
        layout.addRow(hline)
        self._connection = None

    def connection(self):
        return self._connection

    def setup(self, connection, secrets):
        self.set_connection(connection)

    def set_connection(self, connection):
        self._connection = connection
        resource = ''
        if connection is not None:
            resource = connection.identifier()
        self._resource_widget.set_value(resource)

    def secrets(self):
        raise NotImplementedError

    def set_secrets(self, secrets):
        raise NotImplementedError


class EditSecretsWidget(EditCredentialWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._secret_widgets = {}

    def secrets(self):
        return {k: v.get_value() for k, v in
                self._secret_widgets.items()}

    def set_secrets(self, secrets):
        for k, widget in self._secret_widgets.items():
            widget.set_value(secrets.get(k, ''))

    def setup(self, connection, secrets):
        old = self._connection
        super().setup(connection, secrets)

        if old is not None:
            self._old_widgets = []
            for k, widget in self._secret_widgets.items():
                widget.deleteLater()
                self._old_widgets.append(widget)
                self.layout().removeRow(widget)
            self._secret_widgets.clear()

        if self._connection is not None:
            for k, v in secrets.items():
                widget = SecretWidget(v)
                self._secret_widgets[k] = widget
                self.layout().addRow(k, widget)


class EditLoginWidget(EditCredentialWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._password_widget = PasswordWidget('')
        self._username_widget = UsernameWidget('')
        layout = self.layout()
        layout.addRow('Username', self._username_widget)
        layout.addRow('Password', self._password_widget)

    def secrets(self):
        return {
            'username': self._username_widget.get_value(),
            'password': self._password_widget.get_value(),
        }

    def set_secrets(self, secrets):
        self._username_widget.set_value(secrets.get('username', ''))
        self._password_widget.set_value(secrets.get('password', ''))

    def setup(self, connection, secrets):
        super().setup(connection, secrets)
        self.set_secrets(secrets)


class AzureLoginWidget(QtWidgets.QWidget):
    finished = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()
        self._redirect_url = None
        view = _web_engine_view(parent=self)
        # Use separate cache folder for each login.
        # This helps with changing it, otherwise it will re-use the existing.
        # Could also help with issues from multiple WebEngines using the same
        # folder.
        profile = view.page().profile()
        profile.setHttpCacheType(profile.NoCache)
        profile.setPersistentCookiesPolicy(profile.NoPersistentCookies)
        temp_root = os.path.join(tempfile.gettempdir(), 'Sympathy', 'Azure')
        os.makedirs(temp_root, exist_ok=True)
        self._temp = tempfile.mkdtemp(dir=temp_root)
        profile.setPersistentStoragePath(self._temp)
        self._view = view

        layout.addWidget(view)
        self.setLayout(layout)
        self._view_running = False
        view.urlChanged.connect(self._view_url_changed)
        view.loadStarted.connect(self._view_load_started)
        self._result = None
        policy = self.sizePolicy()
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(policy)

    def _view_url_changed(self, url):
        url = urllib.parse.urlparse(url.toString())
        if self.same_resource(url, self._redirect_url) and self._view_running:
            self._result = self.url_query_to_dict(url)
            self._view_done()
            self.finished.emit()

    def _view_load_started(self):
        pass

    def _view_done(self):
        if self._view_running:
            self._view_running = False
            self._view.urlChanged.disconnect(self._view_url_changed)
            self._view.loadStarted.disconnect(self._view_load_started)
            self._view.stop()

    def setup(self, auth_url, redirect_url):
        self._result = None
        self._view_running = True
        self._redirect_url = urllib.parse.urlparse(redirect_url)
        self._view.load(auth_url)

    def cleanup(self):
        if self._temp:
            shutil.rmtree(self._temp, ignore_errors=True)
            self._temp = None

    def result(self):
        return self._result

    @staticmethod
    def flatlist(data: dict):
        """
        Replace top-level list values in dict with
        their last value.
        """
        res = {}
        for k, vo in data.items():
            if isinstance(vo, list):
                for v in vo:
                    res[k] = v
            else:
                res[k] = vo
        return res

    @staticmethod
    def same_resource(url1: ParseResult, url2: ParseResult) -> bool:
        def resource(url):
            return (url.scheme, url.netloc, url.port, url.path or '/')

        return resource(url1) == resource(url2)

    @classmethod
    def url_query_to_dict(cls, url: ParseResult) -> dict:
        query_seg = url.query
        query_data = urllib.parse.parse_qs(query_seg)
        return cls.flatlist(query_data)


class EditAzureWidget(EditCredentialWidget):

    finished = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._login_widget = AzureLoginWidget(parent=self)
        self._login_widget.finished.connect(self.finished)
        self._secrets = {'state': None, 'code': None}
        layout = self.layout()
        layout.addRow(self._login_widget)

    def secrets(self):
        return self._login_widget.result() or self._secrets

    def set_secrets(self, secrets):
        pass

    def setup(self, connection, secrets):
        super().setup(connection, secrets)
        auth = secrets['auth']
        self._secrets = {'state': auth['state'], 'code': None}
        self._login_widget.setup(auth['auth_url'], auth['redirect_url'])

    def cleanup(self):
        self._login_widget.cleanup()


class EditCredentialsDialog(QtWidgets.QDialog):
    _title = 'Unknown'

    def __init__(self, connection, secrets, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle(self._title)
        self._edit_widget = self._editor_cls()(parent=self)
        self._edit_widget.setup(connection, secrets)
        layout.addWidget(self._edit_widget)
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok |
            QtWidgets.QDialogButtonBox.Cancel)
        self._add_stretch()

        layout.addWidget(button_box)

        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalStretch(1)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Preferred)
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Maximum)
        self.setSizePolicy(policy)

        self._ok_button = button_box.button(
            QtWidgets.QDialogButtonBox.Ok)
        self._cancel_button = button_box.button(
            QtWidgets.QDialogButtonBox.Cancel)

        self._ok_button.clicked.connect(self.accept)
        self._cancel_button.clicked.connect(self.reject)

        self.setMinimumWidth(400)

    def _add_stretch(self):
        pass

    def _editor_cls(self) -> EditCredentialWidget:
        raise NotImplementedError

    def secrets(self):
        return self._edit_widget.secrets()


class EditSecretsDialog(EditCredentialsDialog):
    _title = 'Edit Secrets'

    def __init__(self, connection, secrets, parent=None):
        super().__init__(connection, secrets, parent=parent)

    def _add_stretch(self):
        self.layout().addStretch()

    def _editor_cls(self):
        return EditSecretsWidget


class EditLoginDialog(EditSecretsDialog):
    _title = 'Edit Login'

    def _editor_cls(self):
        return EditLoginWidget


class EditAzureDialog(EditCredentialsDialog):
    _title = 'Edit Azure Login'

    def __init__(self, connection, secrets, parent=None):
        super().__init__(connection, secrets, parent=parent)
        self._edit_widget.finished.connect(self.accept)
        self._ok_button.setVisible(False)
        self.finished.connect(self._handle_finished)
        self.setMinimumSize(QtCore.QSize(600, 600))

    def _editor_cls(self):
        return EditAzureWidget

    def _handle_finished(self, result):
        self._edit_widget.cleanup()


def add_form_row(layout, label, widget):
    # layout.addRow(label, widget)
    label_widget = QtWidgets.QLabel(label)
    hlayout = QtWidgets.QHBoxLayout()
    hlayout.addWidget(label_widget)
    hlayout.addWidget(widget)
    hlayout.setStretchFactor(widget, 1)
    layout.addLayout(hlayout)
    return hlayout, label


def _form_layout():
    # layout = QtWidgets.QFormLayout()
    layout = QtWidgets.QVBoxLayout()
    return layout


def create_button_box():
    box = QtWidgets.QDialogButtonBox()
    return box


def standard_button_box(dialog):
    box = create_button_box()
    box.addButton(QtWidgets.QDialogButtonBox.Ok)
    box.addButton(QtWidgets.QDialogButtonBox.Cancel)
    box.accepted.connect(dialog.accept)
    box.rejected.connect(dialog.reject)
    return box


class ParameterCredentialWidget(QtWidgets.QWidget):
    changed = QtCore.Signal()
    request_edit_dialog = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def load(self, credentials: Credentials):
        raise NotImplementedError()

    def credential(self):
        raise NotImplementedError()

    def action(self) -> QtWidgets.QAction:
        raise NotImplementedError()

    def mode(self):
        raise NotImplementedError()

    def create_edit_dialog(self, connection: Connection, secrets: dict
                           ) -> QtWidgets.QWidget:
        raise NotImplementedError()

    def can_edit(self):
        return False

    def set_can_edit(self, value):
        pass


class NoParameterCredentialWidget(ParameterCredentialWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._action = sywidgets.create_action(
            text='No credentials',
            icon_name='actions/key-slash.svg',
            tooltip_text='Use resource as is, with no credentials')

    def load(self, credentials: Credentials):
        pass

    def credential(self):
        return Credentials()

    def action(self) -> QtWidgets.QAction:
        return self._action

    def mode(self):
        return None

    def create_edit_dialog(self, connection, secrets):
        raise NotImplementedError()


class LoginParameterCredentialWidget(ParameterCredentialWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = sywidgets.FormLayout()
        layout.setContentsMargins(0, 0, 0, 5)
        layout.setVerticalSpacing(5)
        self.setLayout(layout)
        self._name_widget = QtWidgets.QLineEdit()
        self._name_widget.setPlaceholderText('Optional resource name')
        login_name_tooltip = (
            'Optional resource name used instead of the resource itself '
            'for storing and loading login credentials.\n\n'
            'It can be used to share the same login for multiple resources '
            'or to allow different logins.\nFor example, if the resource '
            'is http://example.com/path it might be useful to set the name '
            'to\nhttp://example.com and use that in each node where you '
            'want to access http://example.com.')
        self._name_widget.setToolTip(login_name_tooltip)
        layout.addRow('Name', self._name_widget)
        login_label = layout.labelForField(self._name_widget)
        login_label.setToolTip(login_name_tooltip)
        button_box = create_button_box()
        self._edit_button = button_box.addButton(
            'Edit Login', button_box.ActionRole)
        self._edit_button.setToolTip(
            'Edit the credentials used for this resource '
            '(username and password).\n'
            'Note that logins are shared between all nodes that use '
            'login credentials.\n\n'
            'Credentials are only stored on your system and are not part of '
            'the node\'s configuration.')
        layout.addRow(None, button_box)
        self.set_can_edit(False)

        self._name_widget.textChanged.connect(self.changed)

        self._edit_button.clicked.connect(
            self._handle_edit_button_clicked)

        self._action = sywidgets.create_action(
            text='Login credentials',
            icon_name='actions/user-key-4.svg',
            tooltip_text='Use resource with login credentials')

    def mode(self):
        return CredentialsMode.login

    def action(self):
        return self._action

    def load(self, credentials: Credentials):
        self._name_widget.setText(credentials.name)

    def credential(self):
        return Credentials(
            mode=CredentialsMode.login,
            name=self._name_widget.text())

    def create_edit_dialog(self, connection, secrets, parent=None
                           ) -> QtWidgets.QWidget:
        return EditLoginDialog(connection, secrets, parent=parent)

    def _handle_edit_button_clicked(self, checked):
        self.request_edit_dialog.emit()


class SecretsParameterCredentialWidget(ParameterCredentialWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = sywidgets.FormLayout()
        layout.setContentsMargins(0, 0, 0, 5)
        layout.setVerticalSpacing(5)

        self.setLayout(layout)
        button_box = create_button_box()
        self._edit_button = button_box.addButton(
            'Edit Secrets', button_box.ActionRole)
        self._edit_button.setToolTip(
            'Edit the secret credentials used for this resource. '
            'Secrets are variables in the resource, '
            'written inside angular brackets.\nFor example, username and '
            'password in "http://<username>:<password>@example.com".\nNote '
            'that secrets are shared between all nodes that use secret '
            'credentials.\n\n'
            'Credentials are only stored on your system and are not part of '
            'the node\'s configuration.')

        self.set_can_edit(False)
        layout.addRow(button_box)
        self._edit_button.clicked.connect(
            self._handle_edit_button_clicked)

        self._action = sywidgets.create_action(
            text='Secret credentials',
            icon_name='actions/mask-key-3.svg',
            tooltip_text='Use resource with secret credentials')

    def action(self):
        return self._action

    def mode(self):
        return CredentialsMode.secrets

    def load(self, credentials: Credentials):
        pass

    def credential(self):
        return Credentials(
            mode=CredentialsMode.secrets)

    def create_edit_dialog(self, connection, secrets, parent=None):
        return EditSecretsDialog(connection, secrets, parent=parent)

    def _handle_edit_button_clicked(self, checked):
        self.request_edit_dialog.emit()

    def can_edit(self):
        return self._can_edit

    def set_can_edit(self, value):
        self._can_edit = value
        self._edit_button.setEnabled(value)
