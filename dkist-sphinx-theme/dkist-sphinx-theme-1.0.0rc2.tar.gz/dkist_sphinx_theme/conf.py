import os
from . import get_html_theme_path

html_theme_path = get_html_theme_path()

html_theme = "dkist"

html_theme_options = {
                      'navbar_links': [
                                       ("DKIST", "http://dkist.nso.edu/", "index"),
                                      ]
                     }

html_favicon = os.path.join(html_theme_path[0], html_theme, "static",
                            "img", "favico.ico")

html_sidebars = {
    '**': ['localtoc.html'],
    'search': [],
    'genindex': [],
    'py-modindex': [],
}
