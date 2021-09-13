# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ue_schedule']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'icalendar>=4.0.7,<5.0.0', 'requests>=2.24.0,<3.0.0']

entry_points = \
{'console_scripts': ['ue-schedule = ue_schedule.cli:main']}

setup_kwargs = {
    'name': 'ue-schedule',
    'version': '2.1.3',
    'description': 'UE Katowice class schedule utility library',
    'long_description': '## UE Class schedule utility library\n\nA utility library used to download, filter and export class schedule at University of Economics in Katowice. Imports data from ["Wirtualna uczelnia"](https://e-uczelnia.ue.katowice.pl/).\n\nEach students gets a constant schedule id which is used to generate the schedule.\n\nYou can get your ID by going to "Wirtualna uczelnia" > "Rozkład zajęć" > "Prezentacja harmonogramu zajęć" > "Eksport planu do kalendarza".\n\nThe url ends with `/calendarid_XXXXXX.ics`, the XXXXXX will be your ID.\n\n### Installation\n\n```\npip install ue-schedule\n```\n\nYou can then run the ue-schedule tool from your shell like\n\n```sh\nue-schedule <schedule_id>\n```\n\n### Development\n\nYou can install dependencies in a virtualenv with poetry\n\n```bash\npoetry install\n\n# switch to the virtualenv\npoetry shell\n```\n\n### Usage\n\n```python\nfrom ue_schedule import Schedule\n\n# initialize the downloader\ns = Schedule(schedule_id)\n\n# get event list\nschedule.get_events()\n\n# get event list as iCalendar\nschedule.get_ical()\n\n# get event list as json\nschedule.get_json()\n```\n\nData is automatically fetched when exporting, but you can force fetch with\n\n```python\nschedule.fetch()\n```\n\nIf you need to dump the event list and load later\n\n```python\n# dump the event list\nevents = schedule.dump_events()\n\n# load the event list\nschedule.load_events(events)\n```\n\nIf there\'s a need to format the list acquired with `.get_events()`, you can use format functions\n\n```python\n# format event list as ical file\nSchedule.format_as_ical(events)\n\n# format event list as json\nSchedule.format_as_json(events)\n```\n',
    'author': 'Maciej Rim',
    'author_email': 'maciej.rim@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rimmaciej/ue-schedule.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
