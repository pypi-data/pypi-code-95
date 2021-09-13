# Copyright (C) 2019  Nexedi SA and Contributors.
#                     Romain Courteaud <romain@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.

import io
import re
from setuptools import setup, find_packages

with io.open("src/surykatka/bot.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="surykatka",
    version=version,
    license="GPLv3+",
    author="Nexedi",
    author_email="romain@nexedi.com",
    long_description=__doc__,
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=False,
    zip_safe=True,
    python_requires=">=3.5",
    install_requires=[
        "setuptools>40.5.0",
        "requests>2.20.0",
        "forcediphttpsadapter",
        "peewee>2.10.1",
        "click>=7.0",
        "dnspython",
        "python-whois",
        "miniupnpc",
    ],
    extras_require={
        "dev": ["pytest", "black", "pyflakes", "mock", "httpretty"]
    },
    entry_points={
        "console_scripts": [
            "surykatka=surykatka.cli:runSurykatka ",
            "surykatkastat=surykatka.cli:runStats ",
        ]
    },
)
