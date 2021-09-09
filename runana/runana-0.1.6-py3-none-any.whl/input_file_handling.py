from shutil import copy

try:
    basestring          # Python 2.x
except NameError:
    basestring = str    # Python 3.x


def filter_inp_file_f90nml(inp_file_in, inp_file_out, replace_with_these):
    """ Replaces elements in *inp_file_in* and places the result in *inp_file_out*

    replace_with_these is a dict with entries of the form
    {'Name of parameter':*value to replace with*}

    This version works on namelist files using the f90nml package
    """
    import f90nml
    patch = patch_from_tupled_dict(replace_with_these)
    if patch:
        f90nml.patch(inp_file_in, patch, inp_file_out)
    else:
        copy(inp_file_in, inp_file_out)


def patch_from_tupled_dict(tupled_dict):
    """ Creates a nested dictionary that f90nml can interpret as a patch."""
    patch = {}
    for replace_this, replace_val in tupled_dict.items():
        group, field = replace_this
        group, field = group.lower(), field.lower()
        gdict = patch.get(group, {})
        gdict.update({field: replace_val})
        patch[group] = gdict
    return patch


def filter_inp_file_upname(inp_file_in, inp_file_out, replace_with_these):
    """ Replaces elements in *inp_file_in* and places the result in *inp_file_out*

    replace_with_these is a dict with entries of the form
    {'Name of parameter':*value to replace with*}

    This version replaces entries that is one line below a string matching
    *Name of parameter*, in the same position as the string
    """
    with open(inp_file_in, 'r') as input_file_in:
        input_data = input_file_in.readlines()
    replace_pos = dict(find_upname_positions(input_data, replace_with_these))
    output_data = '\n'.join(replace_lines(input_data, replace_pos))
    with open(inp_file_out, 'w') as input_file_out:
        input_file_out.write(output_data)


def find_upname_positions(input_data, replace_w_these):
    """ Finds the positions at which to do replacements. """
    for iline, line in enumerate(input_data):
        for replace_this, with_this in replace_w_these.items():
            for iword, word in enumerate(line.split()):
                if replace_this == word:
                    yield (iline+1, iword), with_this


def filter_inp_file_positional(inp_file_in, inp_file_out, replace_with_these):
    """ Replaces elements in *inp_file_in* and places the result in *inp_file_out*

    replace_with_these is a dict with entries of the form
    {(line number,field number):*value to replace with*}
    """
    with open(inp_file_in, 'r') as input_file_in:
        input_data = input_file_in.readlines()
    output_data = '\n'.join(replace_lines(input_data, replace_with_these))
    with open(inp_file_out, 'w') as input_file_out:
        input_file_out.write(output_data)


def replace_lines(input_data, replace_w_these):
    for iline, line in enumerate(input_data):
        lin = line.split()
        for (iline_rep, ifield_rep), replace_w_this in replace_w_these.items():
            if iline == iline_rep:
                lin[ifield_rep] = str(replace_w_this)
        yield '  '.join(lin)


#: Available input file filter functions
INP_FILE_FILTERS = {'f90nml': filter_inp_file_f90nml,
                    'upname': filter_inp_file_upname,
                    'positional': filter_inp_file_positional}


def read_positional_file(filename):
    """ Reads input file

    A dictionary is returned, the keys of which are the tuples `(iline,iword)`
    with the line and word index of the value. Each variable/name should be
    seperated by at least two whitespaces, a comma or a tab.
    """
    with open(filename, 'r') as input_file_in:
        input_data = input_file_in.readlines()
    return dict(index_line_words(input_data))


def index_line_words(input_list):
    for iline, line in enumerate(input_list):
        line = line.replace(',', '  ').replace('\t', '  ').split('  ')
        for iword, word in enumerate(line):
            yield (iline, iword), word


def read_upname_file(filename):
    """ Reads file in upname format

    In this format the names of variables are given on a line, with the values
    on the following line. Each variable/name should be seperated by at least
    two whitespaces or a tab. Each set of names/values lines should be
    seperated by at least one blank line
    """
    with open(filename, 'r') as input_file_in:
        input_data = input_file_in.readlines()
    previous_line = []
    data = {}
    for line in input_data:
        # Break line on tab or more than two consequtive whitespaces
        line = line.rstrip().replace(',', '  ').replace('\t', '  ').split('  ')
        line = [num_str(elem.strip()) for elem in line if elem]
        data.update(dict(zip(previous_line, line)))
        previous_line = line
    return data


