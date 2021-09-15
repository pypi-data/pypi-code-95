
from .logger import Logger
from .exceptions import DSOException


def clean_directory(path):
    for path in Path(path).glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)




# def merge_dicts(source, destination):
#     if not source: return destination
#     for key, value in source.items():
#         if isinstance(value, dict):
#             if key in destination.keys():
#                 if not isinstance(destination[key], dict):
#                     raise Exception(f"Failed to merge '{key}' beacuse destination has an existing key with incompatible type ({type(destination[key])}) to that of the source ({type(source[key])}).")
#             else:
#                 destination[key] = {}
#             node = destination[key]
#             merge_dicts(value, node)
#         else:
#             destination[key] = value

#     return destination


# def merge_dicts(source: dict, destination: dict, merge_key=None):
    
#     if not isinstance(source, dict) or not isinstance(destination, dict):
#         raise Exception("Failed to merge, 'dict' type is expected for source and destination.")

#     def find_item(item, alist, merge_key=None):
#         if merge_key:
#             if callable(merge_key):
#                 found = [x for x in alist if merge_key(x) == merge_key(item)]
#             else:
#                 if isinstance(item, dict) and merge_key in item:
#                     found = [x for x in alist if x[merge_key] == item[merge_key]]
#                 else:
#                     found = [x for x in alist if x == item]
#         else:
#             found = [x for x in alist if x == item]

#         return found[0] if found else None

#     if not source: return destination
    
#     for key, value in source.items():
#         if isinstance(value, dict):
#             if key in destination.keys():
#                 if not isinstance(destination[key], dict):
#                     raise Exception(f"Failed to merge '{key}' beacuse destination has an existing key with incompatible type ({type(destination[key])}) to that of the source ({type(source[key])}).")
#             else:
#                 destination[key] = {}
#             node = destination[key]
#             merge_dicts(value, node, merge_key)
#         elif isinstance(value, list):
#             if key in destination.keys():
#                 if not isinstance(destination[key], list):
#                     raise Exception(f"Failed to merge '{key}' beacuse destination has an existing key with incompatible type ({type(destination[key])}) to that of the source ({type(source[key])}).")
#             else:
#                 destination[key] = []
#             for item in value:
#                 if not isinstance(item, dict):

#                 node = find_item(item, destination[key], merge_key)
#                 if node:
#                     if isinstance(node, dict):
#                         if not isinstance(item, dict):
#                             raise Exception("Failed to merge. Destination has an existing key with incompatible type.")
#                         merge_dicts(item, node, merge_key)
#                     else:
#                         if destination[key].index(item) < 0:
#                             destination[key].append(item)
#                 else:
#                     destination[key].append(item)
#         # elif isinstance(value, tuple):
#         #     raise NotImplementedError
#         # elif isinstance(value, set):
#         #     raise NotImplementedError
#         else:
#             destination[key] = value

#     return destination


def merge_dicts(source, destination, merge_key=None):
    
    def find_item(item, alist, merge_key=None):
        found = None
        if merge_key:
            if callable(merge_key):
                for x in alist:
                    if merge_key(x) == merge_key(item):
                        found = x
                        break
                # found = [x for x in alist if merge_key(x) == merge_key(item)]
            else:
                if isinstance(item, dict) and merge_key in item:
                    for x in alist:
                        if isinstance(x, dict) and merge_key in x and x[merge_key] == item[merge_key]:
                            found = x
                            break
                    # found = [x for x in alist if merge_key in x and x[merge_key] == item[merge_key]]
                else:
                    for x in alist:
                        if x == item:
                            found = x
                            break
                    # found = [x for x in alist if x == item]
        else:
            for x in alist:
                if x == item:
                    found = x
                    break

        return found

    if not source: return destination

    if not type(source) == type(destination):
        raise Exception("Failed to merge, source and destination must be of the same type.")

    if isinstance(source, dict):
        for key, value in source.items():
            if isinstance(value, dict) or isinstance(value, list) or isinstance(value, tuple):
                if not key in destination.keys(): destination[key] = type(value)()
                node = destination[key]
                merge_dicts(value, node, merge_key)
            else:
                destination[key] = value

    elif isinstance(source, list):
        for item in source:
            node = find_item(item, destination, merge_key)
            if node:
                if isinstance(node, dict) or isinstance(node, list) or isinstance(source, tuple):
                    merge_dicts(item, node, merge_key)
            else:
                destination.append(item)
    else:
        raise NotImplementedError


    return destination



