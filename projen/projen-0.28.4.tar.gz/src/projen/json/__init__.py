import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import Component as _Component_2b0ad27f, Project as _Project_57d89203


class Projenrc(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.json.Projenrc",
):
    '''(experimental) Sets up a project to use JSON for projenrc.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        filename: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param filename: (experimental) The name of the projenrc file. Default: ".projenrc.json"

        :stability: experimental
        '''
        options = ProjenrcOptions(filename=filename)

        jsii.create(self.__class__, self, [project, options])


@jsii.data_type(
    jsii_type="projen.json.ProjenrcOptions",
    jsii_struct_bases=[],
    name_mapping={"filename": "filename"},
)
class ProjenrcOptions:
    def __init__(self, *, filename: typing.Optional[builtins.str] = None) -> None:
        '''
        :param filename: (experimental) The name of the projenrc file. Default: ".projenrc.json"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if filename is not None:
            self._values["filename"] = filename

    @builtins.property
    def filename(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the projenrc file.

        :default: ".projenrc.json"

        :stability: experimental
        '''
        result = self._values.get("filename")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjenrcOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Projenrc",
    "ProjenrcOptions",
]

publication.publish()
