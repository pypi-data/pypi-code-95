import abc


class DocumentString(abc.ABC):

    @abc.abstractproperty
    def content(self) -> str:
        ...