def flatten_dict(input, prefixed_key = '', delimiter = '.'):
    def visit(input, prefixed_key, delimiter, output):
        if isinstance(input, dict):
            for key, value in input.items():
                new_key = f"{prefixed_key}{delimiter}{key}" if prefixed_key else f"{key}"
                visit(value, new_key, delimiter, output)
        elif isinstance(input, list):
            for idx, item in enumerate(input):
                visit(item, f"{prefixed_key}{delimiter}{idx}", delimiter, output)
        else:
            output[prefixed_key] = input

        return output

    return visit(input, prefixed_key, delimiter, {})



def deflatten_dict(input: dict, delimiter = '.'):
    data = {}
    for key, value in input.items():
        set_dict_value(data, key.split(delimiter), value, overwrite_parent=True, overwrite_children=True)
    return data



def get_dict_item(dic, keys, create=True):
    for i in range(0, len(keys)):
        key = keys[i]
        if isinstance(dic, dict):
            if not key in dic.keys():
                if create:
                    dic[key] = {}
                else:
                    return None
            dic = dic[key]
        elif isinstance(dic, list):
            raise DSOException("Lists items are not allowed '{0}'. Must be converted to dictionary.".format('.'.join(keys[0:i])))
        else:
            return None
    return dic
    



def set_dict_value(dic, keys, value, overwrite_parent=False, overwrite_children=False):
    parent_item = get_dict_item(dic, keys[:-1])
    lastKey = keys[-1]
    ### parent item is expected to be a dictionary
    if not isinstance(parent_item, dict):
        if overwrite_parent:
            grand_parent_item = get_dict_item(dic, keys[:-2])
            grand_parent_item[keys[-2]] = {}
            parent_item = grand_parent_item[keys[-2]]
            Logger.warn("'{0}' was overwritten by '{1}.".format('.'.join(keys[:-1]),'.'.join(keys)))
        else:
            raise DSOException("Failed to set '{0}' becasue it would overwrite parent item '{1}' which is not a dictionary but of type '{2}'.".format('.'.join(keys), '.'.join(keys[:-1]), type(parent_item)))
    if lastKey in parent_item.keys():
        ### item is expected to be a basic type (string, number, ...)
        if isinstance(parent_item[lastKey], dict) or isinstance(parent_item[lastKey], list) or isinstance(parent_item[lastKey], set) or isinstance(parent_item[lastKey], tuple):
            if overwrite_children:
                Logger.warn("'{0}' was overwritten.".format('.'.join(keys)))
            else:
                raise DSOException("Failed to set '{0}' becasue it would overwrite an existing item of type '{1}'.".format('.'.join(keys), type(parent_item)))
    parent_item[lastKey] = value



def del_dict_item(dic, keys):
    item = get_dict_item(dic, keys[:-1], create=False)
    if not item or not keys[-1] in item:
        return False

    if isinstance(item[keys[-1]], dict):
        raise DSOException("'{0}' is a non-empty namespace and cannot be deleted.".format('.'.join(keys)))

    item.pop(keys[-1])
    return True



def del_dict_empty_item(dic, keys):
    if not dic: return
    item = get_dict_item(dic, keys)
    if not item:
        item = get_dict_item(dic, keys[:-1])
        item.pop(keys[-1])
        del_dict_empty_item(dic, keys[:-1])



def is_binary_file(filename):
    """ 
    Return true if the given filename appears to be binary.
    File is considered to be binary if it contains a NULL byte.
    FIXME: This approach incorrectly reports UTF-16 as binary.
    """
    with open(filename, 'rb') as f:
        for block in f:
            if b'\0' in block:
                return True
    return False




