

__version__ = 20210913


def version(version_value=__version__, verbose=True):
    version_dev = 'Alpha'
    if verbose:
        return '{version_dev} version {version_number}'.format(version_dev=version_dev, version_number=version_value)
    else:
        return version_value