from ..tree.tree_node import TreeNode
from ..tree.tree_builder import display_tree
from ..widgets.dynamic_widgets import DynamicWidget

try:

    from IPython.display import display
    import ipywidgets as widgets
    from ipywidgets import HBox, Label, VBox
    from ipywidgets import Button, Layout, HTML

    module_found = True

except ModuleNotFoundError:

    module_found = False

from collections import defaultdict
from threading import Event


class AccessObject():
    """Creates the DynamicWidgets based on the input tree.
    """
    
    def __init__(self, root, node_dicts):

        self.initial_event = Event()
        param_setter_event = Event()

        self.module_found = module_found

        if not self.module_found:
            return
        
        self.root, self.node_dicts = root, node_dicts
        self.widget_dicts = defaultdict(dict)
        self.widget_nodes = defaultdict(dict)  # this should replace widget_dicts, so we don't have duplicates

        # we don't have duplicates they are the same objects.
        self.param_vboxes = {}

        for topic in self.root.children:

            param_widgets = []

            for param in topic.children:

                param_widget = DynamicWidget(topic.name, param, self.widget_dicts, self.widget_nodes, self.initial_event, param_setter_event)

                param_widgets.append(param_widget)

            param_vbox = VBox(param_widgets)

            self.param_vboxes[topic.name] = param_vbox

        self.initial_event.set()

    def display_tree(self):

        display_tree(self.root)

    def get_topics(self):
    
        return self.root.get_children_names()

    def get_params(self, topic=None):

        if topic:
    
            return list(self.widget_dicts[topic].keys())

        else:

            l = []
            self._find_params(self.root, l)

            return l


    def get_effective_params(self, topic=None):

        effective_params = []

        params = self.get_params(topic)

        for param in params:

            

            widget_type = self.widget_nodes[topic][param].type

            if widget_type=='text':

                if not self.get_value(param, topic) == '':

                    effective_params.append(param)

            elif widget_type=='choice':

                if not self.get_value(param, topic) is None:

                    effective_params.append(param)

            elif widget_type=='boolean':

                effective_params.append(param)

        return effective_params

    def _find_params(self, node, l):

        depth = node.depth
        node_type = node.primary_type
        node_name = node.name

        if node_type != 'root':

            if node_type == 'topic':

                depth += 1
                
            if node_type in ['param', 'optional']:
                
                if node_name not in l:
                    l.append(node_name)

        for child in node.children:

            self._find_params(child, l)

    def get_value(self, param, topic=None):
        """This will return the string casted user input values. We will not
        cast this value to the castable type since the access_object is meant
        for the internal uses only. All widget values are internally treated
        as strings, so we will keep it that way.

        The returned values will be casted into castable types in the class
        decorator just before the values are returned to the user.
        """
        return self.get_widget(param, topic).value

    def set_value(self, value, param, topic=None):


        widget_type = self.get_widget_node(param, topic).type

        if widget_type=='boolean':
            self.get_widget(param, topic).value = eval(value)

        else:
            self.get_widget(param, topic).value = str(value)            


    def get_vbox(self, topic):
        
        return self.param_vboxes[topic]

    def get_widget_node(self, param, topic=None):

        # return self.widget_nodes[topic][param]


        if topic:


            
            
            try:
                return self.widget_nodes[topic][param]
            except:
                pass
            
                print(param, topic, '=====')
                print(self.widget_dicts, '+++++')
        
        else:
            
            params = []
            topics = []
            
            for topic, param_dict in self.widget_nodes.items():
            
                if param in param_dict:
                    
                    params.append(param_dict[param])
                    topics.append(topic)
                    
            if len(params) > 1:
                
                raise TypeError('Specify the topic!', topics)

        return params[0]
    
    def get_widget(self, param, topic=None):

        if '/' in param:
            topic, param = param.split('/')
        
        if topic:


            
            
            try:
                return self.widget_dicts[topic][param].children[-1]
            except:
                pass
            
                print(param, topic, '=====')
                print(self.widget_dicts, '+++++')
        
        else:
            
            params = []
            topics = []
            
            for topic, param_dict in self.widget_dicts.items():
            
                if param in param_dict:
                    
                    params.append(param_dict[param])
                    topics.append(topic)
                    
            if len(params) > 1:
                
                raise TypeError('Specify the topic!', topics)

            
                
            return params[0].children[-1]
        
    def get_node(self, node, topic=None):
        
        if topic:
            
            return self.node_dicts[topic][node]
        
        else:
            
            nodes = []
            topics = []
            
            for topic, node_dict in self.node_dicts.items():
                
                if node in node_dict:
                    
                    nodes.append(node_dict[node])
                    topics.append(topic)
                    
            if len(nodes) > 1:
                
                raise TypeError('Specify the topic!', topics)
                    
            if len(nodes)==0:
                return None
                    
            return nodes[0]

    def node_exists(self, node, topic=None):

        node = self.get_node(node, topic)

        if node is None:
            return False
        else:
            return True

    def get_active_param_values(self):
    
        dsl_gen = [""]

        added_params = []

        for topic in self.root.children:

            if topic.name not in self.topic_choice_widget.value:
                continue

            dsl_gen[0] += "{}\n".format(topic.name)

            for param in topic.children:  # genesis params

                self._follow_branch(param, topic, dsl_gen, added_params)

            if len(added_params)==0:

                dsl = dsl_gen[0][0:-1]
                dsl_gen[0] = '\n'.join(dsl.split('\n')[0:-1])

            dsl_gen[0] += "\n"
                
        return dsl_gen[0][0:-2]

    def _follow_branch(self, param, topic, dsl_gen, added_params):
        """Notice the similarity to _add_widgets method in DynamicWidget
        class
        """
        
        input_value = self.get_value(param.name, topic.name)

        if param.name in self.widget_nodes[topic.name]:  # For the topic/param names

            widget_type = self.widget_nodes[topic.name][param.name].type

        else:

            widget_type = None

        if widget_type=='text':

            if not input_value == '':

                dsl_gen[0] += "-{}:{}\n".format(param.name, input_value)
                added_params.append(param.name)

        elif widget_type=='choice':

            if not input_value is None:

                dsl_gen[0] += "-{}:{}\n".format(param.name, input_value)
                added_params.append(param.name)

        elif widget_type=='boolean':

            dsl_gen[0] += "-{}:{}\n".format(param.name, input_value)
            added_params.append(param.name)

        for child_node in param.children:  # Since this is choice param, child_nodes are all options
            
            if child_node.name==input_value:
                
                for _child_node in child_node.children:
                    
                    self._follow_branch(_child_node, topic, dsl_gen, added_params)

