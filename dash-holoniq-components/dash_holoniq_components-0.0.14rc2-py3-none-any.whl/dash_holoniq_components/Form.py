# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Form(Component):
    """A Form component.
The `Form` components normal submit action is inhibited. Instead the forms 
data, as it would be reported by the default form action, is collected and is
available via the form_data attribute.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- className (string; optional):
    Often used with CSS to style elements with common properties.

- form_data (dict; optional):
    The forms data as it would be reported by the default form action.

- inline (boolean; optional):
    Use inline=True to apply the `form-inline` class, allowing you to
    display a series of labels, form controls, and buttons on a single
    horizontal row. Form controls within inline forms vary slightly
    from their default states.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- loading_state (dict; optional):
    Object that holds the loading state object coming from
    dash-renderer.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- preventDefault (boolean; optional):
    Use preventDefault=True to block the forms default action.

- style (dict; optional):
    Defines CSS styles which will override styles previously set."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, key=Component.UNDEFINED, inline=Component.UNDEFINED, preventDefault=Component.UNDEFINED, form_data=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'form_data', 'inline', 'key', 'loading_state', 'preventDefault', 'style']
        self._type = 'Form'
        self._namespace = 'dash_holoniq_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'form_data', 'inline', 'key', 'loading_state', 'preventDefault', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Form, self).__init__(children=children, **args)
