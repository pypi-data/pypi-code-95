# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.


class InvalidPackageNameError(Exception):
    """Invalid package name or non-existing package."""
    def __init__(self, frontend, pkg_name):
        self.frontend = frontend
        self.pkg_name = pkg_name

    def __str__(self):
        return (f'The package {self.pkg_name} could not be found by frontend '
                f'{self.frontend}')


class InvalidPackageVersionError(Exception):
    """Invalid or non-existing version of a valid package"""
    def __init__(self, frontend, pkg_name, version):
        self.frontend = frontend
        self.pkg_name = pkg_name
        self.version = version

    def __str__(self):
        return (f'Version {self.version} of package {self.pkg_name} '
                f'could not be found by frontend {self.frontend}')


class UnhandledFrontendError(Exception):
    """Frontend not supported by backend."""
    def __init__(self, backend, frontend):
        self.backend = backend
        self.frontend = frontend

    def __str__(self):
        return (f'The {self.backend} backend does not work well with the '
                f'{self.frontend} frontend (yet!). Unable to generate a '
                f'package definition.')
