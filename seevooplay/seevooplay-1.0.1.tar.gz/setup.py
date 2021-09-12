# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['seevooplay', 'seevooplay.migrations']

package_data = \
{'': ['*'],
 'seevooplay': ['static/seevooplay/css/*',
                'templates/*',
                'templates/admin/seevooplay/event/*',
                'templates/seevooplay/*']}

install_requires = \
['Django>=3.2.4,<4.0.0',
 'Pillow>=8.2.0,<9.0.0',
 'django-model-utils>=4.1.1,<5.0.0',
 'django-richtextfield>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'seevooplay',
    'version': '1.0.1',
    'description': 'Seevooplay is a Django app for online invitations and RSVPs.',
    'long_description': "# Seevooplay\n\nSeevooplay is a Django app for online invitations and RSVPs. Think of it as your personal, selfhosted version of Evite (or a similar service). Throwing a party? Don't give all your friends' email addresses to Evite. Don't expect your friends to be on Facebook. Embrace the indieweb, kick the corporate middleman to the curb, and let Seevooplay send email invitations and collect responses for you! That's the pitch, anyway.\n\nSeevooplay was crafted for *personal* use; it is not architected for scale. It is directly inspired by [DaVite](http://marginalhacks.com/Hacks/DaVite/), a 2000-line Perl script last updated in 2004 -- a very cool and useful hack for its time, but inappropriate for use on the web in 2021. Seevooplay aims to solve the same problems DaVite did, in much the same way, but with modern, maintainable, extensible code, atop the rock-solid foundation of Python and Django.\n\nThe owner of a Seevooplay instance interacts with Seevooplay mainly through Django's admin. [[Screenshot 1](https://user-images.githubusercontent.com/782716/129496242-c791d261-0d5f-43a7-b65d-b8759685b9af.png), [Screenshot 2](https://user-images.githubusercontent.com/782716/129496271-2591b149-db9f-41bd-96ab-9cad18e91c08.png)] Invitees interact with a single public view, whose template and styling is deliberately minimalistic and intended to be customized. [[Screenshot 3](https://user-images.githubusercontent.com/782716/129496302-b2ebeff9-c73b-49cc-b971-706db8589f05.png)] Through the magic of the CSS cascade and Django [template overriding](https://docs.djangoproject.com/en/3.2/howto/overriding-templates/), you can make what your guests see as gorgeous (or as ugly) as you like.\n\nYour invitees will receive emails containing personalized links back to your Seevooplay instance. They won't have to create any sort of account (or log in) to RSVP to your event; a UUID in their link tells Seevooplay who they are.  *This means that forwarded links are problematic: If Alice forwards her invitation to Bob, Bob can RSVP as Alice.* In other words, from a security standpoint, Seevooplay is about as naive as it gets. For the casual, personal use cases Seevooplay is designed for, however, this model works. If it spooks you, your parties are much higher stakes than mine, and you should look for a different solution. :)\n\nSeevooplay is free software, licensed under the terms of the GNU General Public License, Version 3. See the included COPYING file for details.\n\n# Installation\n\nSeevooplay can be run as a standalone project, or integrated with an existing Django project.\n\n## Run as a standalone project\n\nThere is not (yet) a containerized distribution of Seevooplay, but if you are familiar with Python, Django, and their modern ecosystems, you should have no trouble getting Seevooplay up and running as a standalone Django project. In broad strokes, the steps are:\n\n1. Download the Seevooplay distribution and extract to a folder, or `git clone` it.\n2. Copy config/settings/local.py.example to config/settings/local.py and edit local.py to match your server environment.\n3. Create a Python virtual environment with your tool of choice and populate it with Seevooplay's dependencies. For example, `pip install -r requirements.txt` or `poetry install`.\n4. The rest happens from within your virtualenv. First:\n```\n./manage.py migrate\n./manage.py collectstatic\n```\n5. Do `./manage.py sendtestemail` to ensure your setup can send mail.\n6. Do `./manage.py createsuperuser` to create a superuser.\n7. Fire up the Django development server with `./manage.py runserver` or put your favorite server (gunicorn, nginx, apache) in front of the project.\n8. In your browser, navigate to http://yourdomain/admin and log in with your superuser credentials to poke around and create your first event in Seevooplay. As long as you remain logged in, you can view your first event at http://yourdomain/rsvp/1.\n\n## Integrate with an existing Django project\n\n1. Add Seevooplay to your project with `pip install seevooplay` or `poetry add seevooplay` or whatever your Python package-manager-of-choice requires.\n2. Add to INSTALLED_APPS in your settings.py:\n```\n'djrichtextfield',  # required for seevooplay\n'seevooplay.seevooplay',\n```\n3. Add settings for django-richtextfield in your settings.py. See [django-richtextfield's docs](https://github.com/jaap3/django-richtextfield#django-rich-text-field) for details, or copy the DJRICHTEXTFIELD_CONFIG stanza from Seevooplay's config/settings/base.py.\n4. In your main urls.py, add this import:\n```\nfrom seevooplay.seevooplay.views import email_guests, event_page\n```\n... and these urlpatterns:\n```\npath('admin/email_guests/<int:event_id>/', email_guests, name='email_guests'),\npath('rsvp/<int:event_id>/', event_page, name='invitation'),\npath('rsvp/<int:event_id>/<guest_uuid>/', event_page),\npath('djrichtextfield/', include('djrichtextfield.urls')),\n```\n5. From within your project's virtual environment:\n```\n./manage.py migrate\n./manage.py collectstatic\n```\n6. There should now be a Seevooplay section in your project's admin, where you can start kicking the tires.\n\n# What Seevooplay Lacks\n\n- 'Add to calendar' functionality. This is probably something I'll hack on at some point.\n- Internationalization. I welcome pull requests to change this.\n- HTML emails. Plain text emails don't bother me, so this is unlikely to change unless someone else does the work.\n- Comprehensive documentation. If anyone other than me ends up using this, the docs will get better. In the meantime, if you try using Seevooplay and run into trouble, please open an issue on GitHub. I will help if I can.\n- Perfection. This software was crafted to scratch a personal itch. It almost certainly has bugs. If you discover one, or you have a suggestion for improving the code, please open an issue on GitHub.\n",
    'author': 'Matthew Newton',
    'author_email': 'matthewn@mahnamahna.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/matthewn/seevooplay',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