def read_and_flatten_namelist(filename):
    import f90nml
    namelist = f90nml.read(filename)
    dict_ = dict(flat_iterator(namelist))
    return dict_


def read_input_files_f90nml(patterns=['*.nml'],
                            read_one_file=read_and_flatten_namelist):
    """ Read the all files matching `patterns` with :func:`f90nml.read`

    The namelists are flattened and supersetted, the resulting dict is
    returned
    """
    from itertools import chain
    import glob
    filenames = list(chain(*(glob.glob(pattern)
                             for pattern in string_or_iterable(patterns))))
    return read_list_of_input_files(filenames,
                                    read_one_file=read_one_file)
    # dicts = dict((filename, read_one_file(filename))
    #              for filename in filenames)
    # return superset_collisions(dicts)


def read_list_of_input_files(filenames,
                             read_one_file=read_and_flatten_namelist):
    """ Read the all files in list `filenames` with :func:`f90nml.read`

    The namelists are flattened and supersetted, the resulting dict is
    returned
    """
    dicts = dict((filename, read_one_file(filename))
                 for filename in filenames)
    return superset_collisions(dicts)


def read_input_files_upname(patterns=['*.inp']):
    """ Read the all files matching `patterns` with :func:`read_upname_file`

    The data from all the files is supersetted and the resulting dict is
    returned
    """
    return read_input_files_f90nml(patterns=patterns,
                                   read_one_file=read_upname_file)


def read_input_files_positional(patterns=['*.inp']):
    """ Read the all files matching `patterns` with :func:`read_positional_file`

    The data from all the files is supersetted and the resulting dict is
    returned
    """
    return read_input_files_f90nml(patterns=patterns,
                                   read_one_file=read_positional_file)


def flat_iterator(nml):
    """Iterator that returns the adress of an element as a 2-tuple,
    along with the element """
    for key, value in nml.items():
        for inner_key, inner_value in value.items():
            yield (key, inner_key), inner_value


def string_or_iterable(args):
    """ Generator that assumes args is either a string or an iterable. """
    if isinstance(args, basestring):
        yield args
    else:
        for arg in args:
            yield arg


# This function was inspired by nmltab
def superset(alldicts):
    """ Returns dict containing all keys from the dicts contained in `alldicts`

    :param dict alldicts: a dictionary containing dictionaries"""
    superdict = {}
    for dict_ in alldicts.values():
        superdict.update(dict_)
    return superdict


def superset_collisions(alldicts):
    """ Returns dict containing all keys from the dicts contained in `alldicts`

    :param dict alldicts: a dictionary containing dictionaries

    If two dictionaries contains the same key, the keys will be appended with
    the difference of the file names. """
    superdict = {}
    filenames = list(alldicts.keys())
    filediff_dict = dict(zip(filenames,
                             extract_noncommon_substrings(filenames)))
    for key, dict_ in alldicts.items():
        for innerkey, value in dict_.items():
            if innerkey in superdict and value != superdict[innerkey]:
                try:
                    innerkey += filediff_dict[key]
                except TypeError:
                    try:
                        # innerkey += (filediff_dict[key],)
                        innerkey = (innerkey[0],
                                    str(innerkey[1]) + filediff_dict[key])
                    except TypeError:
                        innerkey = str(innerkey) + filediff_dict[key]
            superdict[innerkey] = value
    return superdict


def num_str(s):
    """ Tries to convert input to integer, then tries float, then complex.
If all these fails the string is returned unchanged"""
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            try:
                return complex(s)
            except ValueError:
                return s


def extract_common_substrings(strings):
    """ Returns all substrings that are common between the strings in the list
`strings` as a single string.
    """
    common = strings[0]
    for string in strings:
        common = ''.join(ndiff_select(string, common))
    return common


def extract_noncommon_substrings(strings, common=None):
    """ Returns a list with parts of strings that are different.

    `common` is a string of all the common parts of `strings`, such as e.g.
    returned from func:`extract_common_substrings`. If set set to `None`,
    func:`extract_common_substrings` will be called to set this variable """
    if common is None:
        common = extract_common_substrings(strings)
    noncommon = [''.join(ndiff_select(string, common, '-'))
                 for string in strings]
    return noncommon


def ndiff_select(string, common, selector=' '):
    from difflib import ndiff
    for s in ndiff(string, common):
        if s[0] == selector:
            yield '{}'.format(s[-1])
