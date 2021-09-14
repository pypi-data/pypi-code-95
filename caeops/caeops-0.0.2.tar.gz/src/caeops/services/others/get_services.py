"""
## Description
---
This command helps you register an account with CloudAEye.
Run `caeops user signup --help` for more help.

## Synopsis
---
```
  signup
--email [value]
--given-name [value]
--family-name [value]
--company [value]
--identifier [value]
[--company-phone [value]]
[--company-logo [value]]
[--company-url [value]]
[--linkedin-url [value]]
[--phone-number [value]]
```

## Options
---

--email (string)

> A valid email-id for account registration



## Examples
---
To register a user wth CloudAEye.

The following `signup` example registers a user with CloudAEye.

```
caeops user signup --email user@example.com --email user-example
```


## Output
---

Registered User -> (Structure)
> Details of the registered user
    > Details of the registered user

"""

import argparse
import sys


def get_services():
    # Get a list of all services supported by cloudaeye
    parser = argparse.ArgumentParser(
        prog="caeops get-services", description="Get a list of all CloudAEye services"
    )
    print("metrics-service [Prometheus]")
    print("dashboards-service [Grafana]")
    print("logs-service [ELK]")
    print("alert-manager-service [Alert Manager]")
    print("incident-manager-service [ML/Incident Manager]")
    print("traces-service [Tracing - to be added soon]")
