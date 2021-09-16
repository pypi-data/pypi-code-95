# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class LayoutRouter(Component):
    """A LayoutRouter component.
The children of LayoutRouter are each wrapped in a Div that is
is hidden/shown based on the current value of the LayoutRouter 'switch' 
attribute.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- className (string; optional):
    Often used with CSS to style elements with common properties.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- routes (list of strings; optional):
    The route/switch values to be associated with each of the child
    routes.

- switch (string; optional):
    The route to be activated."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, key=Component.UNDEFINED, className=Component.UNDEFINED, switch=Component.UNDEFINED, routes=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'key', 'routes', 'switch']
        self._type = 'LayoutRouter'
        self._namespace = 'dash_holoniq_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'key', 'routes', 'switch']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(LayoutRouter, self).__init__(children=children, **args)
