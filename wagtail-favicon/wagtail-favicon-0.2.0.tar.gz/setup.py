# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wagtail_favicon',
 'wagtail_favicon.migrations',
 'wagtail_favicon.templatetags']

package_data = \
{'': ['*'], 'wagtail_favicon': ['templates/*', 'templates/tags/*']}

setup_kwargs = {
    'name': 'wagtail-favicon',
    'version': '0.2.0',
    'description': 'Easily add shortcut icons to any wagtail site.',
    'long_description': "# Wagtail Favicon\n\nEasily add shortcut icons to any wagtail site. Upload a .png image from a wagtail settings page and wagtail-favicon will resize it and add provide markup to your pages via a template tag.\n\n---\n\n### Installation & Setup\n\n#### Install with pip\n\n```\npip install wagtail-favicon\n\nor\n\npoetry add wagtail-favicon\n```\n\n#### Add to Django installed apps\n\n```\nINSTALLED_APPS = [\n    #...\n    'wagtail.contrib.settings'  # <-- ensure you have wagtail settings loaded \n    'wagtail_favicon',\n]\n```\n\n#### Add routes to app.urls\n\n```\nfrom wagtail_favicon.urls import urls as favicon_urls\n\nurlpatterns += [\n    url(r'^documents/', include(wagtaildocs_urls)),\n    url(r'^search/$', search, name='search'),\n    url(r'', include(wagtail_urls)),\n\n    url(r'', include(favicon_urls)),  # <------ add urls to existing urls\n]\n\n# note: newer versions of django may use `path` instead of `url`\n```\n\nOnce you've completed setup you will now be able to access the folloing urls:\n\n- https://example.com/manifest.json\n- https://example.com/browser-config.xml\n\n\n#### Add template tag to <head> tag in templates/base.html\n\n```\n{% load favicon_tags %}\n  <html>\n    <head>\n        {% favicon_meta %}\n    </head>\n```\n\n#### Edit Settings\n\nGo to `Wagtail Admin >> Settings >> Favicon`  \n\nConfigure settings  \n\nFor best results use a transparent png at 1024 x 1024.  \nIdeally pre optimised with a tool like [tinypng.com](https://tinypng.com).\n\n![Screenshot](https://github.com/octavenz/wagtail-favicon/blob/master/screenshot.jpg)\n\n",
    'author': 'Pat Horsley',
    'author_email': 'pat@octave.nz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/octavenz/wagtail-favicon',
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
