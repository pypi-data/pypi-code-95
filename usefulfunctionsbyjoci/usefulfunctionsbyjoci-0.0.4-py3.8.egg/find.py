import os

def find_files(substring, path):
    """
    find_files('test', '/testdir')
    you can find files with this in directory
    .. versionadded:: 0.0.4
    """
    
    results = []
    for f in os.listdir(path):
        if substring in f:
            results.append(os.path.join(path, f))
    return results
    