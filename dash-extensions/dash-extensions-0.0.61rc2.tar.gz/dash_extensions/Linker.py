# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Linker(Component):
    """A Linker component.
The Sync component makes it possible to synchronize states between components.

Keyword arguments:
- children (list of a list of or a singular dash component, string or numbers; optional): The children of this component. Must be a list of components with length > 1.
- links (dict; optional): List of links. Each link is a list of dicts that specify which properties to synchronize. links has the following type: list of list of dicts containing keys 'id', 'prop'.
Those keys have the following types:
  - id (string; required)
  - prop (boolean | number | string | dict | list; required)s
- id (string; optional): The ID used to identify this component in Dash callbacks.
- style (dict; optional): The CSS style of the component.
- className (string; optional): A custom class name."""
    @_explicitize_args
    def __init__(self, children=None, links=Component.UNDEFINED, id=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'links', 'id', 'style', 'className']
        self._type = 'Linker'
        self._namespace = 'dash_extensions'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'links', 'id', 'style', 'className']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Linker, self).__init__(children=children, **args)
