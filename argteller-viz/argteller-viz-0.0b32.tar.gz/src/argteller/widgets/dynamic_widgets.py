from .widgets import ParamChoiceWidget
from .widgets import ParamBooleanWidget
from .widgets import Custom1
from .widgets import ParamTextWidget
from .widgets import ParamSetterWidget

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


class DynamicWidget(VBox):
    # https://stackoverflow.com/questions/60998665/is-it-possible-to-make-another-ipywidgets-widget-appear-based-on-dropdown-select
    
    def __init__(self, topic, node, widget_dicts, widget_nodes, initial_event, param_setter_event, gui_triggered=False):

        if not isinstance(VBox, MetaHasTraits):
            return
        
        self.initial_event = initial_event

        self.currently_param_setter = False
        self.param_setter_event = param_setter_event

        self.topic = topic
        self.node = node
        
        self.widget_dicts = widget_dicts
        self.widget_nodes = widget_nodes

        default_value = None
        preset_value = None

        if node.primary_type=='param' or node.primary_type=='optional' or node.primary_type=='alien':

            is_optional_param = node.primary_type=='optional'

            # Set aside the default and preset values
            default_value = node.default_value
            preset_value = node.preset_value

            # if choiceable param, add choices here
            if node.secondary_type=='option':
                
                options = node.get_children_names() 

                if self.node.name in self.widget_dicts[self.topic]:

                    widget = self.widget_dicts[self.topic][self.node.name]

                    self.widget = ParamChoiceWidget(
                        name=self.node.name, 
                        options=options, 
                        default_value=default_value, 
                        preset_value=preset_value, 
                        widget=widget,
                        optional=is_optional_param,
                        widget_initialized=True,
                        param_setter_event=self.param_setter_event)

                else:
                    
                    self.widget = ParamChoiceWidget(
                        name=self.node.name, 
                        options=options, 
                        default_value=default_value, 
                        preset_value=preset_value, 
                        optional=is_optional_param,
                        widget_initialized=False,
                        param_setter_event=self.param_setter_event)
                    
                    self.widget_dicts[self.topic][self.node.name] = self.widget.widget
                    self.widget_nodes[self.topic][self.node.name] = self.widget

            elif node.secondary_type=='boolean':

                if self.node.name in self.widget_dicts[self.topic]:

                    widget = self.widget_dicts[self.topic][self.node.name]

                    self.widget = ParamBooleanWidget(
                        name=self.node.name, 
                        default_value=default_value, 
                        preset_value=preset_value, 
                        widget=widget,
                        optional=is_optional_param,
                        widget_initialized=True,
                        param_setter_event=self.param_setter_event)

                else:
                    
                    self.widget = ParamBooleanWidget(
                        name=self.node.name, 
                        default_value=default_value, 
                        preset_value=preset_value, 
                        optional=is_optional_param,
                        widget_initialized=False,
                        param_setter_event=self.param_setter_event)
                    
                    self.widget_dicts[self.topic][self.node.name] = self.widget.widget
                    self.widget_nodes[self.topic][self.node.name] = self.widget
                   
            elif node.secondary_type=='string':

                if self.node.name in self.widget_dicts[self.topic]:

                    widget = self.widget_dicts[self.topic][self.node.name]

                    self.widget = ParamTextWidget(
                        name=self.node.name, 
                        default_value=default_value,
                        preset_value=preset_value,
                        optional=is_optional_param, 
                        widget=widget,
                        widget_initialized=True,
                        param_setter_event=self.param_setter_event,
                        set_from=self.node.set_from)

                else:
                
                    self.widget = ParamTextWidget(
                        name=self.node.name, 
                        default_value=default_value,
                        preset_value=preset_value,
                        optional=is_optional_param,
                        widget_initialized=False,
                        param_setter_event=self.param_setter_event,
                        set_from=self.node.set_from)
                    
                    self.widget_dicts[self.topic][self.node.name] = self.widget.widget
                    self.widget_nodes[self.topic][self.node.name] = self.widget
                   
            elif node.secondary_type=='string_sample':

                if self.node.name in self.widget_dicts[self.topic]:

                    widget = self.widget_dicts[self.topic][self.node.name]

                    self.widget = ParamTextWidget(
                        name=self.node.name, 
                        default_value=default_value,
                        preset_value=preset_value,
                        optional=is_optional_param, 
                        widget=widget,
                        widget_initialized=True,
                        param_setter_event=self.param_setter_event)

                else:
                
                    string_sample_node = node.children[0]
                    string_sample = string_sample_node.name
                    
                    self.widget = ParamTextWidget(
                        name=self.node.name, 
                        example=string_sample, 
                        default_value=default_value,
                        preset_value=preset_value,
                        optional=is_optional_param, 
                        widget_initialized=False,
                        param_setter_event=self.param_setter_event)
                    
                    self.widget_dicts[self.topic][self.node.name] = self.widget.widget
                    self.widget_nodes[self.topic][self.node.name] = self.widget
                
        elif node.primary_type=='custom1':
            
            self.widget = Custom1()
            
            self.widget_dicts[self.topic][self.node.name] = 'custom1'
            self.widget_nodes[self.topic][self.node.name] = self.widget

        elif node.primary_type=='param_setter':

            topic, node_name = node.name.split('/')

            # node_name is some node that already exists in some other topic

            widget = self.widget_dicts[topic][node_name]

            # recall that widget that already exists

            self.param_setter_event.set()  # set the event here so that the param setter widget can use it

            self.widget = ParamSetterWidget(
                name=self.node.name, 
                widget=widget, 
                default_value=self.node.default_value,
                preset_value=preset_value,
                widget_initialized=False,
                param_setter_event=self.param_setter_event)

            self.currently_param_setter = True
            
        self.dynamic_widget_holder = VBox()
        
        children = [
            self.widget, 
            self.dynamic_widget_holder
        ]

        
        self.widget.children[1].children[-1].observe(self._add_widgets, names=['value'])

        super().__init__(children=children)

        # Manually trigger the children widget node initialization if there
        # is default or preset value

        branching = node.primary_type=='param' or node.primary_type=='optional'
        value_presetting = default_value or preset_value
        initial_event = not self.initial_event.isSet()

        if (branching and value_presetting and initial_event):
            child_node = self.node.get_child_by_name(preset_value)

            new_widgets = []

            if self.node.secondary_type=='boolean':

                for child_node in self.node.children:

                    widget = DynamicWidget(self.topic, child_node, self.widget_dicts, self.widget_nodes, self.initial_event, self.param_setter_event,
                        gui_triggered=False)
                    new_widgets.append(widget)


            else:
            
                for child_node in self.node.children:

                    # This is so that if the default value and preset value were different,
                    # the widgets do not follow down both of the branches.
                    if preset_value is not None:
                        checked_value = preset_value
                    elif default_value is not None:
                        checked_value = default_value
                    else:
                        checked_value = None
                    
                    if child_node.name==checked_value and (child_node.secondary_type=='param' or child_node.secondary_type=='param_setter'):
                        
                        for _child_node in child_node.children:
                        
                            widget = DynamicWidget(self.topic, _child_node, self.widget_dicts, self.widget_nodes, self.initial_event, self.param_setter_event)
                            new_widgets.append(widget)
            
            self.dynamic_widget_holder.children = tuple(new_widgets)

        # Follow through the branching at the gui event trigger.
        elif branching and gui_triggered:

            new_widgets = []

            for child_node in self.node.children:

                if (child_node.secondary_type=='param' or child_node.secondary_type=='param_setter'):

                    if child_node.name==self.widget.get_value():

                        for _child_node in child_node.children:

                            widget = DynamicWidget(self.topic, _child_node, self.widget_dicts, self.widget_nodes, self.initial_event, self.param_setter_event)
                            new_widgets.append(widget)


            self.dynamic_widget_holder.children = tuple(new_widgets)

    def _add_widgets(self, widg):
        
        # if node is choiceable param
        # and if any of the choice node has param nodes
        
        # check the choice of current widget
        # and that choice has value1
        
        # look at the choice param value1, and see if that has any children
        # then loop over those children and add them all to the new_widgets

        input_value = widg['new']  # The picked option for choice param

        child_node = self.node.get_child_by_name(input_value)



        new_widgets = []


        if self.node.secondary_type=='boolean':

            if input_value == True:

                for child_node in self.node.children:

                    widget = DynamicWidget(self.topic, child_node, self.widget_dicts, self.widget_nodes, self.initial_event, self.param_setter_event,
                        gui_triggered=True)
                    new_widgets.append(widget)


        else:
            
            for child_node in self.node.children:  # Since this is choice param, child_nodes are all options
                
                if child_node.name==input_value and (child_node.secondary_type=='param' or child_node.secondary_type=='param_setter'):

                    # If the child_node.name == option 
                    # and if that child_node (option) is "branching", 
                    
                    for _child_node in child_node.children:

                        # the children of that child_node are all param or param_setters

                        # if _child_node is param setter,
                        
                        # create new dynamicwidgets for each of those
                        widget = DynamicWidget(self.topic, _child_node, self.widget_dicts, self.widget_nodes, self.initial_event, self.param_setter_event,
                            gui_triggered=True)
                        new_widgets.append(widget)
        
        self.dynamic_widget_holder.children = tuple(new_widgets)

        if self.currently_param_setter:
            self.param_setter_event.clear()

    def set_input(self, key, value):
         
        self.recur(self, key, value)

    def recur(self, node, key, value):

        if not (isinstance(node, widgets.widget_box.VBox) or 
                isinstance(node, DynamicWidget)):
            return

        if isinstance(node, DynamicWidget):

            if key in node.widget_dicts:

                node.widget_dicts[key].value = str(value)

        for child in node.children:

            self.recur(child, key, value)

