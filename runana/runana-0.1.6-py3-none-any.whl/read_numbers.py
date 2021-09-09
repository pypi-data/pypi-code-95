from contextlib import contextmanager
try:
    @contextmanager
    def whatever():
        yield

    @whatever()
    def whateever():
        pass
except TypeError:
    from contextlib2 import contextmanager


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


# ignored = contextmanager(ignored)

# def ignore_error(error=IOError, return_=None):
#     def ignore(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except error:
#                 return return_
#         return wrapper
#     return ignore


ignore_missing_file = ignored(IOError)


@ignore_missing_file
def read_last_number_from_file(fname, pattern=''):
    number = None
    with open(fname) as stdout_file:
        for number in numbers_in_file_iterator(stdout_file, pattern=pattern):
            pass
    return number


@ignore_missing_file
def read_smallest_number_from_file(fname, pattern=''):
    with open(fname) as stdout_file:
        smallest = 100000
        for number in numbers_in_file_iterator(stdout_file, pattern=pattern):
            if number < smallest:
                smallest = number
    return smallest


@ignore_missing_file
def read_number_from_file(fname, inumber, pattern=''):
    with open(fname) as stdout_file:
        for indx, number in enumerate(numbers_in_file_iterator(stdout_file, pattern=pattern)):
            if indx == inumber-1:
                return number
    number = 'Not enough numbers in file'
    return number


@ignore_missing_file
def read_column_from_file(fname, icolumn, pattern=''):
    with open(fname) as stdout_file:
        for line in lines_in_file_iterator(stdout_file, pattern=pattern):
            for indx, word in enumerate(line.split()):
                if indx == icolumn-1:
                    return word


@ignore_missing_file
def read_entire_file(fname):
    with open(fname) as file_:
        return file_.readlines()


def lines_in_file_iterator(file_handle, pattern=''):
    for line in file_handle:
        if pattern in line:
            yield line


def words_in_file_iterator(file_handle, pattern=''):
    for line in lines_in_file_iterator(file_handle, pattern=pattern):
        for word in line.split():
            yield word


def numbers_in_file_iterator(file_handle, pattern=''):
    for word in words_in_file_iterator(file_handle, pattern=pattern):
        try:
            number = float(word)
            yield number
        except ValueError:
            pass


def split(delimiters, string, maxsplit=0):
    import re
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)


@ignore_missing_file
def read_file_sev_blocks(fname):
    with open(fname, 'r') as fil:
        blocks = [[[float(element) for element in line.split()]
                   for line in block.split('\n') if len(line) > 0]
                  for block in split(['\n \n', '\n\n'], fil.read())
                  if len(block) > 0]
    return blocks


def numpy_file_read(fname):
    import numpy as np
    try:
        a = np.loadtxt(fname)
    except IOError:
        a = None
    return a


def read_file_sev_blocks_c(fname):
    with open(fname, 'r') as fil:
        blocks = [[[num_c(element) for element in line.split()]
                   for line in block.split('\n') if len(line) > 0]
                  for block in split(['\n \n', '\n\n'], fil.read())
                  if len(block) > 0]
    return blocks


def read_file_super_blocks(fname):
    with open(fname, 'r') as fil:
        blocks = [[[[num_c(element) for element in line.split()]
                    for line in block.split('\n') if len(line) > 0]
                   for block in split(['\n \n', '\n\n'], super_block) if len(block) > 0]
                  for super_block in split(['\n \n \n', '\n\n\n'], fil.read()) if len(super_block) > 0]
    return blocks


def read_file_sev_blocks_new(fname):
    with open(fname, 'r') as fil:
        lines = [[num_c(field) for field in line.split()] for line in fil
                 if not line.lstrip()[:1] == '#']
    lines = split_list(lines)
    return lines


def read_file_sev_blocks_float(fname):
    with open(fname, 'r') as fil:
        lines = [[float(field) for field in line.split()] for line in fil
                 if not line.lstrip()[:1] == '#']
    return split_list(lines)


def read_file_sev_blocks_float_no_comment(fname):
    with open(fname, 'r') as fil:
        lines = [[float(field) for field in line.split()] for line in fil]
    return split_list(lines)


def split_list(list_):
    len_lines = list(map(len, list_))
    zero_idx = [i for i, x in enumerate(len_lines) if x == 0]
    if len(zero_idx) == 0:
        return list_
    else:
        if len(list_)-1 != zero_idx[-1]:
            zero_idx = zero_idx + [len(list_)]
        rangez = [(i+1, j) for i, j in zip(zero_idx, zero_idx[1:])]
        if zero_idx[0] != 0:
            rangez = [(0, zero_idx[0])] + rangez
        splitted_list = split_list([list_[i:j] for i, j in rangez])
        return splitted_list


def num_c(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return complex(s)


def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def read_file_one_block(fname):
    with open(fname, 'r') as fil:
        block = [[num(element) for element in line.split()]
                 for line in fil.read().split('\n') if len(line) > 0]
    return block


def read_file_one_block_c(fname):
    with open(fname, 'r') as fil:
        block = [[num_c(element) for element in line.split()]
                 for line in fil.read().split('\n') if len(line) > 0]
    return block


def read_file_one_block_numpy(fname):
    import numpy as np
    block = read_file_one_block(fname)
    return np.asarray(block)
