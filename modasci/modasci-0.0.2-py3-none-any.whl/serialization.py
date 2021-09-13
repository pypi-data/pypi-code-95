import abc


class YAMLMixin:

    @abc.abstractmethod
    def toDict(self):
        """Must be overridden.

        Returns
        -------
        dict
            All the essential (serializable) attributes of the instance.
        """
        pass
