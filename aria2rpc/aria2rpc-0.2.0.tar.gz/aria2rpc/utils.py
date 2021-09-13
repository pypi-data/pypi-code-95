import requests
import json
import os
from lxml import html


__ALL__ = ["generate_core"]


def generate_core():
    ref = "https://aria2.github.io/manual/en/html/aria2c.html"
    r = requests.get(ref)
    r = html.fromstring(r.content.decode())
    methods = r.xpath("//*[@id='methods']/dl/dt")
    obj = {}
    for method in methods:
        name = method.xpath("./@id")[0]
        args = method.xpath("./em[@class='sig-param']")
        for i in range(0, len(args)):
            prev_is_open = args[i].xpath("./preceding-sibling::span[1]/text()")[0] == "["
            next_is_close = args[i].xpath("./following-sibling::span[1]/text()")[0] == "]"
            try:
                _args = args[i].xpath("./text()")[0]
            except:
                _args = args[i].xpath("./*/text()")[0]
            if prev_is_open or next_is_close:
                args[i] = [0, _args]
            else:
                args[i] = [1, _args]
        cls, func = name.split(".")
        cls += "_rpc_api"
        if cls not in obj:
            obj[cls] = {}
        obj[cls][func] = args
        print(func)
    tab = 4*" "
    out = '''from xmlrpc.client import ServerProxy


__ALL__ = <__ALL__>


class base_rpc_api:
    def __init__(self, host: str = "127.0.0.1", port: int = 6800, secret: str = ""):
        self.secret = "token:{}".format(secret)
        self.client = ServerProxy("http://{}:{}/rpc".format(host, port))
        
'''
    _all = []
    for cls, methods in obj.items():
        _all.append(cls)
        if out:
            out += "\n"
        out += "class {}(base_rpc_api):\n".format(cls)
        for method, args in methods.items():
            required = "".join(["\n{}if not {}:\n{}raise Exception(\"'{}' argument is required\")".format(
                tab*2,
                arg,
                tab*3,
                arg
            ) for required, arg in args if required])
            out += "{}def {}({}):\n{}{}\n{}params = [_ for _ in [{}] if _]\n{}return self.client.{}.{}(*params)\n\n".format(
                tab,
                method,
                ", ".join(["self"]+["{}=None".format(v) for k, v in args]),
                tab*2+"# "+ref+"#"+cls[:-8]+"."+method,
                required,
                tab*2,
                ", ".join(["{} or self.secret".format(v) if v == "secret" else v for k, v in args]),
                tab*2,
                cls[:-8],
                method,
            )
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "core.py"), "wb").write(out.replace("<__ALL__>", json.dumps(_all)).encode())


if __name__ == '__main__':
    generate_core()


