import re


class PyVersion:
    
    def __init__(self, version: str):
        """
        Args:
            version: str['python27', 'python38', 'python39',
                         'python27-32', 'python38-32', 'python39-32', ...]
        """
        self._version = version
        assert re.match(r'^python[23]\d+(?:-32)?', version), \
            ('Illegal version pattern!', version)
        self.major = int(version[6])  # 2 or 3
        self.minor = int(version.split('-')[0][7:])
        #   0, 1, 2, ..., 9, 10 ('python310'), ...
    
    def __str__(self):
        return self._version
    
    @property
    def v(self):
        """
        Returns:
            self._version = 'python39' -> 'python39'
            self._version = 'python39-32' -> 'python39-32'
        """
        return self._version
    
    @property
    def v_prefix(self):
        """
        Returns:
            self._version = 'python39' -> 'python39'
            self._version = 'python39-32' -> 'python39'
        """
        if '-' in self._version:
            return self._version.split('-')[0]
        else:
            return self._version
    
    @property
    def v_suffix(self):
        """
        Returns:
            self._version = 'python39' -> '39'
            self._version = 'python39-32' -> '39-32'
        """
        return self._version.removeprefix('python')
