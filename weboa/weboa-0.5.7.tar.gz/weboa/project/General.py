from PIL import Image
from weboa.utils import Processing
from weboa.utils import Meta
from weboa import os
from weboa import prepare
from weboa import json


class General(Processing.Processing):
    def __init__(self, langs=("en", "ru"), path="../", BUILDFOLDER="/"):
        super().__init__(path=path, BUILDFOLDER=BUILDFOLDER)
        self.langs = langs
        Meta.meta.Weboa_Add("langs", json.dumps(self.langs))

    @staticmethod
    def load(backend):
        _backend = Meta.meta.Weboa_Open()
        __backend = backend(path=_backend["rpath"],
                            langs=json.loads(_backend["langs"]),
                            BUILDFOLDER=_backend["build_folder"])
        return __backend

    def robots(self):
        self.copy(prepare.Package.stream + 'misc/robots.txt', "/robots.txt")

    def ico(self):
        img = Image.new('RGB', (64, 64))
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
        img.save(os.path.join(self.path, self.BUILDFOLDER) + '/favicon.ico', sizes=icon_sizes)

    def css(self, css="css"):
        files = ["/css/styles." + css]
        for f in files:
            self.File_Create(f)

    def js(self):
        files = ["/js/script.js"]
        for f in files:
            self.File_Create(f)

    def img(self):
        img = Image.new('RGB', (128, 128))
        img.save(os.path.join(self.path, self.BUILDFOLDER) + '/img/favicon.png')
        img = Image.new('RGB', (1024, 500))
        img.save(os.path.join(self.path, self.BUILDFOLDER) + '/img/sn_share.png')

    def readme(self):
        self.copy(prepare.Package.stream + 'misc/README.md', "/README.md")

    def gitignore(self):
        self.copy(prepare.Package.stream + 'misc/gitignore', "/.gitignore")

    def _add(self, wh, f="footer", t="js"):
        fpath = self.path + self.BUILDFOLDER + "/php/modules/" + f + ".phtml"
        with open(fpath, "r") as f:
            _Wh = f.read()
        _Wh = _Wh.split("\n")

        if t == "js":
            tt = wh.load_script()
        elif t == "css":
            tt = wh.load_link()

        for s in tt:
            if t == "js":
                _Wh.insert(1, "<script src='" + s + "'></script>\n")
            elif t == "css":
                _Wh.insert(-1, "<link href='" + s + "' rel='stylesheet'/>")

            with open(fpath, "w") as f:
                f.write("\n".join(_Wh))

    def script(self, jscript):
        self._add(jscript)

    def link(self, _link):
        self._add(_link, "header", "css")
