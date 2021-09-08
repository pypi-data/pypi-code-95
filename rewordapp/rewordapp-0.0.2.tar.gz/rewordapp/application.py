"""Module containing the logic for the RewordApp application."""

import re
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from os import path
# from pprint import pformat
import webbrowser
from textwrap import dedent
import platform

from rewordapp import version
from rewordapp import edition


__version__ = version
__edition__ = edition


def get_relative_center_location(parent, width, height):
    """get relative a center location of parent window.

    Parameters
    ----------
    parent (tkinter): tkinter widget instance.
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


def create_msgbox(title=None, error=None, warning=None, info=None,
                  question=None, okcancel=None, retrycancel=None,
                  yesno=None, yesnocancel=None, **options):
    """create tkinter.messagebox
    Parameters
    ----------
    title (str): a title of messagebox.  Default is None.
    error (str): an error message.  Default is None.
    warning (str): a warning message. Default is None.
    info (str): an information message.  Default is None.
    question (str): a question message.  Default is None.
    okcancel (str): an ok or cancel message.  Default is None.
    retrycancel (str): a retry or cancel message.  Default is None.
    yesno (str): a yes or no message.  Default is None.
    yesnocancel (str): a yes, no, or cancel message.  Default is None.
    options (dict): options for messagebox.

    Returns
    -------
    any: a string or boolean result
    """
    if error:
        # a return result is a "ok" string
        result = messagebox.showerror(title=title, message=error, **options)
    elif warning:
        # a return result is a "ok" string
        result = messagebox.showwarning(title=title, message=warning, **options)
    elif info:
        # a return result is a "ok" string
        result = messagebox.showinfo(title=title, message=info, **options)
    elif question:
        # a return result is a "yes" or "no" string
        result = messagebox.askquestion(title=title, message=question, **options)
    elif okcancel:
        # a return result is boolean
        result = messagebox.askokcancel(title=title, message=okcancel, **options)
    elif retrycancel:
        # a return result is boolean
        result = messagebox.askretrycancel(title=title, message=retrycancel, **options)
    elif yesno:
        # a return result is boolean
        result = messagebox.askyesno(title=title, message=yesno, **options)
    elif yesnocancel:
        # a return result is boolean or None
        result = messagebox.askyesnocancel(title=title, message=yesnocancel, **options)
    else:
        # a return result is a "ok" string
        result = messagebox.showinfo(title=title, message=info, **options)

    return result


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
    repo_url = 'https://github.com/Geeks-Trident-LLC/rewordapp'
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


class Snapshot(dict):
    """Snapshot for storing data."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for attr, val in self.items():
            if re.match(r'[a-z]\w*$', attr):
                setattr(self, attr, val)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        for attr, val in self.items():
            if re.match(r'[a-z]\w*$', attr):
                setattr(self, attr, val)


