class PyVersion:
    
    def __init__(self, version: str):
        self._version = version
        a, b, c, *_ = (version + '.0.0.0').split('.')
        self.major = int(a)
        self.minor = int(b)
        self.patch = int(c)
    
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
    def v0(self):
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
    def v1(self):
        """
        Returns:
            self._version = 'python39' -> '39'
            self._version = 'python39-32' -> '39-32'
        """
        return self._version.removeprefix('python')
