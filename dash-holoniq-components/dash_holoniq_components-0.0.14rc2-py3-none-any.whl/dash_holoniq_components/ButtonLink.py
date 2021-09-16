# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ButtonLink(Component):
    """A ButtonLink component.
ButtonLink allows you to create a clickable link within a multi-page app in
the same way as dcc.Link. The standard dcc.Button attributes `n_clicks` 
and `n_clicks_timestamp` have been added to ButtonLink. These attributes
can be used for notification that the ButtonLink has been clicked

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- className (string; optional):
    Often used with CSS to style elements with common properties.

- disabled (boolean; optional):
    Set True to disable the component.

- href (string; optional):
    The URL of a linked resource.

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

- n_clicks (number; default 0):
    An integer that represents the number of times that this element
    has been clicked on.

- n_clicks_timestamp (number; default -1):
    An integer that represents the time (in ms since 1970) at which
    n_clicks changed. This can be used to tell which button was
    changed most recently.

- refresh (boolean; default False):
    Controls whether or not the page will refresh when the link is
    clicked.

- style (dict; optional):
    Defines CSS styles which will override styles previously set."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, href=Component.UNDEFINED, disabled=Component.UNDEFINED, refresh=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, n_clicks=Component.UNDEFINED, n_clicks_timestamp=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'disabled', 'href', 'loading_state', 'n_clicks', 'n_clicks_timestamp', 'refresh', 'style']
        self._type = 'ButtonLink'
        self._namespace = 'dash_holoniq_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'disabled', 'href', 'loading_state', 'n_clicks', 'n_clicks_timestamp', 'refresh', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(ButtonLink, self).__init__(children=children, **args)
