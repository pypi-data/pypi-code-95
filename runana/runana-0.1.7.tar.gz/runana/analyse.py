from collections import deque
from math import isnan
from functools import partial
from os import path

from runana.read_numbers import ignored
from runana.run import cwd, get_subdirs
from runana.input_file_handling import read_input_files_f90nml, string_or_iterable, superset


def collecting_loop_recursive(dir_, read_func,
                              look_for_these=["hostname.txt"],
                              ignore_these=["ignore"]):
    """Collect information from runs.

    Recursively locate directories under `dir_` containing any of the
    files in `look_for_these`, but leaves out directories that contain
    any files in `ignore_these`. In each of the located directories the
    function `read_func` is run with no arguments (the working directory
    is temporarily changed to the located directory).

    """
    subdirs = get_subdirs(dir_)
    for subdir in subdirs or []:
        asubdir = path.join(dir_, subdir)
        if not any(path.exists(path.join(asubdir, fname)) for fname in ignore_these):
            if any(path.exists(path.join(asubdir, fname)) for fname in look_for_these):
                with cwd(asubdir):
                    value = read_func()
                yield (subdir, ), value
            else:
                for dirs, vals in collecting_loop_recursive(path.join(dir_, subdir),
                                                            read_func):
                    yield (subdir, )+dirs, vals


def read_input_files(workdir, indices=[], read_func=read_input_files_f90nml):
    """ Read information from input files.

    Recursively searches through all subdirectories of `workdir`.
    `read_func` is run in any directory containing a file named 'hostname.txt',
    and the result is stored in a :class:`ParamDict`, with the path in tuple-form
    as key. This :class:`ParamDict` is returned.

    If `indices` is given as a non-empty list, the indices in this argument
    will be used instead of recursive search

    Subdirectories of a directory with a 'hostname.txt' file are not searched.
    """
    paramdict = ParamDict()
    if indices:
        paramdict.from_list_of_indices(workdir, indices,
                                       read_func=read_func)
    else:
        paramdict.read(workdir, read_func=read_func)
    return paramdict


class ParamDict(dict):
    """ Dictionary that holds dictionaries of parameters """
    def read(self, workdir, read_func=read_input_files_f90nml):
        for index, result in collecting_loop_recursive(workdir, read_func):
            self[index] = result

    def from_list_of_indices(self, workdir, indices,
                             read_func=read_input_files_f90nml):
        for index in indices:
            with cwd(path.join(workdir, *index)):
                self[index] = read_func()

    def diff(self):
        """ Call :func:`dictdiff` on `ParamDict` object """
        dictdiff(self)

    def unpack_list_values(self):
        """ Takes any numerical parameter value in `ParamDict` object that is
        a list and packs it into individual slots with name numparam_name + idx

        Works in-place
        """
        for param_dict in self.values():
            spread_out_lists(param_dict)


def spread_out_lists(dict_):
    newdict = {}
    delete_keys = []
    for key, val in dict_.items():
        if isinstance(val, list):
            delete_keys += [key]
            for idx, elem in enumerate(val):
                if isinstance(key, tuple):
                    newkey = (key[0], str(key[1])+'_'+str(idx+1))
                else:
                    newkey = str(key)+'_'+str(idx+1)
                newdict[newkey] = elem
    dict_.update(newdict)
    for key in delete_keys:
        del dict_[key]


def make_collector_function(workdir, read_func, *args, **kwargs):
    """ Returns a function that runs `read_func(*args,**kwargs)` in the
directory that is the join of `workdir` and the argument to the function
    """
    return read_from_dir(roll_in_args(read_func, *args, **kwargs), workdir)


# @ignored(TypeError)
def collect(dir_, read_func):
    """ Switches to `dir_` and runs `read_func`"""
    with cwd(dir_):
        return read_func()


def roll_in_args(read_func, *args, **kwargs):
    read_func_no_args = partial(read_func, *args, **kwargs)
    read_func_subdir = partial(collect, read_func=read_func_no_args)
    return read_func_subdir


