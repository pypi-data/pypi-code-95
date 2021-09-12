from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.16'
DESCRIPTION = 'A basic number tools package'
LONG_DESCRIPTION = """# num_tool
## _Basic number tools package_

## Features:

**Random numbers list:**
```py
from num_tool import random_num_list
print(random_num_list(0, 5, length=20))
```

- **returns a list with length random values in the range a, b**

Example:
```py
[5, 0, 1, 0, 0, 1, 5, 3, 3, 3, 5, 3, 1, 0, 3, 0, 5, 1, 2, 4]
```

**Count Duplicates:**

```py
from num_tool import count_duplicates
print(count_duplicates([0, 0, 1, 1, 2, 1, 3, 2]))
```

- **returns a dictionary with the duplicates**

Example:
```py
{0: 2, 1: 3, 2: 2, 3: 1}
```

**Remove Duplicates:**

```py
from num_tool import remove_duplicates
print(remove_duplicates([0, 0, 1, 1, 2, 1, 3, 2]))
```

- **returns the list without duplicates**

Example:
```py
[0, 1, 2, 3]
```

**is prime:**

```py
from num_tool import is_prime
print(is_prime(3))
```

- **returns True if the number given is a prime number**

Example:

```py
True
```"""

setup(
    name="num_tool",
    version=VERSION,
    author="totensee (Ruben Pérez Krüger)",
    author_email="<churrerico@web.de>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    install_requires=[],
    packages=["num_tool"],
    keywords=['python', 'random', 'number', 'tools'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    zip_safe=False)