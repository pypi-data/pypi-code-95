import importlib
import warnings


class CommonHelper:
    def __init__(self):
        pass

    @staticmethod
    def read_target(target, keychain: tuple, default: any = None):
        if type(target) is dict:
            return CommonHelper.read_dictionary(target, keychain, default)
        elif type(target) is list or type(target) is tuple:
            return CommonHelper.read_array(target, keychain, default)
        else:
            return default

    @staticmethod
    def read_dictionary(dictionary: dict, keychain: tuple, default: any = None):
        if len(keychain) <= 0:
            return default
        elif len(keychain) == 1:
            return dictionary.get(keychain[0], default)
        else:
            current_key = keychain[0]
            if dictionary.keys().__contains__(current_key):
                sub_dictionary = dictionary.get(current_key, None)
                if type(sub_dictionary) is dict:
                    return CommonHelper.read_dictionary(sub_dictionary, keychain[1:], default)
                elif type(sub_dictionary) is tuple or type(sub_dictionary) is list:
                    return CommonHelper.read_array(sub_dictionary, keychain[1:], default)
                else:
                    return default
            else:
                return default

    @staticmethod
    def read_array(array: tuple, keychain: tuple, default: any = None):
        if len(keychain) <= 0:
            return default
        elif len(keychain) == 1:
            current_key = int(keychain[0])
            if len(array) > current_key:
                return array[int(keychain[0])]
            else:
                return default
        else:
            current_key = int(keychain[0])
            if len(array) > current_key:
                sub_array = array[current_key]
                if type(sub_array) is tuple or type(sub_array) is list:
                    return CommonHelper.read_array(sub_array, keychain[1:], default)
                elif type(sub_array) is dict:
                    return CommonHelper.read_dictionary(sub_array, keychain[1:], default)
                else:
                    return default
            else:
                return default

    @staticmethod
    def write_dictionary(target_dict: dict, keychain: tuple, value: any):
        keychain_length = len(keychain)
        if keychain_length > 1:
            current_key = keychain[0]
            current_target = target_dict.get(current_key)
            if type(current_target) is not dict:
                # Since 0.2.14
                # a great change: all non-dict-type entry would be cleared as an empty dict
                target_dict[current_key] = {}
            CommonHelper.write_dictionary(target_dict[current_key], keychain[1:], value)
        elif keychain_length == 1:
            target_dict[keychain[0]] = value

        return target_dict

    @staticmethod
    def class_with_class_path(module_path: str, class_name: str = None):
        """
        Since 0.1.22
        Since 0.2.19 When the class name is the same with PY file name, `class_name` is optional.

        For a/b.py -> class b
        class_with_namespace is like 'package.sub_package.class', 'a.b'
        class_name is 'b'
        return a CLASS definition, to be used with parameters to make instance
        """
        module = importlib.import_module(module_path)
        if class_name is None:
            class_name = module_path.split('.')[-1]
        a_class = getattr(module, class_name)
        return a_class

    @staticmethod
    def class_with_module_and_name(module_base: str, sub_module_name: str):
        """
        Since 0.1.21
        Since 0.2.19 It is not so convinence to use, consider using `class_with_class_path`.

        For a/b.py -> class b
        module_base is a
        sub_module_name is b
        """
        warnings.warn('Use `class_with_class_path` instead.')

        module = __import__(module_base)
        a_class = getattr(module, sub_module_name)
        return a_class
