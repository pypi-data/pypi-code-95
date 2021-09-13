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
        

class ParamTextWidget(VBox):
    
    def __init__(self, name, example=None, default_value=None, preset_value=None, optional=False, widget=None, 
        widget_initialized=None, param_setter_event=None, set_from=None):

        if not isinstance(VBox, MetaHasTraits):

            return

        self.name = name
        self.type = 'text'

        self.initial = not widget_initialized
        self.param_setter_event = param_setter_event
        
        style = style = {'description_width': 'initial'}
        layout = Layout(display='flex', 
                        flex_flow='row', 
                        flex_basis='auto',
                        align_content='stretch', 
                        justify_content='center',
                        # align_items='baseline stretch',
                        width='70%',
                        
                        flex_wrap='wrap',
                        border=None,
                        # flex_basis='200%'
                        )
        if set_from:
            label = widgets.HTML(f"<b><font size=2 color='grey'>{self.name} (set via {set_from})</b>")
        elif preset_value:
            label = widgets.HTML(f"<b><font size=2 color='blue'>{self.name}</b>")
        elif optional:
            label = widgets.HTML(f"<b><font size=2 color='grey'>{self.name} (optional)</b>")
        else:
            label = widgets.HTML(f"<b><font size=2 color='black'>{self.name}</b>")

        if widget:
            self.widget = widget
        else:
            if example is None:
                self.widget = VBox([widgets.Text(style=style, layout=layout)])
            else:
                self.widget = VBox([
                    widgets.Label(value=example),
                    widgets.Text(style=style, layout=layout)])

        if self.initial or self.param_setter_event.isSet() :  # So that user input is not overwritten every time.

            if preset_value is not None:  # So that preset values take precedence over default values.
                self.widget.children[-1].value = str(preset_value) 
                
            elif default_value is not None:  
                self.widget.children[-1].value = str(default_value) 
                
            self.initial = False
        
        children = [label, self.widget]
        super().__init__(children=children)
        
    def get_value(self):
        
        return self.widget.children[-1].value


class ParamChoiceWidget(VBox):
    
    def __init__(self, name, options, default_value=None, preset_value=None, optional=False, widget=None, widget_initialized=None, param_setter_event=None):

        if not isinstance(VBox, MetaHasTraits):
            return

        self.name = name
        self.type = 'choice'
        
        self.initial = not widget_initialized
        self.param_setter_event = param_setter_event

        layout = Layout(width='auto')
        
        if preset_value:
            label = widgets.HTML(f"<b><font size=2 color='blue'>{self.name}</b>")
        elif optional:
            label = widgets.HTML(f"<b><font size=2 color='grey'>{self.name}</b>")
        else:
            label = widgets.HTML(f"<b><font size=2 color='black'>{self.name}</b>")

        if widget:
            self.widget = widget
        else:
            self.widget =  VBox([widgets.RadioButtons(options=options, disabled=False, layout=layout)])

        if self.initial or self.param_setter_event.isSet() :  # So that user input is not overwritten every time.

            if preset_value is not None:  # So that preset values take precedence over default values.
            
                self.widget.children[0].value = str(preset_value) 
                
            elif default_value is not None:  

                self.widget.children[0].value = str(default_value) 

            else:

                self.widget.children[0].value = None

            
            self.initial = False

        children = [label, self.widget]
        super().__init__(children=children)
        
    def get_value(self):
        
        return self.widget.children[-1].value


