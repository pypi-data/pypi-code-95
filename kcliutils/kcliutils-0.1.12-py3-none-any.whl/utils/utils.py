# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional, Union, Tuple, List
import os, sys

# Pip
from kcu.sh import sh
from kcu import strio, kjson, kpath

# Local
from .constants import Constants
from .prompt import Prompt
from .config import Config

# -------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------- class: Utils --------------------------------------------------------- #

class Utils:

    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    # CLI

    @staticmethod
    def vscode_open(path: str):
        sh('code --reuse-window {}'.format(path))

    # Python

    @staticmethod
    def python(cmd: str, debug: bool = True) -> str:
        return sh('{} {}'.format(sys.executable, cmd), debug=debug)

    @classmethod
    def pip(cls, cmd: str, debug: bool = True) -> str:
        return cls.python('-m pip {}'.format(cmd), debug=debug)

    @classmethod
    def publish(cls) -> None:
        cls.cleanup()

        # Ensure you have the latest versions of twine, setuptools, and wheel
        print(cls.pip('install --user --upgrade twine setuptools wheel'))
        # Build the package
        print(cls.python('setup.py sdist bdist_wheel'))
        # Upload it to pypi
        print(cls.python('-m twine upload --repository pypi dist/*'))

        cls.cleanup()

    @staticmethod
    def cleanup(root_folder_path: Optional[str] = None) -> None:
        root_folder_path = root_folder_path or os.getcwd()

        for (_, dir_paths, _) in os.walk(root_folder_path):
            for dir_path in dir_paths:
                if dir_path == 'dist' or  dir_path == 'build' or dir_path.endswith('.egg-info'):
                    kpath.remove(os.path.join(root_folder_path, dir_path))

            return


    # Args

    @classmethod
    def has_arg(cls, arg: str) -> bool:
        for passed_arg in cls.get_args(minimum_needed=1):
            if arg.lower() == passed_arg.lower():
                return True

        return False

    @classmethod
    def get_arg(cls, surpress_crash: bool = False) -> Optional[str]:
        args = cls.get_args(minimum_needed=0)

        if not args and not surpress_crash:
            raise ValueError('Argument missing')

        return args[0] if args else None

    @staticmethod
    def get_args(minimum_needed: int = 1) -> List[str]:
        args = sys.argv[1:]

        if len(args) < minimum_needed:
            raise ValueError('Not enough args passed: {} out of {}'.format(len(args), minimum_needed))

        return args


    # Paths

    @classmethod
    def ensure_and_get_path(cls) -> str:
        cwd = os.getcwd()

        if not os.path.exists(cls.setup_file_path()):
            raise ValueError('No \'setup.py\' was found in the current directory')

        return cwd

    @staticmethod
    def create_file(
        file_path: str,
        text: Optional[str] = None,
        overwrite: bool = False
    ) -> bool:
        if not overwrite and os.path.exists(file_path):
            return False

        folder_path = kpath.folder_path_of_file(file_path)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        return strio.save(file_path, text or '')

    @classmethod
    def config_path(cls) -> str:
        return cls.path(Constants.CONFIG_FILE_NAME, cls.home_dir())

    @staticmethod
    def home_dir() -> str:
        return sh('echo $HOME').strip()

    @classmethod
    def readme_path(cls) -> str:
        return os.path.join(os.getcwd(), Constants.README_FILE_NAME)

    @classmethod
    def gitignore_path(cls) -> str:
        return cls.path(Constants.GITIGNORE_FILE_NAME)

    @classmethod
    def install_dependencies_path(cls) -> str:
        return cls.path(Constants.INSTALL_DEPENDENCIES_FILE_NAME)

    @classmethod
    def requirements_path(cls) -> str:
        return cls.path(Constants.REQUIREMENTS_FILE_NAME)

    @classmethod
    def demo_path(cls) -> str:
        return cls.path(Constants.DEMO_FILE_NAME)

    @classmethod
    def license_path(cls) -> str:
        return cls.path(Constants.LICENSE_FILE_NAME)

    @classmethod
    def setup_file_path(cls) -> str:
        return cls.path(Constants.SETUP_FILE_NAME)

    @classmethod
    def init_file_path(cls, base_path: Optional[str] = None) -> str:
        return cls.path(Constants.INIT_PY_FILE_NAME, base_path=base_path)

    @staticmethod
    def path(file_name: str, base_path: Optional[str] = None) -> str:
        return os.path.join(base_path or os.getcwd(), file_name)


    # Git

    @classmethod
    def get_git_username(cls) -> Optional[str]:
        return cls.__get_local_git_username() or cls.__get_local_git_username_from_git_url() or cls.get_config(True).default_author or cls.__get_global_git_username()

    @classmethod
    def get_git_url(cls) -> Optional[str]:
        url = cls.__get_arg_from_file('.git/config', 'url = ')

        return url.replace('.git', '').strip('/') if url else None

    @classmethod
    def get_git_repo_name(cls) -> Optional[str]:
        git_url = cls.get_git_url()

        return git_url.split('/')[-1] if git_url else None

    @classmethod
    def get_full_git_repo_name(cls) -> Optional[str]:
        git_username = cls.__get_local_git_username_from_git_url()

        if not git_username:
            return None

        git_repo_name = cls.get_git_repo_name()

        if not git_repo_name:
            return None

        return '{}/{}'.format(git_username, git_repo_name)

    @classmethod
    def get_config(cls, create_new_if_none: bool = True) -> Optional[Config]:
        config = Config.load(cls.config_path())

        if config:
            try:
                config.validate()
            except:
                if create_new_if_none:
                    print("Config is outdated. Create new one. Old config path '{}'".format(cls.config_path()))

                config = None

        return config if config else cls.__create_new_config() if create_new_if_none else None

    @classmethod
    def __create_new_config(
        cls,
        default_author: Optional[str] = None,
        default_git_message: Optional[str] = None,
        default_spaces_per_tab: Optional[int] = None,
        default_comment_line_length: Optional[int] = None,
    ) -> Config:
        default_author, default_commit_message, min_v, max_v, spaces_per_tab, comment_line_length = Prompt.config(
            default_author=default_author or cls.__get_local_git_username() or cls.__get_global_git_username(),
            default_git_message=default_git_message or Constants.DEFAULT_COMMIT_MESSAGE,
            default_spaces_per_tab=default_spaces_per_tab or Constants.DEFAULT_SPACES_PER_TAB,
            default_comment_line_length=default_comment_line_length or Constants.DEFAULT_COMMENT_LINE_LENGTH
        )

        config = Config(
            default_author=default_author,
            default_commit_message=default_commit_message,
            default_min_python_version=min_v,
            default_max_python_version=max_v,
            spaces_per_tab=spaces_per_tab,
            comment_line_length=comment_line_length
        )

        config.save(cls.config_path())

        return config


    # Strings

    @classmethod
    def get_paths_name_class(cls, file_name_or_path: str) -> Tuple[str, str, str]:
        file_path = os.path.join(os.getcwd(), file_name_or_path.strip().strip(os.path.sep).strip())
        folder_path = kpath.folder_path_of_file(file_path)

        if not file_path.endswith('.py'):
            file_path += '.py'

        file_name = file_path.split(os.path.sep)[-1].replace('.py', '')
        file_class = cls.class_name_from_file_name(file_name)

        return folder_path, file_path, file_name, file_class

    @staticmethod
    def class_name_from_file_name(file_name: str) -> str:
        return ''.join([p.title() for p in file_name.split('_')])

    @classmethod
    def get_current_package_name(cls) -> str:
        setup = strio.load(cls.setup_file_path())

        return setup.split('name =')[-1].split('name=')[-1].split(',')[0].strip().replace('"', '').replace("'", '')


    # ---------------------------------------------------- Private methods --------------------------------------------------- #

    # Git

    @classmethod
    def __get_local_git_username(cls) -> Optional[str]:
        return cls.__get_arg_from_file('.git/config', 'name = ')

    @classmethod
    def __get_global_git_username(cls) -> Optional[str]:
        return cls.__get_arg_from_file(os.path.join(cls.home_dir(), '.gitconfig'), 'name = ')

    @classmethod
    def __get_local_git_username_from_git_url(cls) -> Optional[str]:
        git_url = cls.get_git_url()

        return git_url.split('/')[-2] if git_url else None

    @staticmethod
    def __get_arg_from_file(path: str, splitter: str) -> Optional[str]:
        if not os.path.exists(path):
            return None

        try:
            for line in strio.load(path).split('\n'):
                if splitter in line:
                    return line.split(splitter)[1].strip()
        except Exception as e:
            print(e)

        return None


# -------------------------------------------------------------------------------------------------------------------------------- #