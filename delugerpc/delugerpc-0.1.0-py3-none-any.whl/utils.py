import os


__ALL__ = ["generate_core"]


def generate_core(root: str):
    if not root:
        raise Exception("root: path to deluge python library")
    obj = {}
    for a, b, c in os.walk(root):
        for d in c:
            if d.endswith(".py"):
                fp = os.path.join(a, d)
                content = open(fp, "rb").read().decode().splitlines()
                cls = ""
                has_func = False
                if "plugins" in a:
                    cls = a.split(os.path.sep)[-1].split("_")[-1]+"_rpc_api"
                for i, line in enumerate(content):
                    if "plugins" not in a and "class" in line and line.endswith(":"):
                        cls = line.strip().split(" ")[-1].split("(")[0].lower().replace("webapi", "web")+"_rpc_api"
                        continue
                    if "@export" in line and "@deprecated" not in content[i-1]:
                        func = content[i+1].strip().split("def ")[1].split("(")[0]
                        args = content[i+1].strip().split("(")[-1].split(")")[0].split(", ")
                        if "self" in args:
                            args.remove("self")
                        args = [_ for _ in args if _]
                        if cls not in obj:
                            obj[cls] = {}
                        ref = "{}#L{}".format(fp, i+2)
                        if "plugins" in ref:
                            ref = ref.split(os.path.sep)
                            ref[-3] = ref[-3].split("-")[0]
                            ref = os.path.sep.join(ref)
                        obj[cls][func] = [args, ref.replace(root, "https://github.com/deluge-torrent/deluge/tree/develop/deluge").replace(os.path.sep, "/")]
                        data = [func]#[cls, func, args, ref.replace(root, "https://github.com/deluge-torrent/deluge/tree/develop/deluge").replace(os.path.sep, "/")]
                        has_func = True
                        print(("\t".join(["{}"]*len(data))).format(*data))
                if has_func:
                    print()
    print()
    tab = 4*" "
    out = '''import requests
import urllib3


__ALL__ = ["deluge_rpc_api"]


urllib3.disable_warnings()


class deluge_rpc_api:
    def __init__(self, secured: bool = False, host: str = "127.0.0.1", port: int = 8112):
        self.rpc_url = "http{}://{}:{}/json".format("s" if secured else "", host, port)
        self.call_id = 0
        self.s = requests.Session()
        <init>

    def post(self, method, params):
        self.call_id += 1
        return self.s.post(
            self.rpc_url,
            json={
                "id": self.call_id,
                "method": method,
                "params": params or [],
            },
            verify=False
        ).json()
        
    '''.replace("<init>", "\n{}".format(tab*2).join(["self.{} = {}()\n{}self.{}.post = self.post".format(cls[:-8], cls, tab*2, cls[:-8]) for cls in obj]))
    for cls, methods in obj.items():
        print(cls)
        if out:
            out += "\n"
        out += "class {}:\n".format(cls)
        methods["post"] = [["*args", "**kwargs"], ""]
        for method, (args, ref) in methods.items():
            out += "{}def {}({}):\n{}{}\n\n".format(
                tab,
                method,
                ", ".join(["self"]+["{}{}".format(v, "" if v.startswith("*") or "=" in v else "=None") for v in args]),
                tab*2,
                "{}\n{}data = {}\n{}return self.post(**data)".format(
                    "# "+ref,
                    tab*2,
                    '''{{"method": "{}", "params": [{}]}}'''.format(cls[:-8]+"."+method, ", ".join([_.split("=")[0].replace("*", "") for _ in args])),
                    tab*2,
                ) if method != "post" else "pass"
            )
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "core.py"), "wb").write(out.encode())


if __name__ == '__main__':
    generate_core(r"C:\Program Files\Python39\lib\site-packages\deluge")


