"""Module containing the logic for the DLApp."""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from os import path
from pprint import pformat
import webbrowser
from textwrap import dedent
from dlapp import create_from_csv_data
from dlapp import create_from_json_data
from dlapp import create_from_yaml_data
from dlapp.collection import Tabular
from dlapp import version
from dlapp import edition

import platform


def get_relative_center_location(parent, width, height):
    """get relative a center location of parent window.

    Parameters
    ----------
    parent (tkinter): tkinter component instance.
    width (int): a width of a child window.
    height (int): a height of a child window..

    Returns
    -------
    tuple: x, y location.
    """
    pwh, px, py = parent.winfo_geometry().split('+')
    px, py = int(px), int(py)
    pw, ph = [int(i) for i in pwh.split('x')]

    x = int(px + (pw - width) / 2)
    y = int(py + (ph - height) / 2)
    return x, y


def set_modal_dialog(dialog):
    """set dialog to become a modal dialog

    Parameters
    ----------
    dialog (tkinter.TK): a dialog or window application.
    """
    dialog.transient(dialog.master)
    dialog.wait_visibility()
    dialog.grab_set()
    dialog.wait_window()


class Data:
    license_name = 'BSD 3-Clause License'
    repo_url = 'https://github.com/Geeks-Trident-LLC/dlapp'
    license_url = path.join(repo_url, 'blob/main/LICENSE')
    # TODO: Need to update wiki page for documentation_url instead of README.md.
    documentation_url = path.join(repo_url, 'blob/develop/README.md')
    copyright_text = 'Copyright @ 2021-2040 Geeks Trident LLC.  All rights reserved.'

    @classmethod
    def get_license(cls):
        license_ = """
            BSD 3-Clause License

            Copyright (c) 2021-2040, Geeks Trident LLC
            All rights reserved.

            Redistribution and use in source and binary forms, with or without
            modification, are permitted provided that the following conditions are met:

            1. Redistributions of source code must retain the above copyright notice, this
               list of conditions and the following disclaimer.

            2. Redistributions in binary form must reproduce the above copyright notice,
               this list of conditions and the following disclaimer in the documentation
               and/or other materials provided with the distribution.

            3. Neither the name of the copyright holder nor the names of its
               contributors may be used to endorse or promote products derived from
               this software without specific prior written permission.

            THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
            AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
            IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
            DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
            FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
            DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
            SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
            CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
            OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
            OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        """
        license_ = dedent(license_).strip()
        return license_


class Content:
    """Content class

    Attributes
    ----------
    data (str): a text.


    """
    def __init__(self, data='', filename='', filetype=''):
        self.case = 'file' if filename else 'data' if data else 'unknown'
        self.data = data
        self.filename = filename
        self.filetype = filetype
        self.ready = False
        self.query_obj = None
        self.process()

    @property
    def is_csv(self):
        """Check if filename or content is in csv format."""
        return self.filetype == 'csv'

    @property
    def is_json(self):
        """Check if filename or content is in json format."""
        return self.filetype == 'json'

    @property
    def is_yaml(self):
        """Check if filename or content is in yaml format."""
        return self.filetype in ['yaml', 'yml']

    @property
    def is_ready(self):
        """Check if content is ready to use."""
        return self.ready

    def process_filename(self):
        if self.filename:
            _, ext = path.splitext(self.filename)
            extension = ext[1:]
            ext = ext.lower()[1:]
            if ext in ['csv', 'json', 'yml', 'yaml']:
                ext = 'yaml' if ext in ['yml', 'yaml'] else ext
                self.filetype = ext
            else:
                if not ext:
                    message = ('Make sure to select file with '
                               'extension json, yaml, yml, or csv.')
                else:
                    fmt = ('Selecting file extension is {}.  Make sure it is '
                           'in form of json, yaml, yml, or csv.')
                    message = fmt.format(extension)

                title = 'File extension'
                messagebox.showwarning(title=title, message=message)

            with open(self.filename, newline='') as stream:
                self.data = stream.read().strip()

                if not self.data:
                    message = 'This {} file is empty.'.format(self.filename)
                    title = 'File extension'
                    messagebox.showwarning(title=title, message=message)

    def process_data(self):
        if not self.data:
            if self.case != 'file':
                title = 'Empty data'
                message = 'data is empty.'
                messagebox.showwarning(title=title, message=message)

            return

        if not self.filetype:
            if self.case != 'file':
                title = 'Unselecting file extension'
                message = ('Need to check filetype radio button '
                           'such as json, yaml, or csv.')
                messagebox.showwarning(title=title, message=message)
                return

        if self.is_yaml:
            try:
                self.query_obj = create_from_yaml_data(self.data)
                self.ready = True
            except Exception as ex:
                title = 'Processing YAML data'
                message = '{}: {}'.format(type(ex), ex)
                messagebox.showerror(title=title, message=message)
        elif self.is_json:
            try:
                self.query_obj = create_from_json_data(self.data)
                self.ready = True
            except Exception as ex:
                title = 'Processing JSON data'
                message = '{}: {}'.format(type(ex), ex)
                messagebox.showerror(title=title, message=message)
        elif self.is_csv:
            try:
                self.query_obj = create_from_csv_data(self.data)
                self.ready = True
            except Exception as ex:
                title = 'Processing CSV data'
                message = '{}: {}'.format(type(ex), ex)
                messagebox.showerror(title=title, message=message)

    def process(self):
        """Analyze `self.filename` or `self.data` and
        assign equivalent `self.filetype`"""
        self.process_filename()
        self.process_data()


