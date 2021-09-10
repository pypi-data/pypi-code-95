import filetype


def valid_filetype(filename):
    if filetype.guess(filename).extension == 'zip':
        return True
    else:
        return False
