#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import getopt
import untangle
import os
import time
import sys
import shutil
from src.app import App
from src.utils import my_json
from sys import exit
from lxml import etree
this_dir, this_filename = os.path.split(__file__)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    inputfile = ''
    name = ''
    customer = ''
    outfolder = ''
    git_repo = ''
    opts = ''

    try:
        opts, args = getopt.getopt(argv, "hV:f:o:n:g:c", ["help", "version", "file=", "name=", "git-repository-ssh=",
                                                       "out-folder=", "customer="])
    except getopt.GetoptError:
        usage()
        exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            exit()
        elif opt in ("-V", "--version"):
            show_version()
            exit()
        elif opt in ("-f", "--file"):
            inputfile = arg
        elif opt in ("-c", "--customer-id"):
            customer = arg
        elif opt in ("-o", "--out-folder"):
            outfolder = arg
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-g", "--git-repository-ssh"):
            git_repo = arg

    if inputfile == '':
        print("le paramètre -f est obligatoire")
        usage()
        exit(2)
    if name == '':
        print("le paramètre -n est obligatoire")
        usage()
        exit(2)

    check_xml(inputfile)

    parse_xml(inputfile, name, customer, outfolder, git_repo)

def show_version():
    import re
    VERSIONFILE="src/__version__.py"
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))
    print("version {}".format(verstr))


def usage():
    print("usage :")
    print("src -f <input_xml_file> -n <app_name> [-c <customer_id>]")
    print("\t-o, --out-folder=\t\toutput folder")
    print("\t-n, --name=\t\tapplication name, permit application merge in case of name change"
          " (ex core_app")
    print("\t-f, --file=\t\t:XML file to convert")
    print("\t-g, --git-repository-ssh=\t\t: ssh url of the repository")
    print("\t-c, --customer-id=\t\tOPTIONEL : customer id, to create a new branch")


def parse_xml(xml, app_name, customer, outfolder, git_repo):
    time_start = time.perf_counter()
    print("processing {}".format(xml))

    app_tree = untangle.parse(xml)
    date_creation_fichier = os.path.getmtime(xml)
    json_path = os.path.join(this_dir, "utils", "id_dict.json")
    file_id = json.load(open(json_path))

    # objets dépendants -> ajout dans la liste de référence
    if hasattr(app_tree.Application.DependentDefs, "DataObjectDef"):
        for DataObjectDef in app_tree.Application.DependentDefs.DataObjectDef:
            obj = my_json.find_id_json(file_id, DataObjectDef["id"])
            if not obj:
                file_id[DataObjectDef["id"]] = DataObjectDef["origId"]

        jsontest = json.dumps(file_id)
        with open(json_path, "w", encoding='utf-8') as f:
            f.write(jsontest)

        del jsontest, f, file_id

    menus = ""
    hosted = ""
    props = ""
    objects = ""
    webpages = ""
    portals = ""
    seeds = ""
    description = ""
    dependents = ""
    batchs = ""
    methods = ""

    if hasattr(app_tree.Application, "Props"):
        props = app_tree.Application.Props

    if hasattr(app_tree.Application, "DataObjectDefs"):
        if hasattr(app_tree.Application.DataObjectDefs, "DataObjectDef"):
            objects = app_tree.Application.DataObjectDefs.DataObjectDef

    if hasattr(app_tree.Application, "HostedFiles"):
        hosted = app_tree.Application.HostedFiles.HostedFile

    if hasattr(app_tree.Application, "Menus"):
        if hasattr(app_tree.Application.Menus, "Menu"):
            menus = app_tree.Application.Menus.Menu

    if hasattr(app_tree.Application, "WebPageDefs"):
        webpages = app_tree.Application.WebPageDefs.WebPageDef

    if hasattr(app_tree.Application, "Portals"):
        if hasattr(app_tree.Application.Portals, "WebSite"):
            portals = app_tree.Application.Portals.WebSite

    if hasattr(app_tree.Application, "SeedRecords"):
        seeds = app_tree.Application.SeedRecords.DataObject

    if hasattr(app_tree.Application, "Description"):
        description = app_tree.Application.Description.cdata

    if hasattr(app_tree.Application, "DependentDefs"):
        if hasattr(app_tree.Application.DependentDefs, "DataObjectDef"):
            dependents = app_tree.Application.DependentDefs.DataObjectDef

    if hasattr(app_tree.Application, "BatchJobs"):
        if hasattr(app_tree.Application.BatchJobs, "Event"):
            batchs = app_tree.Application.BatchJobs.Event

    if hasattr(app_tree.Application, "CustomMethods"):
        if hasattr(app_tree.Application.CustomMethods, "CustomMethod"):
            methods = app_tree.Application.CustomMethods.CustomMethod

    my_app = App(
        app_name,
        app_tree.Application["id"],
        app_tree.Application["version"],
        app_tree.Application["packedId"],
        app_tree.Application.DisplayName.cdata,
        description,
        props, objects, hosted, menus, webpages, portals, seeds, dependents, batchs,
        outfolder, git_repo, date_creation_fichier, methods
    )
    if git_repo:
        my_app.check_git_exists()
        my_app.git_set_branch(customer)

    app_dir = my_app.to_file()

    text_file = "{}/app.xml".format(app_dir.rstrip("/"))
    shutil.copy(xml, text_file)

    if git_repo:
        my_app.commit_tag_push()
        my_app.git_set_branch()
    time_elapsed = (time.perf_counter() - time_start)

    print("application '{}' generated in {}s".format(app_tree.Application.DisplayName.cdata,
                                                                       round(time_elapsed, 2)))


def check_xml(xml_to_check):
    # parse xml
    try:
        if not os.path.isfile(xml_to_check):
            raise FileNotFoundError

        with open(xml_to_check, "r", encoding='utf-8') as file:
            xml = file.read()
            xml = bytes(bytearray(xml, encoding='utf-8'))
            etree.XML(xml)

    # check for FileNotFoundError
    except FileNotFoundError:
        print("Can't find file {}".format(xml_to_check))
        exit(2)

    # check for file IO error
    except IOError as err:
        print('Invalid File')
        with open('error.log', 'w', encoding='utf-8') as error_log_file:
            error_log_file.write(str(err))

        exit(2)

    # check for XML syntax errors
    except etree.XMLSyntaxError as err:
        print("XML Syntax Error, see error.log")
        with open('error.log', 'w', encoding='utf-8') as error_log_file:
            error_log_file.write(str(err))
        exit(2)

    except Exception as err:
        print("Unknown error, see error.log")
        with open('error.log', 'w', encoding='utf-8') as error_log_file:
            error_log_file.write(str(err))
        exit(2)


if __name__ == "__main__":
    main()
