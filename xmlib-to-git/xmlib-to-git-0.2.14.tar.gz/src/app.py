# -*- coding: utf-8 -*-

import base64, os, shutil, json, datetime, unidecode, git
from git import Repo, RemoteProgress, Actor, Commit
from src.utils import my_json
from src.app_object import Object
from src.app_menu import Menu
from src.web.webpagedef import WebPageDef
from src.web.portal import Portal
from src.seedrecord import SeedRecord
from src.app_event import Event
from src.app_custom_method import CustomMethod

this_dir, this_filename = os.path.split(__file__)


class App(object):
    """
    The application
    """
    header = ""
    footer = ""
    token_names = ""
    git_repo_obj = ""
    git_origin = ""
    git_branch = ""
    show_menus = ""
    use_legacy_header_footer = ""
    is_hidden = ""
    help_field = ""
    is_deployed = ""
    is_managed = ""
    pub_managed = ""
    is_logo_hidden = ""

    def __init__(self, app_name, id, version, packed_id, displayname, description, properties, objects, files,
                 menus, webpages, portals, seeds, dependents, batchs, outfolder, git_repo, creation_date, custom_methods):
        self.id = id
        self.app_name = app_name
        self.version = version
        self.packed_id = packed_id
        self.displayname = displayname
        self.description = description
        if hasattr(properties, "showMenus"):
            self.show_menus = properties.showMenus.cdata
        if hasattr(properties, "useLegacyHeaderFooter"):
            self.use_legacy_header_footer = properties.useLegacyHeaderFooter.cdata
        if hasattr(properties, "isHidden"):
            self.is_hidden = properties.isHidden.cdata
        if hasattr(properties, "helpField"):
            self.help_field = properties.helpField.cdata
        if hasattr(properties, "isDeployed"):
            self.is_deployed = properties.isDeployed.cdata
        if hasattr(properties, "isManaged"):
            self.is_managed = properties.isManaged.cdata
        if hasattr(properties, "header"):
            self.header = base64.b64decode(properties.header.cdata)
        if hasattr(properties, "pubManaged"):
            self.pub_managed = properties.pubManaged.cdata
        if hasattr(properties, "isLogoHidden"):
            self.is_logo_hidden = properties.isLogoHidden.cdata
        if hasattr(properties, "tokenNames"):
            self.token_names = properties.tokenNames.cdata
        self.dependent_defs = properties.dependentDefs.cdata
        if hasattr(properties, "footer"):
            self.footer = base64.b64decode(properties.footer.cdata)
        self.app_directory = "{}/{}".format(outfolder, self.app_name)
        self.objects = objects
        self.files = files
        self.menus = menus
        self.webpages = webpages
        self.portals = portals
        self.seeds = seeds
        self.dependents = dependents
        self.batchs = batchs
        self.git_repo = git_repo
        self.creation_date = creation_date
        self.custom_methods = custom_methods
        # delete all files and folder to make git tracking easyest
        for x in ["hosted_files", "menus", "objects", "pages", "portals",
                  "seeds"]:
            if os.path.exists("{}/{}".format(self.app_directory, x).encode('utf-8')):
                shutil.rmtree("{}/{}".format(self.app_directory, x).encode('utf-8'))

        for x in ["README.md", "MENUS.md", "footer.html", "header.html", "app.xml"]:
            if os.path.exists("{}/{}".format(self.app_directory, x).encode('utf-8')):
                os.remove("{}/{}".format(self.app_directory, x))
        if not os.path.exists(self.app_directory.encode('utf-8')):
            os.makedirs(self.app_directory.encode('utf-8'))

    def check_git_exists(self):
        if not os.path.exists(self.app_directory + "/.git"):
            # os.makedirs(self.app_directory)
            self.git_repo_obj = Repo.init(self.app_directory)
            self.git_origin = self.git_repo_obj.create_remote('origin', url=self.git_repo)
            # self.git_repo_obj\
            #     .create_head('master', self.git_origin.refs.master)\
            #     .set_tracking_branch(self.git_origin.refs.master)\
            #     .checkout()
        else:
            self.git_repo_obj = Repo(self.app_directory)
            self.git_origin = self.git_repo_obj.remote('origin')

        self.git_repo_obj.remotes.origin.push("--all")

    def git_set_branch(self, customer_id=None):
        customer_name = "master"
        if customer_id:
            file_id = json.load(open("./src/utils/customer.json"))

            for i in file_id:
                if i['id'] == int(customer_id):
                    customer_name = i["name"] \
                        .lower() \
                        .replace(' ', '_') \
                        .replace('-', '_')
                    break
            customer_name = unidecode.unidecode(customer_name)
        try:
            self.git_repo_obj.git.checkout(customer_name)
        except git.exc.GitCommandError:
            self.git_repo_obj.git.checkout('-b', customer_name)
        self.git_branch = customer_name

    def commit_tag_push(self):
        repo = self.git_repo_obj
        # add all changes
        repo.git.add(A=True)
        # tree = repo.index.write_tree()

        # create commit with xml file's date

        # Committer and Author
        cr = repo.config_reader()
        committer = Actor.committer(cr)
        author = Actor.author(cr)

        date_creation = datetime.datetime.fromtimestamp(self.creation_date)
        date_creation_git = date_creation.replace(microsecond=0).isoformat()

        # offset = altzone
        # author_time, author_offset = date_creation, offset
        # committer_time, committer_offset = date_creation, offset

        message = "Commit automatique du " + date_creation.strftime('%d/%m/%Y')

        # os.environ["GIT_AUTHOR_DATE"] = str(date_creation)
        # os.environ["GIT_COMMITTER_DATE"] = str(date_creation)

        # Do the commit thing.
        commit = repo.index.commit(message,
                                   author=author,
                                   committer=committer,
                                   commit_date=date_creation_git,
                                   author_date=date_creation_git)

        # Create TAG if version changed
        repo.remotes.origin.push(self.git_branch)
        tags = repo.tags
        if self.version not in tags:
            repo.create_tag(self.version, message='Automatic tag "{0}"'.format(self.version))
            repo.remotes.origin.push(self.version)

        # Do the push
        repo.remotes.origin.push(self.git_branch)

    def to_file(self):
        """
        Write in files application's parameters
        - README.md -> technical informations
        - header.js -> header
        - footer.js -> footer
        :return:
        """
        readme = open("{}/README.md".format(self.app_directory), 'w+', encoding='utf-8')
        with readme:
            # nom de l'src
            readme.write("# {}\n".format(self.displayname))
            readme.write("version {}\n\n".format(self.version))
            # Description
            readme.write("## Description\n")
            readme.write(self.description)
            # Informations
            readme.write("\n\n## Informations\n")
            readme.write("- id : {}\n".format(self.id))
            readme.write("- packedId : {}\n".format(self.packed_id))
            readme.write("\nInfos déploiement :\n")
            readme.write("- [{}] showMenu \n".format("X" if self.show_menus == "true" else " "))
            readme.write(
                "- [{}] useLegacyHeaderFooter\n".format("X" if self.use_legacy_header_footer == "true" else " "))
            readme.write("- [{}] isHidden\n".format("X" if self.is_hidden == "true" else " "))
            readme.write("- [{}] helpField\n".format("X" if self.help_field == "true" else " "))
            readme.write("- [{}] isDeployed\n".format("X" if self.packed_id == "true" else " "))

            # Dependants objects
            readme.write("\n## Objets dépendants:\n")
            json_path = os.path.join(this_dir, "utils", "objects_dict.json")
            objects_dict = json.load(open(json_path))
            readme.write("|Id d'origine|Id|Nom|Nom d'intégration|\n"
                         "|---|---|---|---|\n")
            # for x in self.dependent_defs.split(","):
            #     if len(x) > 0:
            #         obj = my_json.find_in_json(objects_dict, x)
            #         if obj:
            #             readme.write("|{}|{}|{}|{}|\n"
            #                          .format(obj["origId"], x, obj["name"], obj["defName"]))
            #         else:
            #             readme.write("| |{}| | |\n".format(x))

            # write in json file
            jsontest = json.dumps(objects_dict)
            with open(json_path, "w", encoding='utf-8') as f:
                f.write(jsontest)

            del jsontest

            if self.dependents:
                for dependent in self.dependents:
                    obj = my_json.find_in_json(objects_dict, dependent["id"])
                    readme.write("|{}|{}|{}|{}|\n"
                                 .format(dependent["origId"], dependent["id"], dependent.SingularName.cdata,
                                         dependent["objDefName"]))

            # Champs de fusion
            readme.write("\n## Champs de fusion :\n")
            for x in self.token_names.split("|"):
                if len(x) > 0:
                    readme.write("- {}\n".format(x))

        if self.header:
            header = open("{}/header.html".format(self.app_directory), 'w+', encoding='utf-8')
            with header:
                header.write(self.header.decode("utf-8"))

        if self.footer:
            footer = open("{}/footer.html".format(self.app_directory), 'w+', encoding='utf-8')
            with footer:
                footer.write(self.footer.decode("utf-8"))

        self.create_hosted_files()

        self.create_objects()

        if self.menus:
            self.create_menus()

        if self.webpages:
            self.create_web_pages()

        if self.portals:
            self.create_portals()

        if self.seeds:
            self.create_seeds()

        if self.batchs:
            self.create_batchs()
        
        if self.custom_methods:
            self.create_custom_methods()

        return self.app_directory

    def create_objects(self):
        # objets de l'application
        for appObject in self.objects:
            new_object = Object(appObject, self.app_directory)
            new_object.create()

    def create_menus(self):
        # Create a menu folder + menus
        # create a file MENUS.md with tree menu
        path = "{}/menus".format(self.app_directory)
        if not os.path.exists(path.encode('utf-8')):
            os.makedirs(path.encode('utf-8'))
        menu_file = open("{}/MENUS.md".format(self.app_directory), "w+", encoding='utf-8')
        menu_file.write("## Menus\n\n```\n.\n")
        for menu in self.menus:
            new_menu = Menu(menu, path)
            new_menu.to_file()
            menu_file.write(new_menu.get_menus(self.menus))
        menu_file.write("```\n")



    def create_hosted_files(self):
        ### HOSTED FILES
        hosted_files_dir = "{}/hosted_files".format(self.app_directory)
        for file in self.files:
            if not os.path.exists(hosted_files_dir.encode('utf-8')):
                os.mkdir(hosted_files_dir.encode('utf-8'))
                os.mkdir("{}/css".format(hosted_files_dir).encode('utf-8'))
                os.mkdir("{}/js".format(hosted_files_dir).encode('utf-8'))
                os.mkdir("{}/images".format(hosted_files_dir).encode('utf-8'))

            folder = ""
            ext = ""
            is_image = False

            if file["contentType"] == "text/css":
                folder = ext = "css"
            elif file["contentType"] == "application/javascript":
                folder = ext = "js"
            elif file["contentType"] == "application/x-javascript":
                folder = "js"
                ext = "min.js"
            elif file["contentType"] == "image/png":
                folder = "images"
                ext = "png"
                is_image = True
            elif file["contentType"] == "image/jpeg":
                folder = "images"
                ext = "jpg"
                is_image = True

            if folder and not is_image:
                with open("{}/{}/#HOSTED_FILE.{}-{}.{}".format(hosted_files_dir, folder, file["origId"], file.DisplayName.cdata
                        .replace("/", "-")
                        .replace(" ", "_")
                        .replace("\\", "-")
                        .replace("&", "")
                        .replace("!", "")
                        , ext), 'w+', encoding='utf-8') as readme:
                    file_content = base64.b64decode(file.RawData.cdata).decode("iso8859_15", "ignore")
                    readme.write(file_content)
            elif folder and is_image:
                with open("{}/{}/#HOSTED_FILE.{}-{}.{}".format(hosted_files_dir, folder,file["origId"], file.DisplayName.cdata
                        .replace("/", "-")
                        .replace(" ", "_")
                        .replace("\\", "-")
                        .replace("&", "")
                        .replace("!", "")
                        , ext), 'wb') as readme:
                    if hasattr(file, "RawData"):
                        file_content = base64.b64decode(file.RawData.cdata)
                        readme.write(file_content)

    def create_web_pages(self):
        # pages
        for webpage in self.webpages:
            new_webpagedef = WebPageDef(webpage, self.app_directory)
            new_webpagedef.to_file()

    def create_portals(self):
        # portals
        for portal in self.portals:
            new_portal = Portal(portal, self.app_directory)
            new_portal.to_file()

    def create_seeds(self):
        # seed records
        for seed in self.seeds:
            new_seed = SeedRecord(seed, self.app_directory)
            new_seed.to_file()

    def create_batchs(self):
        # jobs
        for batch in self.batchs:
            event = Event(batch, self.app_directory + "/jobs/")
            event.to_file()
    
    def create_custom_methods(self):
        for method in self.custom_methods:
            event = CustomMethod(method, self.app_directory + "/custom_methods/")
            event.to_file()


class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")
