import inspect
import functools

def ArgtellerMethodDecorator(source_name, topic=None):
    
    def decorator(func):

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):

            original_signature = inspect.signature(func)
            
            new_args = []
    
            params = list(original_signature.parameters.values())
            
            has_VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL in [param.kind for param in params]
            has_VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD in [param.kind for param in params]
            
            if source_name in kwargs:
                
                __source_obj__ = kwargs[source_name]
                
                __source_obj__.__settopic__(topic)
                
                del kwargs[source_name]
                
            else:
                
                __source_obj__ = None

            missing_positional_arguments = []
            
            num_hard_pos = 0
            num_pos = 0
                
            for i, param in enumerate(params):      
                
                if i==0:  # Skip the implicit self argument.
                    continue
 
                if param.kind==inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    
                    # Keep track of the number of positional arguments to check
                    # excessive argument input error.
                    if param.default==inspect._empty:
                        num_hard_pos += 1
                    num_pos += 1
                    
                    # We can assume that the first args belong to the
                    # position argument list.
                    if len(args)>=i:
                        
                        new_args.append(args[i-1])

                        # new_args.append(args.pop(0))
                    
                    elif param.name in kwargs:
                        
                        # new_args.append(kwargs[param.name])
                        # del kwargs[param.name]
                        pass  # just keep it there
                        
                    else:
                        
                        if __source_obj__ is not None:
                        
                            if param.name in __source_obj__.__getparams__():

                                kwargs[param.name] = __source_obj__.__getvalue__(param.name)

                                # new_args.append(__source_obj__.__getvalue__(param.name))

                        else:
                            
                            if param.default==inspect._empty:
                                
                                missing_positional_arguments.append("'{}'".format(param.name))
                            
                            # new_args.append(param.default)

                            kwargs[param.name] = param.default
                            
            if not has_VAR_POSITIONAL and num_pos < len(args):
                
                # Add 1 for the implicit self argument.
                if num_hard_pos > 0:
                    
                    raise TypeError("__init__() takes {} positional arguments but {} were given".format(
                        num_pos+1, len(args)+1))
                    
                else:
                    
                    raise TypeError("__init__() takes from {} to {} positional arguments but {} were given".format(
                        num_hard_pos+1, num_pos+1, len(args)+1))

            elif has_VAR_POSITIONAL and num_pos < len(args):

                new_args += args[num_pos:]

            if len(missing_positional_arguments) > 0:

                missing_args = " and ".join(missing_positional_arguments)

                raise TypeError("__init__() missing {} required positional arguments: {} !".format(len(missing_positional_arguments), missing_args))
                        
            cr = func(self, *new_args, **kwargs) # call original function

            if __source_obj__ is not None:
                
                __source_obj__.__resettopic__()  # release the topic binding

            return cr

        return wrapper
    
    return decorator