class Application:

    browser = webbrowser

    def __init__(self):
        # support platform: macOS, Linux, and Window
        self.is_macos = platform.system() == 'Darwin'
        self.is_linux = platform.system() == 'Linux'
        self.is_window = platform.system() == 'Windows'

        # standardize tkinter widget for macOS, Linux, and Window operating system
        self.RadioButton = tk.Radiobutton if self.is_linux else ttk.Radiobutton
        self.CheckBox = tk.Checkbutton if self.is_linux else ttk.Checkbutton
        self.Label = ttk.Label
        self.Frame = ttk.Frame
        self.LabelFrame = ttk.LabelFrame
        self.Button = ttk.Button
        self.TextBox = ttk.Entry
        self.TextArea = tk.Text
        self.PanedWindow = ttk.PanedWindow

        self._base_title = 'RewordApp {}'.format(edition)
        self.root = tk.Tk()
        self.root.geometry('800x600+100+100')
        self.root.minsize(200, 200)
        self.root.option_add('*tearOff', False)

        # method call
        self.set_title()
        self.build_menu()

    def set_title(self, widget=None, title=''):
        """Set a new title for tkinter widget.

        Parameters
        ----------
        widget (tkinter): a tkinter widget.
        title (str): a title.  Default is empty.
        """
        widget = widget or self.root
        btitle = self._base_title
        title = '{} - {}'.format(title, btitle) if title else btitle
        widget.title(title)

    def build_menu(self):
        """Build menubar for RewordApp GUI."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file = tk.Menu(menu_bar)
        # preferences = tk.Menu(menu_bar)
        help_ = tk.Menu(menu_bar)

        menu_bar.add_cascade(menu=file, label='File')
        # menu_bar.add_cascade(menu=preferences, label='Preferences')
        menu_bar.add_cascade(menu=help_, label='Help')

        file.add_command(label='Open', command=lambda: self.callback_open_file())
        file.add_separator()
        file.add_command(label='Quit', command=lambda: self.root.quit())

        # preferences.add_command(
        #     label='Settings',
        #     command=lambda: self.callback_preferences_settings()
        # )
        # preferences.add_separator()
        # preferences.add_command(
        #     label='User Template',
        #     command=lambda: self.callback_preferences_user_template()
        # )

        help_.add_command(label='Documentation',
                          command=lambda: self.callback_help_documentation())
        help_.add_command(label='View Licenses',
                          command=lambda: self.callback_help_view_licenses())
        help_.add_separator()
        help_.add_command(label='About', command=lambda: self.callback_help_about())

    def callback_open_file(self):
        """Callback for Menu File > Open."""
        filetypes = [
            ('Text Files', '.txt', 'TEXT'),
            ('All Files', '*'),
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        print(filename)
        # if filename:
        #     with open(filename) as stream:
        #         if self.search_chkbox_var.get():
        #             self.search_chkbox.invoke()
        #
        #         if self.snapshot.curr_app == 'backup_app':
        #             self.close_backup_btn.invoke()
        #
        #         content = stream.read()
        #         self.test_data_btn.config(state=tk.NORMAL)
        #         self.test_data_btn_var.set('Test Data')
        #         self.set_textarea(self.result_textarea, '')
        #         self.snapshot.update(test_data=content)
        #         title = 'Open {} + LOAD Test Data'.format(filename)
        #         self.set_title(title=title)
        #         self.set_textarea(self.input_textarea, content)
        #         self.copy_text_btn.configure(state=tk.NORMAL)
        #         self.save_as_btn.configure(state=tk.NORMAL)
        #         self.input_textarea.focus()

    def callback_help_documentation(self):
        """Callback for Menu Help > Getting Started."""
        self.browser.open_new_tab(Data.documentation_url)

    def callback_help_view_licenses(self):
        """Callback for Menu Help > View Licenses."""
        self.browser.open_new_tab(Data.license_url)

    def callback_help_about(self):
        """Callback for Menu Help > About"""

        def mouse_over(event):  # noqa
            url_lbl.config(font=url_lbl.default_font + ('underline',))
            url_lbl.config(cursor='hand2')

        def mouse_out(event):  # noqa
            url_lbl.config(font=url_lbl.default_font)
            url_lbl.config(cursor='arrow')

        def mouse_press(event):  # noqa
            self.browser.open_new_tab(url_lbl.link)

        about = tk.Toplevel(self.root)
        self.set_title(widget=about, title='About')
        width, height = 460, 460
        x, y = get_relative_center_location(self.root, width, height)
        about.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        about.resizable(False, False)

        top_frame = self.Frame(about)
        top_frame.pack(fill=tk.BOTH, expand=True)

        paned_window = self.PanedWindow(top_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=8, pady=12)

        # company
        frame = self.Frame(paned_window, width=450, height=20)
        paned_window.add(frame, weight=4)

        fmt = 'RewordApp v{} ({} Edition)'
        company_lbl = self.Label(frame, text=fmt.format(version, edition))
        company_lbl.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        # URL
        cell_frame = self.Frame(frame, width=450, height=5)
        cell_frame.grid(row=1, column=0, sticky=tk.W, columnspan=2)

        url = Data.repo_url
        self.Label(cell_frame, text='URL:').pack(side=tk.LEFT)
        font_size = 12 if self.is_macos else 10
        style = ttk.Style()
        style.configure("Blue.TLabel", foreground="blue")
        url_lbl = self.Label(
            cell_frame, text=url, font=('sans-serif', font_size),
            style='Blue.TLabel'
        )
        url_lbl.default_font = ('sans-serif', font_size)
        url_lbl.pack(side=tk.LEFT)
        url_lbl.link = url

        url_lbl.bind('<Enter>', mouse_over)
        url_lbl.bind('<Leave>', mouse_out)
        url_lbl.bind('<Button-1>', mouse_press)

        # dependencies
        self.Label(
            frame, text='Dependencies:'
        ).grid(row=2, column=0, sticky=tk.W)

        # # regexapp package
        # import regexapp as rapp
        # text = 'Regexapp v{} ({} Edition)'.format(rapp.version, rapp.edition)
        # self.Label(
        #     frame, text=text
        # ).grid(row=3, column=0, padx=(20, 0), sticky=tk.W)
        #
        # # dlquery package
        # import dlquery as dlapp
        # text = 'DLQuery v{} ({} Edition)'.format(dlapp.version, dlapp.edition)
        # self.Label(
        #     frame, text=text
        # ).grid(row=4, column=0, padx=(20, 0), pady=(0, 10), sticky=tk.W)
        #
        # # textfsm package
        # import textfsm
        # text = 'TextFSM v{}'.format(textfsm.__version__)
        # self.Label(
        #     frame, text=text
        # ).grid(row=3, column=1, padx=(20, 0), sticky=tk.W)
        #
        # # PyYAML package
        # text = 'PyYAML v{}'.format(yaml.__version__)
        # self.Label(
        #     frame, text=text
        # ).grid(row=4, column=1, padx=(20, 0), pady=(0, 10), sticky=tk.W)

        # license textbox
        lframe = self.LabelFrame(
            paned_window, height=200, width=450,
            text=Data.license_name
        )
        paned_window.add(lframe, weight=7)

        width = 58 if self.is_macos else 51
        height = 18 if self.is_macos else 14 if self.is_linux else 15
        txtbox = self.TextArea(lframe, width=width, height=height, wrap='word')
        txtbox.grid(row=0, column=0, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(lframe, orient=tk.VERTICAL, command=txtbox.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        txtbox.config(yscrollcommand=scrollbar.set)
        txtbox.insert(tk.INSERT, Data.get_license())
        txtbox.config(state=tk.DISABLED)

        # footer - copyright
        frame = self.Frame(paned_window, width=450, height=20)
        paned_window.add(frame, weight=1)

        footer = self.Label(frame, text=Data.copyright_text)
        footer.pack(side=tk.LEFT, pady=(10, 10))

        set_modal_dialog(about)

    def run(self):
        """Launch RewordApp GUI."""
        self.root.mainloop()


def execute():
    """Launch RewordApp GUI."""
    app = Application()
    app.run()
