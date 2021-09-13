from ..tree.tree_parser import parse_dsl
from ..tree.tree_builder import construct_tree
from ..tree.tree_builder import merge_with_preset_tree
from ..builder.access_object import AccessObject
from ..builder.get_control_panel import get_control_panel

try:
    
    from IPython.display import display

except ModuleNotFoundError:

    pass

import inspect
import os
import warnings
import time
import glob


TEMP_FILENAME = '__tmpdsl__.txt'



class ArgtellerClassDecorator():
    
    def __init__(self, dsl, override=False):
        
        if os.path.exists(dsl):
            with open(dsl) as f:
                self.dsl = f.read()

        elif isinstance(dsl, str):
            self.dsl = dsl
            
        self.override = override
        
    def __call__(self, cls):
        
        class Wrapped(cls):
            
            def __init__(cls_self, *args, **kwargs):

                args = list(args)

                parsed_node_data = parse_dsl(self.dsl)
                root, node_dicts, value_dicts = construct_tree(parsed_node_data)

                # Instantiate the temporary AccessObject to check the keyword arguments.
                temp_access_object = AccessObject(root, node_dicts)

                # Instantiate the AccessObject early so that we can
                # 1) catch the unexpected keyword arguments without having to cache them, and
                # 2) directly feed in the relevant POSITIONAL_OR_KEYWORD into the preset tree.


                # The original signature of the class being decorated.
                original_signature = inspect.signature(cls.__init__)
                
                params = list(original_signature.parameters.values())
                
                param_names = [param.name for param in params]  # The names of the params found in signature
                param_types = [param.kind for param in params]  # The parameter types
                
                # Because the inner __init__ method signature only consists
                # of VAR_POSITIONAL and VAR_KEYWORD type parameter, we need
                # to check manually.

                has_VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL in param_types
                has_VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD in param_types

                
                # If VAR_KEYWORD type parameter (e.g. **kwargs) is not in the original_signature,
                # we cannot accept kwargs not in the param_names or not in the access_object.
                if not has_VAR_KEYWORD:
                    
                    for key, value in kwargs.items():

                        if key=='__dsl__':
                            # But if that key is __dsl__, forgive that.
                            pass
                    
                        elif not key in param_names:

                            if temp_access_object.node_exists(key):
                                # If the key exists in the param list, forgive that.
                                pass

                            else:
                                raise TypeError("__init__() got an unexpected keyword argument '{}'!".format(
                                    key))
                # This checking may not be necessary anymore since we call super __init__ now.


                # The below code is commented out because we call super __init__ now.
                # if not inspect.Parameter.VAR_POSITIONAL in param_types:
                    
                #     num_pos_or_kw = len([param_type for param_type in param_types if
                #                          param_type==inspect.Parameter.POSITIONAL_OR_KEYWORD])
                    
                #     if len(args) > num_pos_or_kw - 1:  # -1 for the implicit "self" argument
                        
                #         raise TypeError("__init__() takes {} positional arguments but {} were given!".format(
                #             num_pos_or_kw, len(args) + 1))  # +1 to count for the implicit self argument
                
    
                signature_arg_preset_dict = dict()

                # Inspect the user passed arguments at the __init__ method invocation.
                check_pos_args = []
                
                for i, param in enumerate(params):
                    
                    if i==0:  # Skip the implicit "self" argument.
                        continue
                    
                    # The parameter in signature is "named"
                    if param.kind==inspect.Parameter.POSITIONAL_OR_KEYWORD:   
                        
                        if len(args)>=i:

                            arg_value = args[i-1]

                            # Set the attribute only if the param is not in the tree.
                            # setattr(cls_self, param.name, arg_value)

                            # Else, record it, and directly inject into preset tree
                            
                        elif param.name in kwargs:
                            
                            setattr(cls_self, param.name, kwargs[param.name])
                            # del kwargs[param.name]
                            
                        else:
                            
                            if param.default==inspect._empty:  
                            # If we find a unsupplied named arg, we check if there is a chance
                            # it will be supplied by the tree

                                if temp_access_object.node_exists(param.name):

                                    args.append(None)

                                
                            
                                check_pos_args.append(param.name)
                            
                            # The Method decorator will source from the source
                            # object here. But for Class decorator, because the 
                            # widgets are dynamic, we cannot do that.
                            
                            # We will only check to see if the missing argument
                            # is at least found in the widget param namespace.

                    elif param.kind==inspect.Parameter.VAR_POSITIONAL:
                        pass

                        
                        
                # The Method decorator can check the missing_positional_arguments
                # to throw TypeError missing argument exception. But with the 
                # Class decorator, we cannot do that because we are waiting on the
                # user to interact with the widget. 
                # So instead, we will rely on the requirement signals of the widgets.

                

                # we want, for those params that exist in the tree, merge them into the 
                # preset tree
                # They can be either: 
                # 1) found in the params (we checked this above)
                # 2) found in the kwargs
                

                
                in_tree = []

                # List of keyword args found in the tree.
                for k, v in kwargs.items():

                    if temp_access_object.node_exists(k):

                        in_tree.append(k)

                # Add those to the preset dict.
                for k in in_tree:

                    signature_arg_preset_dict[k] = kwargs[k]

                    # If the k in kwargs is not in the signature
                    # and if VAR_KEYWORD type parameter is not part of signature:
                    if k not in param_names and not has_VAR_KEYWORD:

                        # then delete this key so that we don't get the unexpected keyword 
                        # argument exception.
                        del kwargs[k]




                if '__dsl__' in kwargs:

                    parsed_node_preset_data = parse_dsl(preset_dsl)
                    preset_root, preset_node_dicts, preset_value_dicts = construct_tree(parsed_node_preset_data)

                    del kwargs['__dsl__']

                    merge_with_preset_tree(root, preset_value_dicts)


                # Instantiate the AccessObject object
                # Inject it into the module global namespace to avoid infinite recursion
                # at the setattr method
                global __access_object__
                __access_object__ = AccessObject(root, node_dicts)



                for k, v in signature_arg_preset_dict.items():

                    __access_object__.set_value(str(v), k)

                if __access_object__.module_found:

                    cls_self.__control_panel__ = get_control_panel(__access_object__)
                    display(cls_self.__control_panel__)
                
                    widget_params = __access_object__.get_params()
                    cls_self.topic = None

                else:

                    warnings.filterwarnings('always')

                    warnings.warn("Please install 'IPython' and 'ipywidgets' modules to enable widgets.", ImportWarning)

                    warnings.filterwarnings(action='ignore', category=DeprecationWarning, module='ipykernel')
                    
                    widget_params = []

                # Below missing positional arguments cannot be found in the widget param namespace.
                
                # missing_pos_args = []
                
                # for check_pos_arg in check_pos_args:
                    
                #     if check_pos_arg not in widget_params:
                        
                #         missing_pos_args.append("'{}'".format(check_pos_arg))
                        
                # if len(missing_pos_args) > 0:

                #     missing_args = " and ".join(missing_pos_args)

                #     raise TypeError("__init__() missing {} required positional arguments: {} !".format(
                #         len(missing_pos_args), missing_args))


                super(Wrapped, cls_self).__init__(*args, **kwargs)


            def __getattr__(cls_self, param):
                """This magic method is invoked when the __getattribute__ 
                magic method throws an exception. This is a natural way to
                query the widgets when the user has not supplied a required
                argument, or when the user queries for a parameter that is 
                not specified in the original signature.
                """
                if __access_object__.module_found and param in __access_object__.get_params():

                    return cls_self.__getvalue__(param)

                else:
                    
                    raise AttributeError("'{}' object has no attribute '{}'!".format(cls.__name__, param))

            def __setattr__(cls_self, param, value):

                if __access_object__.module_found and param in __access_object__.get_params():


                    topic_index = __access_object__.tab_widget.selected_index
                    titles = __access_object__.tab_widget._titles
                    current_topic = titles[str(topic_index)]

                    cls_self.__setvalue__(value, param, current_topic)
                    
                else:
                    super(Wrapped, cls_self).__setattr__(param, value)

                    
                
            def __settopic__(cls_self, topic):
                
                cls_self.topic = topic
                
            def __resettopic__(cls_self):
                
                cls_self.topic = None

            def __getparams__(cls_self):

                return __access_object__.get_effective_params(cls_self.topic)

            def __getvalue__(cls_self, param):
                """The return values will be automatically typecasted. 

                '' from Text widget will be None
                int castable values will be casted to int
                float castable values will be casted to float (assuming it was not int)
                """
                try:
                    value = __access_object__.get_value(param, cls_self.topic)
                except TypeError as e:
                    raise TypeError(str(e) + ' Invoke  obj.__settopic__(topic) method to set topic. Invoke obj.__resettopic__() to reset it.')

                if value is None:
                    return value

                if isinstance(value, bool):
                    return value

                try:    
                    value = int(value)
                    return value
                except ValueError:
                    pass
                
                try:
                    value = float(value)
                    return value
                except ValueError:
                    pass
                
                try:
                    value = eval(value)
                    return value
                except (SyntaxError, NameError):
                    pass

                if value=='':
                    return None
                
                return value

            def __setvalue__(cls_self, value, param, topic):

                __access_object__.set_value(str(value), param, topic)

            def get_dsl(cls_self):

                print(__access_object__.get_active_param_values())

            def __savedsl__(cls_self, filename):

                dsl = cls_self.get_dsl()
    
                if not '/' in filename:
                    
                    curdir = os.getcwd()
                    filename = os.path.join(curdir, filename)
                    
                elif not os.path.exists(os.path.dirname(filename)):
                    
                    raise FileNotFoundError('No such file or directory: {}'.format(
                        os.path.dirname(filename)))
                    
                    os.listdir(os.path.dirname(filename))
                    
                with open(filename, 'w') as f:
                    
                    f.write(dsl)
                
                return filename

            def load_dsl(cls_self, inp=None):

                # clear out the initial event to trigger recursive widget
                # activation
                __access_object__.initial_event.clear()

                if inp is None:

                    filename = __access_object__.filepath_widget.value

                    with open(filename, "r") as f:

                        dsl = f.read()

                elif os.path.exists(inp):

                    with open(inp, "r") as f:

                        dsl = f.read()

                else:

                    dsl = inp


                parsed_node_data = parse_dsl(dsl)
                _, _, value_dicts = construct_tree(parsed_node_data)

                for topic, param_dict in value_dicts.items():
    
                    for param, value in param_dict.items():
                        
                        
                        __access_object__.set_value(value, param, topic)


                __access_object__.initial_event.set()

            def __loadtmpdsl__(cls_self):

                dsl = None

                path = "*__tmpdsl__*.txt"

                for filename in glob.glob(path):

                    

                    
                    dsl = cls_self.__loaddsl__(filename)
                        
                    os.remove(filename)

                return dsl

            def __access_object__(cls_self):

                return __access_object__

        return Wrapped