class Application:
    """A DLApp application class.

    Attributes
    ----------
    root (tkinter.Tk): a top tkinter app.
    content (Content): a Content instance.

    Methods
    -------
    build_menu() -> None
    run() -> None
    callback_file_open() -> None
    callback_file_exit() -> None
    callback_help_documentation() -> None
    callback_help_view_licenses() -> None
    callback_help_about() -> None
    """

    browser = webbrowser

    def __init__(self):
        self._base_title = 'DLApp {}'.format(edition)
        self.root = tk.Tk()
        self.root.geometry('800x600+100+100')
        self.root.minsize(200, 200)
        self.root.option_add('*tearOff', False)
        self.content = None

        self.panedwindow = None
        self.text_frame = None
        self.entry_frame = None
        self.result_frame = None

        self.radio_btn_var = tk.StringVar()
        self.radio_btn_var.set(None)
        self.lookup_entry_var = tk.StringVar()
        self.select_entry_var = tk.StringVar()
        self.result = None

        self.textarea = None
        self.result_textarea = None
        self.csv_radio_btn = None
        self.json_radio_btn = None
        self.yaml_radio_btn = None

        self.is_macos = platform.system() == 'Darwin'
        self.is_linux = platform.system() == 'Linux'
        self.is_window = platform.system() == 'Windows'

        self.RadioButton = tk.Radiobutton if self.is_linux else ttk.Radiobutton
        self.Label = ttk.Label
        self.Frame = ttk.Frame
        self.LabelFrame = ttk.LabelFrame
        self.Button = ttk.Button
        self.TextBox = ttk.Entry
        self.TextArea = tk.Text
        self.PanedWindow = ttk.PanedWindow

        self.set_title()
        self.build_menu()
        self.build_frame()
        self.build_textarea()
        self.build_entry()
        self.build_result()

    def set_title(self, node=None, title=''):
        """Set a new title for tkinter component.

        Parameters
        ----------
        node (tkinter): a tkinter component.
        title (str): a title.  Default is empty.
        """
        node = node or self.root
        btitle = self._base_title
        title = '{} - {}'.format(title, btitle) if title else btitle
        node.title(title)

    def callback_file_exit(self):
        """Callback for Menu File > Exit."""
        self.root.quit()

    def callback_file_open(self):
        """Callback for Menu File > Open."""
        filetypes = [
            ('JSON Files', '*json'),
            ('YAML Files', '*yaml'),
            ('YML Files', '*yml'),
            ('CSV Files', '*csv')
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            content = Content(filename=filename)
            if content.is_ready:
                self.set_title(title=filename)
                self.textarea.delete("1.0", "end")
                self.textarea.insert(tk.INSERT, content.data)
                self.radio_btn_var.set(content.filetype)

    def callback_help_documentation(self):
        """Callback for Menu Help > Getting Started."""
        self.browser.open_new_tab(Data.documentation_url)

    def callback_help_view_licenses(self):
        """Callback for Menu Help > View Licenses."""
        self.browser.open_new_tab(Data.license_url)

    def callback_help_about(self):
        """Callback for Menu Help > About"""
        def mouse_over(event):      # noqa
            url_lbl.config(font=url_lbl.default_font + ('underline',))
            url_lbl.config(cursor='hand2')

        def mouse_out(event):       # noqa
            url_lbl.config(font=url_lbl.default_font)
            url_lbl.config(cursor='arrow')

        def mouse_press(event):     # noqa
            self.browser.open_new_tab(url_lbl.link)

        about = tk.Toplevel(self.root)
        self.set_title(node=about, title='About')
        width, height = 440, 400
        x, y = get_relative_center_location(self.root, width, height)
        about.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        about.resizable(False, False)

        top_frame = self.Frame(about)
        top_frame.pack(fill=tk.BOTH, expand=True)

        panedwindow = self.PanedWindow(top_frame, orient=tk.VERTICAL)
        panedwindow.pack(fill=tk.BOTH, expand=True, padx=8, pady=12)

        # company
        frame = self.Frame(panedwindow, width=420, height=20)
        panedwindow.add(frame, weight=1)

        fmt = 'DLApp v{} ({} Edition)'
        company_lbl = self.Label(frame, text=fmt.format(version, edition))
        company_lbl.pack(side=tk.LEFT)

        # URL
        frame = self.Frame(panedwindow, width=420, height=20)
        panedwindow.add(frame, weight=1)

        url = Data.repo_url
        self.Label(frame, text='URL:').pack(side=tk.LEFT)
        font_size = 12 if self.is_macos else 10
        style = ttk.Style()
        style.configure("Blue.TLabel", foreground="blue")
        url_lbl = self.Label(frame, text=url, font=('sans-serif', font_size))
        url_lbl.config(style='Blue.TLabel')
        url_lbl.default_font = ('sans-serif', font_size)
        url_lbl.pack(side=tk.LEFT)
        url_lbl.link = url

        url_lbl.bind('<Enter>', mouse_over)
        url_lbl.bind('<Leave>', mouse_out)
        url_lbl.bind('<Button-1>', mouse_press)

        # license textbox
        lframe = self.LabelFrame(
            panedwindow, height=300, width=420,
            text=Data.license_name
        )
        panedwindow.add(lframe, weight=7)

        width = 55 if self.is_macos else 48
        height = 19 if self.is_macos else 15 if self.is_linux else 16
        txtbox = self.TextArea(lframe, width=width, height=height, wrap='word')
        txtbox.grid(row=0, column=0, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(lframe, orient=tk.VERTICAL, command=txtbox.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        txtbox.config(yscrollcommand=scrollbar.set)
        txtbox.insert(tk.INSERT, Data.get_license())
        txtbox.config(state=tk.DISABLED)

        # footer - copyright
        frame = self.Frame(panedwindow, width=380, height=20)
        panedwindow.add(frame, weight=1)

        footer = self.Label(frame, text=Data.copyright_text)
        footer.pack(side=tk.LEFT)

        set_modal_dialog(about)

    def build_menu(self):
        """Build menubar for dlapp."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file = tk.Menu(menu_bar)
        help_ = tk.Menu(menu_bar)

        menu_bar.add_cascade(menu=file, label='File')
        menu_bar.add_cascade(menu=help_, label='Help')

        file.add_command(label='Open', command=lambda: self.callback_file_open())
        file.add_separator()
        file.add_command(label='Quit', command=lambda: self.callback_file_exit())

        help_.add_command(label='Documentation',
                          command=lambda: self.callback_help_documentation())
        help_.add_command(label='View Licenses',
                          command=lambda: self.callback_help_view_licenses())
        help_.add_separator()
        help_.add_command(label='About', command=lambda: self.callback_help_about())

    def build_frame(self):
        """Build layout for DLApp."""
        self.panedwindow = self.PanedWindow(self.root, orient=tk.VERTICAL)
        self.panedwindow.pack(fill=tk.BOTH, expand=True)

        self.text_frame = self.Frame(
            self.panedwindow, width=600, height=400, relief=tk.RIDGE
        )
        self.entry_frame = self.Frame(
            self.panedwindow, width=600, height=100, relief=tk.RIDGE
        )
        self.result_frame = self.Frame(
            self.panedwindow, width=600, height=100, relief=tk.RIDGE
        )
        self.panedwindow.add(self.text_frame, weight=7)
        self.panedwindow.add(self.entry_frame)
        self.panedwindow.add(self.result_frame, weight=2)

    def build_textarea(self):
        """Build input text for DLApp."""

        self.text_frame.rowconfigure(0, weight=1)
        self.text_frame.columnconfigure(0, weight=1)
        self.textarea = self.TextArea(self.text_frame, width=20, height=5, wrap='none')
        self.textarea.grid(row=0, column=0, sticky='nswe')
        vscrollbar = ttk.Scrollbar(
            self.text_frame, orient=tk.VERTICAL, command=self.textarea.yview
        )
        vscrollbar.grid(row=0, column=1, sticky='ns')
        hscrollbar = ttk.Scrollbar(
            self.text_frame, orient=tk.HORIZONTAL, command=self.textarea.xview
        )
        hscrollbar.grid(row=1, column=0, sticky='ew')
        self.textarea.config(
            yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set
        )

    def build_entry(self):
        """Build input entry for DLApp."""
        def callback_run_btn():
            data = self.textarea.get('1.0', 'end').strip()
            filetype = self.radio_btn_var.get()
            lookup = self.lookup_entry_var.get()
            select = self.select_entry_var.get()

            content = Content(data=data, filetype=filetype)
            if not content.is_ready:
                return

            try:
                result = content.query_obj.find(lookup=lookup, select=select)
                self.result = result
                self.result_textarea.delete("1.0", "end")
                self.result_textarea.insert(tk.INSERT, str(result))

            except Exception as ex:
                title = 'Query problem'
                message = '{}: {}'.format(type(ex).__name__, ex)
                messagebox.showerror(title=title, message=message)

        def callback_tabular_btn():
            data = self.textarea.get('1.0', 'end').strip()
            filetype = self.radio_btn_var.get()
            lookup = self.lookup_entry_var.get()
            select = self.select_entry_var.get()

            content = Content(data=data, filetype=filetype)
            if not content.is_ready:
                return

            try:
                result = content.query_obj.find(lookup=lookup, select=select)
                self.result = result
                tabular_obj = Tabular(self.result)

                if tabular_obj.is_tabular:
                    text = tabular_obj.get()
                else:
                    fmt = 'CANNOT convert to tabular format because {!r}\n{}\n{}'
                    pretty_text = pformat(self.result)
                    text = fmt.format(tabular_obj.failure, '-' * 40, pretty_text)

                self.result_textarea.delete("1.0", "end")
                self.result_textarea.insert(tk.INSERT, str(text))

            except Exception as ex:
                title = 'Query problem'
                message = '{}: {}'.format(type(ex).__name__, ex)
                messagebox.showerror(title=title, message=message)

        def callback_clear_text_btn():
            self.textarea.delete("1.0", "end")
            self.result_textarea.delete("1.0", "end")
            self.radio_btn_var.set(None)
            self.lookup_entry_var.set('')
            self.select_entry_var.set('')
            self.result = None
            self.set_title()

        def callback_paste_text_btn():
            filetype = self.radio_btn_var.get()
            if filetype == 'None':
                title = 'Unselect CSV/JSON/YAML'
                message = 'Please select CSV, JSON, or YAML.'
                messagebox.showwarning(title=title, message=message)
                return

            try:
                data = self.root.clipboard_get()
                if data:
                    self.textarea.delete("1.0", "end")
                    # filetype = self.radio_btn_var.get()
                    self.content = Content(data=data, filetype=filetype)
                    if self.content.is_ready:
                        self.set_title(title='<<PASTE - Clipboard>>')
                        self.textarea.insert(tk.INSERT, data)
                        self.radio_btn_var.set(self.content.filetype)
            except Exception as ex:     # noqa
                title = 'Empty Clipboard',
                message = 'CAN NOT paste because there is no data in pasteboard.'
                messagebox.showwarning(title=title, message=message)

        def callback_clear_lookup_entry():
            self.lookup_entry_var.set('')

        def callback_clear_select_entry():
            self.select_entry_var.set('')

        width = 70 if self.is_macos else 79 if self.is_linux else 107
        x1 = 2 if self.is_linux else 0

        # frame for row 0
        frame = self.Frame(self.entry_frame, width=600, height=30)
        frame.grid(row=0, column=0, padx=10, pady=(4, 0), sticky=tk.W)

        # radio buttons
        self.csv_radio_btn = self.RadioButton(
            frame, text='csv', variable=self.radio_btn_var,
            value='csv'
        )
        self.csv_radio_btn.pack(side=tk.LEFT)

        self.json_radio_btn = self.RadioButton(
            frame, text='json', variable=self.radio_btn_var,
            value='json'
        )
        self.json_radio_btn.pack(side=tk.LEFT, padx=(x1, 0))

        self.yaml_radio_btn = self.RadioButton(
            frame, text='yaml', variable=self.radio_btn_var,
            value='yaml'
        )
        self.yaml_radio_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # open button
        open_file_btn = self.Button(frame, text='Open',
                                    command=self.callback_file_open)
        open_file_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # paste button
        paste_text_btn = self.Button(frame, text='Paste',
                                     command=callback_paste_text_btn)
        paste_text_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # clear button
        clear_text_btn = self.Button(frame, text='Clear',
                                     command=callback_clear_text_btn)
        clear_text_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # run button
        run_btn = self.Button(frame, text='Run',
                              command=callback_run_btn)
        run_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # pprint button
        tabular_btn = self.Button(frame, text='Tabular',
                                  command=callback_tabular_btn)
        tabular_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # frame for row 1 & 2
        frame = ttk.Frame(self.entry_frame, width=600, height=30)
        frame.grid(row=1, column=0, padx=10, pady=(0, 4), sticky=tk.W)

        # lookup entry
        lbl = self.Label(frame, text='Lookup')
        lbl.grid(row=0, column=0, padx=(0, 4), pady=0, sticky=tk.W)
        lookup_entry = self.TextBox(frame, width=width,
                                    textvariable=self.lookup_entry_var)
        lookup_entry.grid(row=0, column=1, padx=0, pady=0, sticky=tk.W)
        lookup_entry.bind('<Return>', lambda event: callback_run_btn())

        # clear button
        clear_lookup_btn = self.Button(frame, text='Clear',
                                       command=callback_clear_lookup_entry)
        clear_lookup_btn.grid(row=0, column=2, padx=(x1, 0), pady=0, sticky=tk.W)

        # select statement entry
        lbl = self.Label(frame, text='Select')
        lbl.grid(row=1, column=0, padx=(0, 4), pady=0, sticky=tk.W)
        select_entry = self.TextBox(frame, width=width,
                                    textvariable=self.select_entry_var)
        select_entry.grid(row=1, column=1, padx=0, pady=0, sticky=tk.W)
        select_entry.bind('<Return>', lambda event: callback_run_btn())

        # clear button
        clear_select_btn = self.Button(frame, text='Clear',
                                       command=callback_clear_select_entry)
        clear_select_btn.grid(row=1, column=2, padx=(x1, 0), pady=0, sticky=tk.W)

    def build_result(self):
        """Build result text"""
        self.result_frame.rowconfigure(0, weight=1)
        self.result_frame.columnconfigure(0, weight=1)
        self.result_textarea = self.TextArea(
            self.result_frame, width=20, height=5, wrap='none'
        )
        self.result_textarea.grid(row=0, column=0, sticky='nswe')
        vscrollbar = ttk.Scrollbar(
            self.result_frame, orient=tk.VERTICAL,
            command=self.result_textarea.yview
        )
        vscrollbar.grid(row=0, column=1, sticky='ns')
        hscrollbar = ttk.Scrollbar(
            self.result_frame, orient=tk.HORIZONTAL,
            command=self.result_textarea.xview
        )
        hscrollbar.grid(row=1, column=0, sticky='ew')
        self.result_textarea.config(
            yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set
        )

    def run(self):
        """Launch DLApp."""
        self.root.mainloop()


def execute():
    """Launch DLApp."""
    app = Application()
    app.run()
