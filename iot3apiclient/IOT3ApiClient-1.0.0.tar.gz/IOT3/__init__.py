import requests
import json

class Thing():
    def __init__(self,username, thing ,dev_secret,thing_secret):
            self.user = username
            self.thing = thing
            self.dev_secret = dev_secret
            self.thing_secret = thing_secret

    def __setitem__(self, key, item):
        requests.post("https://iot3.harshaaddanki.repl.co/api/set/" + self.user + "/" + self.thing + "/" + self.dev_secret + "/" + key + "/" + item,data={"thing_secret":self.thing_secret})
        self.__dict__[key] = item

    def __getitem__(self, key):
        r = requests.post("https://iot3.harshaaddanki.repl.co/api/set/" + self.user + "/" + self.thing + "/" + self.dev_secret + "/" + key,data={"thing_secret":self.thing_secret})
        d = json.loads(r.text)
        self.__dict__[key] = d.value
        if d.type == "I":
            return int(self.__dict__[key])
        if d.type == "S":
            return str(self.__dict__[key])
        if d.type == "B":
            return bool(self.__dict__[key])
        if d.type == "D":
            return float(self.__dict__[key])

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        raise Exception("Cannot Delete Property")

    def clear(self):
        raise Exception("Cannot Delete Property")

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __unicode__(self):
        return unicode(repr(self.__dict__))
