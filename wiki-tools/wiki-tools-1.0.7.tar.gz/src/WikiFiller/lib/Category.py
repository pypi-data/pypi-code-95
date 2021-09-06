import urwid
from termcolor import colored
from WikiFiller.lib.Globals import palette

class WikiCategory:
    def __init__(self, title, categories):
        wiki_categories = self.form_categories(title, categories)
        categories = urwid.Pile(wiki_categories)
        top = urwid.Filler(categories, valign='top')
        top = urwid.AttrMap(top, 'blue_background')
        self.loop = urwid.MainLoop(top, palette, unhandled_input=self.key_handler)
        self.loop.run()

    def form_categories(self, title, categories):
        header_text = urwid.AttrMap(urwid.Text(('banner', u"Wikipedia Categories"), align="center"), 'streak')
        pile_list = [urwid.AttrMap(urwid.CheckBox(t), 'banner') for t in categories]
        pile_list = [urwid.Padding(t, align=('relative', 18), width=('relative', 95)) for t in pile_list]
        horizontal_rule = urwid.Divider()
        continue_button = urwid.AttrMap(urwid.Button(('banner', 'Continue')), 'banner')
        continue_button = urwid.Padding(continue_button, align=('relative', 5), width=('relative', 8))
        urwid.connect_signal(continue_button.original_widget.original_widget, 'click', self.on_continue_clicked)
        title_text = urwid.Text(('banner_title', f"{title}:"), align="left")
        pile_list.insert(0, header_text)
        pile_list.insert(1, horizontal_rule)
        pile_list.insert(2, title_text)
        pile_list.insert(3, horizontal_rule)
        pile_list.append(horizontal_rule)
        pile_list.append(continue_button)
        return pile_list

    def on_continue_clicked(self, button):
        from requests import get
        widget_var = self.loop.widget.original_widget.original_widget.widget_list
        checkboxes_list = [widget.original_widget.original_widget for widget in widget_var if isinstance(widget, urwid.decoration.Padding)]
        checkboxes_list = [checkbox for checkbox in checkboxes_list if isinstance(checkbox, urwid.wimp.CheckBox)]
        output = [(c.get_label(), c.get_state()) for c in checkboxes_list]
        self.output = output
        raise urwid.ExitMainLoop()

    def key_handler(self, key):
        if key in ('f8', 'q', 'Q'):
            raise urwid.ExitMainLoop()

