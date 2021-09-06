# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional, List
import os, time

# Pip
from kcu import kpath, strio, sh, kjson
from kdependencies import Dependencies, InstalledPackage

# Local
from .constants import Constants
from .utils import Utils
from .prompt import Prompt
from .texts import new_api, new_class, new_json_class, new_enum, new_license, new_file, new_flow, gitignore, new_readme, updated_readme, new_setup, updated_setup, new_install_dependencies_file, current_version_number, new_requirements_file, AllFileConsts, FileConsts
from .texts.utils import comment_line

# -------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------- class: Flows --------------------------------------------------------- #

class Flows:

    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    # Main

    @classmethod
    def new_package(cls, package_name: Optional[str]):
        input('Ensure you\'re in the correct path: \'{}\''.format(os.getcwd()))

        config = Utils.get_config(True)
        package_name, description = Prompt.new_package(package_name, os.getcwd().split(os.sep)[-1])

        if not os.path.exists(Utils.setup_file_path()):
            Utils.create_file(Utils.setup_file_path(), new_setup(
                package_name=package_name,
                tab_size=config.spaces_per_tab,
                author=config.default_author,
                git_url=Utils.get_git_url(),
                min_python_version=config.default_min_python_version,
                max_python_version=config.default_max_python_version,
                license_str='License :: OSI Approved :: MIT License'
            ))

        if not os.path.exists(Utils.readme_path()):
            cls.create_new_readme(package_name, Utils.get_full_git_repo_name(), description, open=False)

        if not os.path.exists(Utils.gitignore_path()):
            cls.create_new_gitignore(open=False)

        if not os.path.exists(Utils.license_path()):
            Utils.create_file(Utils.license_path(), new_license(config.default_author))

        if not os.path.exists(Utils.demo_path()):
            Utils.create_file(Utils.demo_path())

        cls.create_new_subpackage(os.path.join(package_name, 'models'), create_class=False)
        cls.create_new_subpackage(os.path.join(package_name, 'models/enums'), create_class=False)
        cls.create_new_subpackage(os.path.join(package_name, 'utils'), create_class=True)
        cls.create_new_subpackage(package_name, create_class=True)

    @classmethod
    def upgrade(cls, ensure_path: bool = True, clean_lines: bool = False):
        if ensure_path:
            Utils.ensure_and_get_path()

        if clean_lines:
            cls.clean_lines(ensure_path=False)

        print('Getting dependencies...')
        dependencies = [d for d in Dependencies.get(os.getcwd()) if not d.invalid]

        print('Updating setup.py')
        old_setup_str = strio.load(Utils.setup_file_path())
        updated_setup_str = updated_setup(old_setup_str, Utils.get_config(True).spaces_per_tab, dependencies)
        Utils.create_file(Utils.setup_file_path(), updated_setup_str, overwrite=True)

        print('Updating README.md')
        old_readme_str = strio.load(Utils.readme_path())
        demo_str = strio.load(Utils.demo_path())
        updated_readme_str = updated_readme(old_readme_str, demo_str, dependencies)
        Utils.create_file(Utils.readme_path(), updated_readme_str, overwrite=True)

        # cls.create_install_file(dependencies, open=False)
        cls.create_requirements_file(dependencies, open=False)

    @classmethod
    def publish(cls, ensure_path: bool = True, clean_lines: bool = False, reinstall: bool = True):
        if ensure_path:
            Utils.ensure_and_get_path()

        current_package_name = Utils.get_current_package_name()

        print('Upgrading \'{}\''.format(current_package_name))
        cls.upgrade(ensure_path=False, clean_lines=clean_lines)

        print('Publishing \'{}\' to pypi'.format(current_package_name))
        Utils.publish()

        if reinstall:
            print('Reinstalling \'{}\''.format(current_package_name))
            cls.uninstall(current_package_name)
            cls.install('.')

    @classmethod
    def publish_and_push(cls, message: Optional[str] = None, clean_lines: bool = False):
        cls.publish(ensure_path=True, clean_lines=clean_lines, reinstall=False)
        cls.push(ensure_path=False, clean_lines=False)

        current_package_name = Utils.get_current_package_name()
        print('Reinstalling \'{}\''.format(current_package_name))
        cls.reinstall(current_package_name, version=current_version_number(Utils.setup_file_path()), max_install_try_count=5)

    @classmethod
    def upgrade_push_install(cls, message: Optional[str] = None, clean_lines: bool = False, reinstall: bool = True):
        Utils.ensure_and_get_path()
        current_package_name = Utils.get_current_package_name()

        print('Upgrading \'{}\''.format(current_package_name))
        cls.upgrade(ensure_path=False, clean_lines=clean_lines)

        if reinstall:
            print('Reinstalling \'{}\''.format(current_package_name))

            cls.uninstall(current_package_name)
            cls.install('.')

        cls.push(ensure_path=False, clean_lines=False)

    @classmethod
    def clean_lines(cls, ensure_path: bool = True):
        if ensure_path:
            Utils.ensure_and_get_path()

        for p in kpath.file_paths_from_folder(os.getcwd(), allowed_extensions=Constants.ALLOWED_EXPENSIONS_TO_CLEAN):
            lower_p = p.lower()
            should_continue = False

            for path_comp in Constants.IGNORED_PATH_COMPONENTS_TO_CLEAN:
                _path_comp = path_comp.lower().strip(os.sep) + os.sep

                if _path_comp in lower_p:
                    should_continue = True

                    break

            if should_continue:
                continue

            with open(p, 'r') as f:
                org_text = f.read()
                text = '\n'.join([l.rstrip() for l in org_text.strip().split('\n')]).strip()

            if org_text != text:
                print('Cleaning: \'{}\''.format(p))

                with open(p, 'w') as f:
                    f.write(text)

    @classmethod
    def migrate_comment_line_len(
        cls,
        line_len: Optional[str]
    ):
        new_command_line_len = int(line_len) if line_len else Utils.get_config(True).comment_line_length
        allowed_extensions = [fc.file_extension for fc in Constants.SUPPORTED_FILE_CONSTS]

        for p in kpath.file_paths_from_folder(os.getcwd(), allowed_extensions=allowed_extensions):
            file_consts = AllFileConsts.PY.value

            for fc in Constants.SUPPORTED_FILE_CONSTS:
                if fc.is_kind(p):
                    file_consts = fc

                    break

            s = strio.load_sync(p)

            for line in s.split('\n'):
                indent_spaces = len(line) - len(line.lstrip())
                line = line.strip()

                if file_consts.is_comment_line(line):
                    comment = line.strip().lstrip(file_consts.comment_starter).rstrip(file_consts.comment_ender).strip().strip(file_consts.comment_line_char).strip()

                    s = s.replace(line, comment_line(
                        comment,
                        line_len=new_command_line_len,
                        file_consts=file_consts,
                        tabs=1,
                        tab_size=indent_spaces
                    ))

            strio.save_sync(p, s)

    # Git

    @classmethod
    def push(cls, message: Optional[str] = None, ensure_path: bool = False, clean_lines: bool = False):
        if ensure_path:
            Utils.ensure_and_get_path()

        if clean_lines:
            cls.clean_lines(ensure_path=False)

        sh.sh('set_git_user', debug=False)
        print(sh.sh('git add .', debug=True))
        print(sh.sh('git commit -a -m \'{}\''.format(message or Utils.get_config(True).default_commit_message), debug=True))
        print(sh.sh('git push', debug=True))

    @staticmethod
    def fetch():
        print(sh.sh('git fetch', debug=True))

    @classmethod
    def pull(cls):
        cls.fetch()
        print(sh.sh('git pull', debug=True))


    # Pip install

    @staticmethod
    def uninstall(package: str):
        print(Utils.pip('uninstall -y {}'.format(package)))

    @staticmethod
    def install(package: str, version: Optional[str] = None, max_try_count: Optional[int] = None):
        package_name = '{}{}'.format(package, '=={}'.format(version) if version else '')
        max_try_count = max_try_count or 1
        current_try_count = 0

        while True:
            current_try_count += 1
            res = Utils.pip('install -U {}'.format(package_name))

            if not res.startswith('ERROR'):
                print(res)
                print('Successfully installed \'{}\''.format(package_name))

                return
            elif current_try_count < max_try_count:
                time.sleep(2)
            else:
                break

        print('ERROR: Could not install \'{}\''.format(package_name))

    @classmethod
    def reinstall(cls, package: str, version: Optional[str] = None, max_install_try_count: Optional[int] = None):
        cls.uninstall(package)
        cls.install(package, version, max_try_count=max_install_try_count)

    # New files

    @staticmethod
    def create_requirements_file(dependencies: Optional[List[InstalledPackage]] = None, open: bool = True):
        file_path = Utils.requirements_path()
        dependencies = dependencies or [d for d in Dependencies.get(os.getcwd()) if not d.invalid]

        if not dependencies:
            if os.path.exists(file_path):
                os.remove(file_path)

            return

        print('Creating \'{}\''.format(Constants.REQUIREMENTS_FILE_NAME))
        Utils.create_file(file_path, new_requirements_file(dependencies), overwrite=True)

        if open:
            Utils.vscode_open(file_path)

    @staticmethod
    def create_install_file(dependencies: Optional[List[InstalledPackage]] = None, open: bool = True):
        file_path = Utils.install_dependencies_path()
        dependencies = dependencies or [d for d in Dependencies.get(os.getcwd()) if not d.invalid]

        if not dependencies:
            if os.path.exists(file_path):
                os.remove(file_path)

            return

        print('Creating \'{}\''.format(Constants.INSTALL_DEPENDENCIES_FILE_NAME))
        Utils.create_file(file_path, new_install_dependencies_file(dependencies), overwrite=True)

        if open:
            Utils.vscode_open(file_path)

    @staticmethod
    def create_new_api(name: str, open: bool = True):
        _, file_path, _, _class = Utils.get_paths_name_class(name)
        config = Utils.get_config(True)
        Utils.create_file(file_path, new_api(_class, tab_size=config.spaces_per_tab, comment_line_len=config.comment_line_length))

        if open:
            Utils.vscode_open(file_path)

    @staticmethod
    def create_new_class(name: str, open: bool = True):
        _, file_path, _, _class = Utils.get_paths_name_class(name)
        config = Utils.get_config(True)
        Utils.create_file(file_path, new_class(_class, tab_size=config.spaces_per_tab, comment_line_len=config.comment_line_length))

        if open:
            Utils.vscode_open(file_path)

    @staticmethod
    def new_class_from_json(json_path: str, name: Optional[str] = None, open: bool = True):
        name = name or json_path.split(os.sep)[-1].split('.')[0]

        _, file_path, _, _class = Utils.get_paths_name_class(name)
        config = Utils.get_config(True)
        Utils.create_file(file_path, new_json_class(_class, kjson.load(json_path), tab_size=config.spaces_per_tab, comment_line_len=config.comment_line_length))

        if open:
            Utils.vscode_open(file_path)

    @staticmethod
    def create_new_enum(name: str, open: bool = True):
        _, file_path, _, _class = Utils.get_paths_name_class(name)

        config = Utils.get_config(True)
        Utils.create_file(file_path, new_enum(_class, tab_size=config.spaces_per_tab, comment_line_len=config.comment_line_length))

        if open:
            Utils.vscode_open(file_path)

    @staticmethod
    def create_new_file(name: str, open: bool = True):
        _, file_path, _, _ = Utils.get_paths_name_class(name)

        config = Utils.get_config(True)
        Utils.create_file(file_path, new_file(tab_size=config.spaces_per_tab, comment_line_len=config.comment_line_length))

        if open:
            Utils.vscode_open(file_path)

    @staticmethod
    def create_new_flow(name: str, open: bool = True):
        _, file_path, _, _ = Utils.get_paths_name_class(name)

        config = Utils.get_config(True)
        Utils.create_file(file_path, new_flow(tab_size=config.spaces_per_tab, comment_line_len=config.comment_line_length))

        if open:
            Utils.vscode_open(file_path)

    @staticmethod
    def create_new_gitignore(open: bool = True):
        Utils.create_file(Utils.gitignore_path(), gitignore)

        if open:
            Utils.vscode_open(Utils.gitignore_path())

    @staticmethod
    def create_new_readme(
        package_name: str,
        full_repo_name: Optional[str] = None,
        description: Optional[str] = None,
        open: bool = False
    ):
        file_path = Utils.readme_path()
        Utils.create_file(file_path, new_readme(package_name=package_name, full_repo_name=full_repo_name, description=description))

        if open:
            Utils.vscode_open(file_path)

    @classmethod
    def create_new_subpackage(cls, relative_folder_path: str, create_class: bool = True):
        _, init_file_path, _, _ = Utils.get_paths_name_class(Utils.init_file_path(relative_folder_path))

        if create_class:
            _, _, class_file_name, _class = Utils.get_paths_name_class(relative_folder_path)
            cls.create_new_class(os.path.join(relative_folder_path, class_file_name), open=False)

            Utils.create_file(init_file_path, 'from .{} import {}'.format(class_file_name, _class))
        else:
            Utils.create_file(init_file_path, '')


# -------------------------------------------------------------------------------------------------------------------------------- #