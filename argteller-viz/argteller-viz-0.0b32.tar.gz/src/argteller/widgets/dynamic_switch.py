import os

try:

    from IPython.display import display
    import ipywidgets as widgets
    from ipywidgets import HBox, Label, VBox
    from ipywidgets import Button, Layout, HTML
    from traitlets import MetaHasTraits

except ModuleNotFoundError:

    class VBox():
        pass

    class MetaHasTraits():
        pass

class DynamicSwitch(VBox):
    
    def __init__(self, widget1, widget2, access_object):

        if not isinstance(VBox, MetaHasTraits):

            return

        self.access_object = access_object
        
        self.widget1 = widget1
        self.widget2 = widget2
        
        self.switch_widget = widgets.Button()
        self.switch_widget.description = "Next"

        self.save_widget = widgets.Button()
        self.save_widget.description = "Save As"

        self.filepath_widget = widgets.Text(layout=widgets.Layout(width='60%'))
        self.filepath_widget.value = os.path.join(os.getcwd(), 'temp_dsl.txt')
        
        access_object.filepath_widget = self.filepath_widget
        
        self.dynamic_widget_holder1 = VBox()
        self.dynamic_widget_holder2 = HBox()

        self.dynamic_widget_holder1.children = [self.widget1]
        self.dynamic_widget_holder2.children = [self.switch_widget]
        
        children = [
            self.dynamic_widget_holder1,
            self.dynamic_widget_holder2
        ]
        
        self.switch_widget.on_click(self._switch_widgets)

        self.save_widget.on_click(self._save_dsl)
        
        super().__init__(children=children)
        
    def _switch_widgets(self, widg):
        
        if self.switch_widget.description=='Back':

            new_widget = self.widget1
            self.switch_widget.description = "Next"

            self.dynamic_widget_holder2.children = [self.switch_widget]
            
        else:
            
            new_widget = self.widget2
            self.switch_widget.description = "Back"

            self.dynamic_widget_holder2.children = [self.switch_widget, self.save_widget, self.filepath_widget]
        
        self.dynamic_widget_holder1.children = [new_widget]

    def _save_dsl(self, widg):

        with open(self.filepath_widget.value, 'w') as f:
        
            f.write(self.access_object.get_active_param_values())




        











