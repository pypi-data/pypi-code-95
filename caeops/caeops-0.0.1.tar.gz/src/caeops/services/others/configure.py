"""
## Description
---
This command helps you configure the cli.

## Synopsis
---
```
  configure
userpoolid [value]

clientid [value]
```

## Options
---

userpoolid (string)

> User pool id as received

--clientid [value]

> Client id as received


## Examples
---
To configure the CLI.

The following `configure` example configures the CLI.

```
caeops configure
```


## Output
---

"""

from caeops.configurations import *
from caeops.global_settings import ConfigKeys
import os


def configure():
    # Creates a new file
    if check_if_config_file_exists():
        email = read(ConfigKeys.EMAIL)
        if email == "email not found" or len(email) == 0:
            write(ConfigKeys.EMAIL, "")
    else:
        if not os.path.exists(config_folder):
            os.mkdir(config_folder)
        write(ConfigKeys.EMAIL, "")


def clear_configuration():
    # Creates a new file
    delete()