class ParamSetterWidget(VBox):

    def __init__(self, name, widget, default_value=None, preset_value=None, widget_initialized=None, param_setter_event=None):

        # this widget already exists

        if not isinstance(VBox, MetaHasTraits):

            return

        self.name = name
        self.type = 'param_setter'

        self.initial = not widget_initialized
        self.param_setter_event = param_setter_event

        # This is just label for this widget. The values are actually being
        # set on different widgets.
        if default_value:
            label = widgets.HTML(f"<b><font size=2 color='blue'>{self.name}</b>")
        else:
            label = widgets.HTML(f"<b><font size=2 color='black'>{self.name}</b>")

        self.widget = widget

        if self.initial or self.param_setter_event.isSet() :  # So that user input is not overwritten every time.

            if preset_value is not None:  # So that preset values take precedence over default values.
                # the widget is now VBox
                self.widget.children[-1].value = str(preset_value) 
                
            elif default_value is not None:  
                self.widget.children[-1].value = str(default_value) 
                
            self.initial = False

      
        children = [label, self.widget]
        super().__init__(children=children)


class ParamBooleanWidget(VBox):
    
    def __init__(self, name, default_value=None, preset_value=None, optional=False, widget=None, widget_initialized=None, param_setter_event=None):
        
        if not isinstance(VBox, MetaHasTraits):
            return

        self.name = name
        self.type = 'boolean'
        
        self.initial = not widget_initialized
        self.param_setter_event = param_setter_event
        
        if preset_value:
            label = widgets.HTML(f"<b><font size=2 color='blue'>{self.name}</b>")
        elif optional:
            label = widgets.HTML(f"<b><font size=2 color='grey'>{self.name}</b>")
        else:
            label = widgets.HTML(f"<b><font size=2 color='black'>{self.name}</b>")
            
        if widget:
            self.widget = widget
        else:
            self.widget =  VBox([widgets.Checkbox(
                value=False,
                description='True',
                disabled=False,
                indent=False
            )])
            
        if self.initial or self.param_setter_event.isSet() :  # So that user input is not overwritten every time.

            if preset_value is not None:  # So that preset values take precedence over default values.
            
                self.widget.children[0].value = bool(preset_value)
                
            elif default_value is not None:  

                self.widget.children[0].value = bool(default_value)

            else:

                self.widget.children[0].value = False

            
            self.initial = False

        children = [label, self.widget]
        super().__init__(children=children)
        
    def get_value(self):
        
        return self.widget.children[-1].value



        
class Custom1(VBox):
    
    def __init__(self):

        if not isinstance(VBox, MetaHasTraits):

            return

        self.name = 'custom1'
        self.type = 'custom'
        
        layout = {'width': '600px'}
        style = {'description_width': 'initial'}

        w1=widgets.IntRangeSlider(
            value=[10, 150],
            min=0,
            max=300,
            step=1,
            description='Regs search range:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            layout=layout,
            style=style
        )

        layout = {'width': '150px'}
        style = {'description_width': 'initial'}
        w2=widgets.Dropdown(
            options=[str(elem) for elem in list(range(1, 10))],
            value='1',
            description='Search gaps:',
            disabled=False,
            layout=layout
        )


        layout = {'width': '600px'}
        style = {'description_width': 'initial'}

        w3=widgets.IntRangeSlider(
            value=[5, 60],
            min=0,
            max=120,
            step=1,
            description='Days search range:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            layout=layout,
            style=style
        )

        layout = {'width': '150px'}
        style = {'description_width': 'initial'}
        w4=widgets.Dropdown(
            options=[str(elem) for elem in list(range(1, 10))],
            value='1',
            description='Search gaps:',
            disabled=False,
            layout=layout
        )
        
        h1 = HBox([w1, w2])
        h2 = HBox([w3, w4])

        label = widgets.HTML(f"<b><font size=2 color='black'>{'search_space'}</b>")     
        
        children = [label, h1, h2]
        super().__init__(children=children)
        
    def get_value(self):
        
        region_range = self.children[0].children[0].value
        region_jump = self.children[0].children[1].value

        day_range = self.children[1].children[0].value
        day_jump = self.children[1].children[1].value
        
        d = {'num_days': list(range(*day_range, int(day_jump))),
             'num_regions': list(range(*region_range, int(region_jump)))}
        
        return d
       

