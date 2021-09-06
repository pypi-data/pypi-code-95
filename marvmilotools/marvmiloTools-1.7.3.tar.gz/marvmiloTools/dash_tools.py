#function for flex style
def flex_style(additional_dict = dict()):
    flex_style_dict = {
        "display": "flex",
        "justify-content": "center",
        "align-items": "center"
    }
    return flex_style_dict | additional_dict