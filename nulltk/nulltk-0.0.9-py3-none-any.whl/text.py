import tkinter as tk
import tkinter.font as tkfont
from .color import Color

#  Sources:
#    https://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget
#    https://stackoverflow.com/questions/65228477/text-doesnt-contain-any-characters-tagged-with-sel-tkinter

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.fg = Color.from_hex(self.option_get("foreground", "Foreground")).darker(0.25)

    def attach(self, text_widget):
        self.textwidget = text_widget
        
    def redraw(self, *args):
        """redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        max_width = 0
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            lnum_text = self.create_text(self.winfo_width(), y, anchor="ne", text=linenum, fill=self.fg.as_hex())
            x1,y1,x2,y2 = self.bbox(lnum_text)
            width = x2-x1
            max_width = max(width, max_width)
            i = self.textwidget.index("%s+1line" % i)
        self.config(width=max_width)

class Text(tk.Text):
    def __init__(self, master, *args,
            wrap=tk.NONE, tab_width=4,
            line_numbers=True, gutter_size=8,
            undo=True, autoseparators=True, maxundo=-1,
            **kwargs):
        self.tab_width = tab_width
        self.line_numbers = line_numbers
        self.gutter_size = gutter_size
        self._frame = tk.Frame(master)
        tk.Text.__init__(self, self._frame, *args,
            wrap=wrap, undo=undo, maxundo=maxundo,
            autoseparators=autoseparators, **kwargs)

        self._line_numbers = TextLineNumbers(self._frame, width=0)
        if line_numbers:
            self._line_numbers.attach(self)

        self._vsb = tk.Scrollbar(self._frame, orient="vertical", command=self.yview)
        self._line_numbers.pack(side=tk.LEFT, fill=tk.Y, padx=(gutter_size/2, gutter_size/2))
        tk.Text.pack(self, side=tk.LEFT, fill=tk.BOTH, expand=True)

        # config vscrollbar
        self.configure(yscrollcommand=self._vsb.set)

        self.bind("<<Change>>",  self._on_change)
        self.bind("<Configure>", self._on_change)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

        font = tkfont.Font(font=self['font'])
        tab = font.measure(' '*tab_width)
        self.config(tabs=tab)

    def _on_change(self, e):
        self._line_numbers.redraw()
        
        # check if we need to show/hide v. scrollbar (self._vsb)
        print(self.cget('height'), int(self.index('end-1c').split('.')[0]))
        if self.cget('height') > int(self.index('end-1c').split('.')[0]):
            self._vsb.pack_forget()
        else:
            self._vsb.pack(side=tk.RIGHT, anchor=tk.W, fill=tk.Y)

    def pack(self, *args, **kwargs):
        """ Forward `pack` to the containing frame """
        return self._frame.pack(*args, **kwargs)
    
    def pack_forget(self):
        """ Forward `pack_forget` to the containing frame """
        return self._frame.pack_forget()

    def _proxy(self, command, *args):
        # avoid error when copying
        if command == 'get' and (args[0] == 'sel.first' and args[1] == 'sel.last') and not self.tag_ranges('sel'): return
        # avoid error when deleting
        if command == 'delete' and (args[0] == 'sel.first' and args[1] == 'sel.last') and not self.tag_ranges('sel'): return
    
        # let the actual widget perform the requested action
        cmd = (self._orig, command) + args
        result = None
        try:
            result = self.tk.call(cmd)
        except tk.TclError as e:
            if str(e) in ('nothing to undo',): pass
            else: raise e

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if command in ("insert", "replace", "delete", "mark", "xview", "yview"):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result