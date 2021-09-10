#!/usr/bin/env python
from weboa import *
from weboa import __VERSION__
from time import sleep as waitfor
import sys
import glob

from weboa.utils.Processing import Processing


def runcli():
    print("Welcome to Weboa!")
    commands = {
        "version": ("--version", "-v"),
        "init": ("--init","-i"),
        "start": ("--start", "-S"),
        "update": ("--update","-u"),
        "build": ('--build',"-b"),

        "add":("--add","-a"),
        "repo":("--repo","-r"),
        "list": ["--list"],
        "help": ("-h","--help"),

        "less": ("--less","-l"),
        "sass": ("--sass","--scss","-s"),

        "langs": ("--langs", "-L"),
        "css": ["--css"]
    }

    args = sys.argv
    for i in range(len(args)):
        if args[i] in commands["version"]:
            print(f"Weboa version is {__VERSION__}")

        elif args[i] in commands["update"]:
            os.system("pip install weboa --upgrade")
            os.system("pip3 install weboa --upgrade")
            os.system("pip3 install weboa --upgrade")

        elif args[i] in commands["help"]:
            print("Usage: weboa [-h] [--init OUTPUT_DIR] [--start] [--langs en...]\n"
                  "Project/Package manager. \n"
                  "\n"
                  "positional arguments: \n"
                  "--css\t\t\t\t\t Select preprocess (less|sass|scss) \n"
                  "-L, --langs\t\t\t\t Select languages shortly (ru|en|ro)\n "
                  "\n"
                  "optional arguments: \n"
                  "-h, --help\t\t\t\t Show this help text\n "
                  "-a, --add\t\t\t\t Css [framework], js [framework], php [framework], fonts [font]\n "
                  "--list\t\t\t\t\t Select list of all frames for [--add]\n"
                  "-r, --repo\t\t\t\t Select list of all PHP packaged\n"
                  "\n"
                  "-l, --less\t\t\t\t Start LESS watcher. Use with & in the end \n"
                  "-s, --sass\t\t\t\t Start SASS watcher. Use with & in the end\n "
                  "-s, --scss\t\t\t\t Start SCSS watcher. Use with & in the end \n"
                  "\n"
                  "-v, --version\t\t\t\t Show current version of Weboa \n"
                  "-u, --update\t\t\t\t Update Weboa through pip \n"
                  "-b, --build\t\t\t\t Minify .js, .css files \n"
                  "-S, --start\t\t\t\t Init .weboa project file \n"
                  "-i, --init\t\t\t\t Initi project (use --init with OUTPUT_DIR)\n")

        elif args[i] in commands["build"]:
            try:
                backend = General.load(PHP)
            except TypeError:
                Printer.error("No .weboa meta file!")
                return False
            try:
                backend.copytree(".", "./build/")
            except:
                pass

            Processing.minify("build/js","js")
            Processing.minify("build/css", "css")

            for f in list(os.walk("./build/php/modules")):
                fpath = f[0]
                Processing.minify(fpath, "phtml")
                Processing.minify(fpath, "html")

            for f in list(os.walk("./build/css")):
                if(f[0][-3:]!="css" or f[0][-10:]=="styles.css"):
                    continue

                with open("./build/css/styles.css", "r") as f:
                    fw = f.read()
                with open(f[0],"r") as f:
                    fw2 = f.read()
                with open("./build/css/styles.css", "w") as f:
                    f.write(fw+fw2)

                os.remove(f[0])

            
        elif args[i] in commands["list"]:
            try:
                print(Library.listall(args[i+1]))
            except IndexError:
                print("css | js | fonts | php")

        elif args[i] in commands["start"]:
            _path = os.getcwd()
            Meta.meta.Weboa_Save(Meta.meta.Weboa_Init())
            Processing.Save_Path(os.getcwd())
            Meta.meta.Weboa_Add("build_folder", _path + "/")
            Meta.meta.Weboa_Add("rpath", "")
            Meta.meta.Weboa_Add("langs", json.dumps(["en","ru"]))
            Printer.info(f"Weboa is installed at {prepare.Package.stream}")

        elif args[i] in commands["repo"]:
            url = "https://raw.githubusercontent.com/New-Vektor-Group/pkg-repo/main/php/libs.json"
            result = Downloader.get(url)
            print(result)

        elif args[i] in commands["add"]:
            _lib = args[i+1]
            _frame = args[i+2]
            try:
                backend = General.load(PHP)
            except TypeError:
                Printer.error("No .weboa meta file!")
                return False

            if(_lib=="css"):
                if(_frame=="mdb5"):
                    backend.link(MDB5())
                elif(_frame=="mdb"):
                    backend.link(MDB())
                elif (_frame == "bootstrap"):
                    backend.link(Bootstrap())
                elif (_frame == "bootstrap5"):
                    backend.link(Bootstrap5())
            elif(_lib=="fonts"):
                if (_frame == "roboto"):
                    backend.link(Roboto())
                elif (_frame in ("FontAwesome","fa")):
                    backend.link(FontAwesome())
            elif(_lib=="js"):
                if _frame == "umbrella":
                    backend.script(UmbrellaJS())
                elif _frame == "jquery":
                    backend.script(JQuery())
                elif _frame == "popper":
                    backend.script(Popper())
                elif _frame == "mdb5":
                    backend.script(MDB5())
                elif _frame == "mdb":
                    backend.script(MDB())
                elif (_frame == "bootstrap"):
                    backend.script(Bootstrap())
                elif (_frame == "bootstrap5"):
                    backend.script(Bootstrap5())
            elif (_lib == "php"):
                url = "https://raw.githubusercontent.com/New-Vektor-Group/pkg-repo/main/"+_lib+"/"
                Downloader.download(os.path.join(backend.path, backend.BUILDFOLDER) + "/"+_lib+"/lib/",url,_frame,_lib)

        elif args[i] in commands["less"]:
            _path = os.getcwd()
            _weboa = Processing.Weboa_Open()
            Printer.log(_weboa)
            Printer.log(_path)
            Printer.log(glob.glob(_path + "/css/*.less"))
            if(_weboa):
                while True:
                    for i in glob.glob(_path + "/css/*.less"):
                        if not Processing.is_file_changed(_weboa, i, precss="less"):
                            continue
                        Processing.pre_css(_weboa, i, precss="less")
                        waitfor(0.5)
                    waitfor(2)

        elif args[i] in commands["sass"]:
            _path = os.getcwd()
            _weboa = Processing.Weboa_Open()
            _warning_was = False
            if(_weboa):
                while True:
                    for i in glob.glob(_path + "/css/*.scss"):
                        if (not Processing.is_file_changed(_weboa, i, precss="scss")):
                            continue
                        Processing.pre_css(_weboa, i, precss="scss")
                    for i in glob.glob(_path + "/css/*.sass"):
                        if (not Processing.is_file_changed(_weboa, i, precss="sass")):
                            continue
                        _proc = Processing.pre_css(_weboa, i, precss="sass")
                        if not _proc:
                            if not _warning_was:
                                Printer.warning(f"{precss} compiled with an error!")
                                _warning_was = True
                        else:
                            _warning_was = False


        elif args[i] in commands["init"]:
            _path = os.getcwd()
            _build_folder = _path + "/"

            try:
                if (args[i] == commands["init"][0]):
                    _build_folder += args[i + 1]
                    os.mkdir(_build_folder)
            except IndexError:
                Printer.error("Index Error")

            Processing.Save_Path(_path)
            try:
                if commands["langs"][0] in args:
                    lindex = args.index(commands["langs"][0])
                elif commands["langs"][1] in args:
                    lindex = args.index(commands["langs"][1])
                else:
                    lindex = False

                if(lindex):
                    langs = args[lindex + 1]
                    Printer.info(f"Langs {langs}")
                    langs = langs.split(",")
                else:
                    langs = ("ru", "en")
            except IndexError:
                langs = ("ru","en")
                Printer.error("Index Error [langs]")

            precss = "css"
            try:
                if commands["css"][0] in args:
                    cssindex = args.index(commands["css"][0])
                    precss = args[cssindex+1]
                    Printer.info(f"Css {precss}")
            except IndexError:
                Printer.error("Index Error [css]")

            php=PHP(path="", langs=langs, BUILDFOLDER=_build_folder)
            php.FS()
            php.index()
            php.language()
            php.controller()
            php.project()
            php.ico()
            php.css(precss)
            php.robots()
            php.js()
            php.img()
            php.readme()
            php.gitignore()

if(__name__=="__main__"):
    runcli()