import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
 
#accent color for own css
accent = "#191919"
 
#meta tags for mobile optimization
mobile_optimization = {"name": "viewport", "content": "width=device-width, initial-scale=1"}
 
#function for flex style
def flex_style(additional_dict = dict()):
    flex_style_dict = {
        "display": "flex",
        "justify-content": "center",
        "align-items": "center"
    }
    return flex_style_dict | additional_dict
 
#function for creating content div with specified width
def content_div(width, padding, children):
    return html.Div(
        html.Div(
            children = [
                *children,
                html.Div(style = {"width": width, "width": "100%"})
            ],
            style = {"max-width": width}
        ),
        style = flex_style({"padding": padding})
    )
 
#function for creating modal header with close button
def modal_header_close(title, close_id , color = None):
    return html.Div(
        children = [
            html.H5(
                title,
                className = "modal-title"
            ),
            dbc.Button(
                className = "btn-close",
                id = close_id
            )  
        ],
        className = "modal-header",
        style = {"background-color": color}
    )