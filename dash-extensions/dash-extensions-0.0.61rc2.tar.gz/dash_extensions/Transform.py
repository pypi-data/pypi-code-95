# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Transform(Component):
    """A Transform component.
The EventListener component listens for events from the document object or children if provided.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component. If any children are provided, the
    component will listen for events from these      components. If no
    children are specified, the component will listen for events from
    the document object.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    A custom class name.

- data (string | dict; optional):
    Input data for transform.

- style (dict; optional):
    The CSS style of the component.

- transform (string | dict; optional):
    Style function applied on hover."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, transform=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, data=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'data', 'style', 'transform']
        self._type = 'Transform'
        self._namespace = 'dash_extensions'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'data', 'style', 'transform']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Transform, self).__init__(children=children, **args)