def compose2(f__, g__):
    def fg_(*a, **kw):
        return f__(g__(*a, **kw))
    return fg_


@ignored(TypeError)
def join_dirs(subdirs, workdir):
    dir_ = path.join(workdir,
                     *tuple(string_or_iterable(subdirs)))
    return dir_


def prepend_dir(workdir):
    """ Returns a function that takes a tuple of directories and returns the
combination of those into a path, with `workdir` prepended """
    return partial(join_dirs, workdir=workdir)


def read_from_dir(read_func, workdir):
    """ Composes `read_func` with :func:`prepend_dir(workdir)<prepend_dir>` """
    return compose2(read_func, prepend_dir(workdir))


class Seqs(dict):
    """ Seqeunces of related runs

    :param dict param_dicts: Dictionary containing dictionaries of parameters,
        in the form returned from e.g. :func:`collect_from_all`
    """
    def __init__(self, param_dicts, *args, **kwargs):
        super(Seqs, self).__init__(*args, **kwargs)
        keys = deque(param_dicts.keys())
        for index in list(keys):
            del keys[0]
            for key, indices in get_indices_dict(index,
                                                 param_dicts, keys).items():
                seqs_list = self.get(key, [])
                if all(not indices_sub(param_dicts, indices.values(),
                                       indices_seqs.values())
                       for indices_seqs in seqs_list):
                    self[key] = seqs_list + [indices]

    def iterator(self):
        for key in self:
            for indx, seq_list in enumerate(self[key]):
                yield key, indx, seq_list


class ChangedParams(dict):
    """ Parameters that changed. Derived from dict

    :param dict param_dicts: Dictionary containing dictionaries of parameters,
        in the form returned from e.g. :func:`collect_from_all`
    """
    def __init__(self, param_dicts, *args, **kwargs):
        super(ChangedParams, self).__init__(*args, **kwargs)
        ignore = []
        keys = list(param_dicts.keys())
        for idx in list(keys):
            del keys[0]
            for idx_compare in keys:
                diffs = find_diff_elements(param_dicts[idx],
                                           param_dicts[idx_compare])
                if len(diffs) == 0:
                    ignore.append(idx_compare)
                elif idx_compare not in ignore and idx not in ignore:
                    self[(idx, idx_compare)] = diffs

    def groupby_varname(self):
        """ Groups elements according to the name of the variable.

        Returns a dictionary containing the values of the variables, and
        another with all the pairs of runs"""
        varvalues = {}
        pairs = {}
        for dirs, varnameval in self.items():
            # varnames = frozenset(varnameval.keys())
            varnames = tuple(varnameval.keys())
            varvals = varnameval.values()
            value = dict(zip(dirs, zip(*varvals)))
            sdirs = set(dirs)
            pairs.setdefault(varnames, []).append(sdirs)
            varvalues.setdefault(varnames, {}).update(value)
        return varvalues, pairs


def groupby_params(dict_w_params, params):
    """ Groups `dict_w_params` according the given set of parameters. This
 can be used to e.g. seperate physical from numerical parameters. """
    grouped_dict = {}
    for key, item in dict_w_params.items():
        item_copy = item.copy()
        index_dict = {}
        for param in params:
            if param in item_copy:
                index_dict[param] = item_copy[param]
                del item_copy[param]
        index_tuple = tuple((key, index_dict[key])
                            for key in sorted(index_dict))
        grouped_dict.setdefault(index_tuple, {}).update({key: item_copy})
    return grouped_dict


def remove_nested_dict_keys(dict_w_params, remove_keys=[]):
    for dict_ in dict_w_params.values():
        for key in remove_keys:
            if key in dict_:
                del dict_[key]


def select_by_key_len(connected, length=1):
    return dict((key, list_) for key, list_ in connected.items()
                if len(key) == length)


def find_connected_components(pairs):
    connected = {}
    for key, value in pairs.items():
        connected[key] = conso(value)
    return connected


