# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dsfr', 'dsfr.templatetags', 'dsfr.test']

package_data = \
{'': ['*'],
 'dsfr': ['static/dsfr/dist/css/*',
          'static/dsfr/dist/favicons/*',
          'static/dsfr/dist/fonts/*',
          'static/dsfr/dist/js/*',
          'templates/dsfr/*']}

install_requires = \
['Django>=3.2.5,<4.0.0']

setup_kwargs = {
    'name': 'django-dsfr',
    'version': '0.2.2',
    'description': 'Integrate the French government Design System into a Django app',
    'long_description': '===========\nDjango-DSFR\n===========\n\nDjango-DSFR is a Django app to integrate the `French government Design System ("Système de design de l’État français") <https://www.systeme-de-design.gouv.fr/>`_.\n\n\nThis app was created as a part of `Open Collectivités <https://github.com/entrepreneur-interet-general/opencollectivites>`_ and is very much a work in progress. See the `documentation (in French) <https://github.com/entrepreneur-interet-general/django-dsfr/blob/main/DOC.md>`_ for details.\n\nDjango-DSFR (partly) implements the `version 1.1.0 of the DSFR <https://gouvfr.atlassian.net/wiki/spaces/DB/pages/806912001/Version+1.1.0>`_.\n\nRequirements\n------------\nTested with Python 3.8 and Django 3.2.5. Per `vermin <https://github.com/netromdk/vermin>`_, it should work with Python >= 3.0, and it should work with old versions of Django too.\n\nQuick start\n-----------\n\n1. Install with :code:`pip install django-dsfr`.\n\n2. Add "dsfr" to your INSTALLED_APPS setting like this, before the app you want to use it with::\n\n    INSTALLED_APPS = [\n        ...\n        \'dsfr\',\n        <your_app>\n    ]\n\n3. Include the tags in your base.html file::\n\n    # <your_app>/templates/<your_app>/base.html\n    {% load static %}\n    {% load dsfr_tags %}\n\n    <!doctype html>\n    <html lang="fr" data-fr-theme="default">\n    <head>\n      <meta charset="utf-8">\n      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">\n\n      {% dsfr_css %}\n      {% dsfr_favicon %}\n\n      {% block extra_css %}{% endblock %}\n\n      <title>MyApp</title>\n    </head>\n\n    <body>\n      <main id="content">\n        {% block custom_header %}\n          {% include "core/blocks/header.html" %}\n        {% endblock %}\n        {% dsfr_theme_modale %}\n\n        {% block content %}{% endblock %}\n\n        {% include "core/blocks/footer_categories.html" %}\n        {% include "core/blocks/footer.html" %}\n      </main>\n\n      {% dsfr_js %}\n      {% block extra_js %}{% endblock %}\n    </body>\n\n    </html> \n\n4. Start the development server and visit http://127.0.0.1:8000/',
    'author': 'Sylvain Boissel',
    'author_email': 'sylvain.boissel@dgcl.gouv.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/entrepreneur-interet-general/django-dsfr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
