from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QFileDialog, QComboBox,QRadioButton, QApplication, QLabel, QLineEdit,QDoubleSpinBox,QSlider,
                             QCheckBox,
                             QPushButton, QWidget,QGroupBox,QSpinBox, QColorDialog, QFrame,QVBoxLayout)

from PyQt5.QtCore import Qt
import numpy as np
from keyword import kwlist
import builtins
import os
import re
# TODO  create also oo hash that saves all needed data, so [o,oo] contains all need to save an open anything
# from TextEditor import TextEditor as HTMLEDITOR
try:
    from AWidget import AWidget
except:
    from Encrypt_Lab.AWidget import AWidget
# from codeeditor import QCodeEditor
# from code_editor.d import CodeEditor

class Input(AWidget):
    def __init__(self, parent, tp, name='', opts={}):

        super().__init__(parent, opts)

        self.real_parent = self.get_real_parent()
        self.float_to_int = 100
        if hasattr(self.real_parent, 'inputs_list'):

            self.input_list = self.real_parent.inputs_list.append(self)
        else:
            self.real_parent.inputs_list = [self]

        self.var_name = 'var_name' in opts and opts['var_name']
        if tp == 'name':
            self.var_name = True
        self.valid = True
        self.error_box = None
        self.opts = opts
        self.tp = tp
        self.my_parent = parent  # try self.parent()


        value = name in self.o and self.o[name]
        if not value and 'def' in opts:
            value = opts['def']

        self.name = self.force_name(name)
        l = None
        if not ('hide name' in opts and opts['hide name']):
            label = self.name
            if 'title' in opts:
                label = opts['title']
            l = QLabel(label)
            if 'center_title' in opts and opts['center_title']:
                self.layout().addWidget(l, alignment=Qt.AlignCenter)
            else:
                self.layout().addWidget(QLabel(label))
            if 'font' in opts and opts['font']:
                print('font')
                l.setStyleSheet(f"font-size: {opts['font']}px")


        if tp in ['string', 'python', 'code', 'varName', 'name', 'coded text']:
            value = value or ''
            func_name, w = ['textChanged', QLineEdit(value)]
            if 'center_text' in opts and opts['center_text']:
                w.setAlignment(Qt.AlignCenter)
        if tp in ['texteditor','code','coded text']:
            value = value or ''
            func_name, w = ['textChanged', CodeEditor(value)]
            # w.setStyleSheet("font: 12pt")
        if tp == 'integer':
            value = value or 0
            func_name, w = ['valueChanged', QSpinBox()]
            w.setRange(-2147483648, 2147483647)  # TODO add expression for max value

            w.setValue(value)
        if tp == 'float':
            value = value or 0.0
            func_name, w = ['valueChanged', QDoubleSpinBox()]
            w.setDecimals('decimals' in opts and opts['decimals'] or 8)
            w.setSingleStep(0.1)
            w.setRange(-2147483648, 2147483647)
            w.setValue(value)
        if tp == 'color':
            value = value or '#aaaaaa'
            func_name, w = ['textChanged', QLineEdit(value)]
            b = QPushButton('Pick Color')
            self.layout().addWidget(b)
            b.setStyleSheet(f'background-color: {value}')
            b.clicked.connect(lambda: w.setText(QColorDialog().getColor().name()))
            b.clicked.connect(lambda: b.setStyleSheet(f'background-color: {w.text()}'))
        if tp == 'HTML':
        # 1
            value = value or ''
            func_name, w = ['textChanged', QLineEdit(value)]
            b = QPushButton('Pick Color')
            self.layout().addWidget(b)
            b.setStyleSheet(f'background-color: {value}')
            b.clicked.connect(lambda: w.setText(QColorDialog().getColor().name()))
            b.clicked.connect(lambda: b.setStyleSheet(f'background-color: {w.text()}'))
        if tp == 'slider':
            if 'slide_minmax' in opts:
                minmax = opts['slide_minmax']
            else:
                minmax = (1, 20)
            float = False
            if 'float' in opts and opts['float']:
                float = True
                minmax = (self.float_to_int*minmax[0], self.float_to_int*minmax[1])
                value *= self.float_to_int

            if not value:
                if minmax:
                    value = int((minmax[1] + minmax[0])/2)
                else:
                    value = 10

            func_name, w = ['valueChanged', QSlider()]
            if float:
                l = QLabel(str(np.round(value/self.float_to_int, 2)))
            else:
                l = QLabel(str(np.round(value,2)))
            self.label = l
            self.layout().addWidget(l)

            w = QSlider(Qt.Horizontal)
            w.setMinimum(minmax[0])
            w.setMaximum(minmax[1])
            if float:
                w.setValue(value)
            else:
                w.setValue(value)

            w.setSingleStep(1)
        if tp == 'radio':
            self.radios = []
            for a in opts['radios']:
                if not value:
                    if 'def_index' in opts:
                        value = value or opts['radios'][opts['def_index']]
                    elif 'def' in opts:
                        value = value or opts['def']

                radiobutton = QRadioButton(a)
                radiobutton.val = a
                radiobutton.setChecked(a == value)
                self.radios.append(a)
                radiobutton.toggled.connect(lambda v: self.update_dic(self.sender().val))
                self.layout().addWidget(radiobutton)
                w = None
        if tp == 'single_radio':
            value = value or 11
            func_name, w = ['toggled', QRadioButton(name)]

        if tp == 'bool':
            value = value or 0
            func_name, w = ['stateChanged', QCheckBox()]
            w.setChecked(value)

        if tp in ['file', 'new_file', 'folder', 'server files', 'files']:
            value = value or ''
            func_name, w = ['textChanged', QLineEdit(value)]
            b = QPushButton(f"Open {tp}")
            if tp != 'server files':
                self.layout().addWidget(b)

            def safe_relpath(str):
                if str == '':
                    return ''
                return os.path.relpath(str)
            if tp in ['file', 'server files', 'files']:
                b.clicked.connect(lambda: w.setText(safe_relpath(QFileDialog.getOpenFileName(self)[0])))

                b2 = QPushButton(f"Open from server")
                self.layout().addWidget(b2)

                from server.FileTree import FileTree
                def lambd():
                    x = FileTree(w, uniq = tp != 'server files')
                    x.show()
                    self.addg = x

                b2.clicked.connect(lambda: lambd())


            if tp == 'new_file':
                b.clicked.connect(lambda: w.setText(safe_relpath(QFileDialog.getSaveFileName(self)[0])))
            if tp == 'files':
                b.clicked.connect(lambda: w.setText(safe_relpath(QFileDialog.getOpenFileNames(self)[0])))
            if tp == 'folder':
                b.clicked.connect(lambda: w.setText(safe_relpath(QFileDialog.getExistingDirectory(None, 'Select Directory'))))


        if tp in ['select', 'type']:
            if tp == 'type':
                opts['group'] = ('group' in opts and opts['group']) or 'general input'

            groups = {
                'general input': ['string', 'file','server files', 'folder', 'coded text', 'integer', 'float', 'color','bool']#'files',
            }

            func_name, w = ['currentTextChanged', QComboBox()]

            if 'allowed types' in opts:
                at = opts['allowed types']
                if type(at) == str:
                    types = [at]
                else:
                    types = at
            else:
                types = groups[opts['group']]
            [w.addItem(t) for t in types]

            value = value or w.itemText(0)

            index = w.findText(value, QtCore.Qt.MatchFixedString)
            w.setCurrentIndex(index)

        if tp == 'group':
            groups_types = {
                'view_definer': ['title', 'type', 'view data'],
                'input_definer': ['name', 'type', 'value'],
                'h': ['type', 'value']
            }

            hide_name = opts['group_type'] == 'h'

            titles = groups_types[opts['group_type']]
            w = False
            if not value:
                value = {}
                self.o[self.name] = value
            if 'input_definer_values' in opts:
                idv = opts['input_definer_values']

                if type(idv) == list:
                    for i in range(0, len(idv)):
                        value[titles[i]] = idv[i]
                else:  # hash
                    for k, v in idv.items():
                        value[k] = v

            save_until_next = None
            for i in range(0, len(titles)):
                title = titles[i]
                if title is 'type':
                    temp_opts = {'o': value, 'group': 'general input', 'hide name': hide_name}
                    if 'allowed types' in opts:
                        temp_opts['allowed types'] = opts['allowed types']

                    save_until_next = Input(self, 'type', title, temp_opts)
                else:
                    if not save_until_next:
                        Input(self, 'string', title, {'o': value})
                    else:

                        if 'type' in value:
                            generic_name = value['type']
                        else:
                            generic_name = 'string'

                        input = Input(self, generic_name, title, {'o': value, 'hide name': hide_name})

                        save_until_next.opts['call_on_update'] = input.transform
                        save_until_next = None
        if w:
            self.w = w
            w.setMinimumHeight(23)
            if tp == 'texteditor':
                w.setMinimumHeight(200)
            try:
                if (parent.parent().parent().__class__.__name__)=='InputGroup':
                    w.setMinimumHeight(78)
            except:
                1
            if tp == 'bool':
                wid = QWidget()
                wid_lay = QVBoxLayout()
                wid.setLayout(wid_lay)
                wid_lay.addWidget(w)
                self.layout().addWidget(wid)
            else:
                self.layout().addWidget(w)
            getattr(w, func_name).connect(self.update_dic)
        if w or tp == 'radio':
            if self.tp == 'slider' and 'float' in self.opts and self.opts['float']:
                value /= self.float_to_int
            self.o[self.name] = value
        if 'add_delete' in opts:
            btn = QPushButton('clear')
            btn.clicked.connect(self.clear)
            btn.setIcon(QtGui.QIcon('assets/icons/delete.png'))
            self.layout().addWidget(btn)

        if 'update_on_init' in opts and opts['update_on_init']:
            self.update_dic(value)
        if tp == 'code':
            self.setMinimumSize(500,200)
        self.present()

    def clipboardChanged(self):
        text = QApplication.clipboard().text()
        QApplication.clipboard().setText('banana') # TODO

    def update_dic(self, value=None):
        old_val = self.o[self.name]
        try:
            value = value or self.w.toPlainText()
        except:
            5 # TODO

        if self.tp == 'slider' and 'float' in self.opts and self.opts['float']:
            value/=self.float_to_int
        try:
            self.label.setText(str(np.round(value, 2)))
        except:
            5  # TODO
        if self.tp == 'float':
            value = float(value)
        self.o[self.name] = value
        if self.tp == 'text':
            1/0 # to raise error
            self.o[self.name] = '"""{0}"""'.format(value)

        if 'call_on_update' in self.opts:
            self.opts['call_on_update'](self)
        if 'on_update' in self.opts:
            self.opts['on_update']()
        if 'connect' in self.opts:
            try:
                self.opts['connect'](value)
            except:
                self.opts['connect'](value, self.name)
        print(self.opts)
        if 'filter' in self.opts:
            filtered_value = self.opts['filter'](value)
            if filtered_value != value:
                self.w.setText(filtered_value)
                value = filtered_value
        if 'connect' in self.opts: # TODO should be extea connect
            self.opts['connect'](value)

        self.value = value
        self.is_valid(value)

    def is_valid(self, value):
        if not self.var_name and 'regex' not in self.opts:
            return True
        regex = "\A[a-zA-Z][a-zA-Z_0-9]*\Z"
        if 'regex' in self.opts:
            regex = self.opts['regex']
        self.valid = re.search(regex, value) and (value not in self.reserved_words())
        self.update_style()

    def update_style(self):
        if self.valid:
            self.w.setStyleSheet('')
        else:
            self.w.setStyleSheet('border-color:red;  border-width: 1px;border-style: solid')

    def clear(self):
        self.setStyleSheet("background-color:{0};".format('blue'))

        if self.name in self.o:
            self.o.pop(self.name)
        try:
            self.my_parent.layout().removeWidget(self)
        except:
            'never mind'
        self.real_parent.inputs_list.remove(self)
        self.setParent(None)
        self.hide()

    def set_disable(self, flag):
        self.w.setDisabled(flag)

    def input_value(self):
        return self.o[self.name]

    def transform(self, input):
        my_index = self.my_parent.layout().indexOf(self)
        self.clear()
        # self.setStyleSheet("background-color:{0};".format('blue'))
        self.setStyleSheet("background-color:{0};".format('blue'))
        new_input = Input(self.my_parent, input.input_value(), self.name, {'o': self.o, 'index': my_index, 'hide name': (
                    'hide name' in self.opts and self.opts['hide name'])})
        input.opts['call_on_update'] = new_input.transform

    def reserved_words(self):
        generals = kwlist + dir(builtins)
        project_files_names = [file for file in os.listdir('../') if '.py' in file]
        return generals + project_files_names

    def get_real_parent(self):
        prnt = self.parent()
        while(prnt.__class__.__name__ in ['InputGroup','Input', 'QWidget', 'QScrollArea','QStackedWidget','QTabWidget' ]):
            prnt = prnt.parent()
        return prnt