type_ignore_isnan = ignored(TypeError)(isnan)


def find_diff_elements(dict1, dict2):
    diffs = {}
    for key, value1 in dict1.items():
        if key in dict2:
            value2 = dict2[key]
            if value1 != value2 and not type_ignore_isnan(value1) and not type_ignore_isnan(value2):
                diffs[key] = (value1, value2)
        else:
            diffs[key] = (value1, None)
    return diffs


def catch_list_values(value):
    try:
        hash(value)
    except TypeError:
        value = tuple(value)
    return value


def get_indices_dict(idx, param_dicts, keys):
    indices_dict = {}
    for idx_compare in keys:
        for key, val, val_compare in get_index_for_all_but_one_changed(param_dicts[idx], param_dicts[idx_compare]):
            # if key not in indices_dict:
            #     indices_dict[key] = catch_list_values(val, idx)
            # indices_dict[key].update(catch_list_values(val_compare, idx_compare))
            indices_dict.setdefault(key, {catch_list_values(val): idx}).update({catch_list_values(val_compare): idx_compare})
    return indices_dict


def get_index_for_all_but_one_changed(nl1, nl2):
    for key, value in nl1.items():
        with ignored(KeyError):
            value2 = nl2[key]
            if value != value2:
                if dict_eq_ignore(nl1, nl2, [key]):
                    yield key, value, value2


def dict_eq_ignore(dict1, dict2, ignore_keys=()):
    dict1_flat = copy_w_ignore_keys(dict1, ignore_keys)
    dict2_flat = copy_w_ignore_keys(dict2, ignore_keys)
    return dict1_flat == dict2_flat


def copy_w_ignore_keys(dict_, ignore_keys=()):
    return dict((key, value) for key, value in dict_.items()
                if key not in ignore_keys)


def indices_sub(dicts, indices1, indices2):
    dict_list1 = list(dicts[indx] for indx in indices1)
    dict_list2 = list(dicts[indx] for indx in indices2)
    return issubset(dict_list2, dict_list1)


def issubset(list1, list2):
    """ Checks if list1 is subset of list2 """
    list3 = []
    for elem in list2:
        if elem in list1:
            list3.append(elem)
    return list2 == list3


# This function was inspired by nmltab
def dictdiff(alldicts):
    """ In-place removes all key:value pairs that are shared across all dicts

    :param dict alldicts: a dictionary containing dictionaries"""
    superdict = superset(alldicts)
    for key in superdict:
        all_dicts_have_key = all((key in dict_) for dict_ in alldicts.values())
        if all_dicts_have_key:
            value_is_same = all((superdict[key] == dict_[key])
                                for dict_ in alldicts.values())
            if value_is_same:
                for dict_ in alldicts.values():
                    del dict_[key]


# From: https://rosettacode.org/wiki/Set_consolidation#Python
def consolidate(sets):
    setlist = [s for s in sets if s]
    for i, s1 in enumerate(setlist):
        if s1:
            for s2 in setlist[i+1:]:
                intersection = s1.intersection(s2)
                if intersection:
                    s2.update(s1)
                    s1.clear()
                    s1 = s2
    return [s for s in setlist if s]


# From: https://rosettacode.org/wiki/Set_consolidation#Python
def conso(s):
    if len(s) < 2:
        return s

    r, b = [s[0]], conso(s[1:])
    for x in b:
        if r[0].intersection(x):
            r[0].update(x)
        else:
            r.append(x)
    return r


def groupby_n_var_params(dict_w_params, n_var_params=1):
    """ Convenience function for finding sets of data for which
    `n_var_params` parameters are changing """
    dict_w_params = dict_w_params.copy()
    dictdiff(dict_w_params)
    changedsparams = ChangedParams(dict_w_params)
    varvals, pairs = changedsparams.groupby_varname()
    connected = find_connected_components(pairs)
    nseqs = select_by_key_len(connected, length=n_var_params)
    return nseqs, varvals
