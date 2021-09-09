from IPython.core.display import HTML
from . import generate_html_table

def show_notebook(**kwargs):
    html = generate_html_table(**kwargs)
    return HTML(html)
