from __future__ import absolute_import
from __future__ import unicode_literals

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Dict
from typing import List
from typing import Optional

from cleo.io.io import IO
from cleo.io.null_io import NullIO

from poetry.core.factory import Factory as BaseFactory
from poetry.core.pyproject.profiles import ProfilesActivationData
from poetry.core.pyproject.toml import PyProject
from poetry.core.toml.file import TOMLFile

from .config.config import Config
from .config.file_config_source import FileConfigSource
from .locations import CONFIG_DIR
from .packages.locker import Locker
from .packages.project_package import ProjectPackage
from .plugins.plugin_manager import PluginManager
from .poetry import Poetry
from .repositories.pypi_repository import PyPiRepository

if TYPE_CHECKING:
    from .repositories.legacy_repository import LegacyRepository


class Factory(BaseFactory):
    """
    Factory class to create various elements needed by Poetry.
    """

    def create_poetry_for_pyproject(
            self, project: PyProject, *,
            with_groups: bool = True,
            io: Optional[IO] = None,
            disable_plugins: bool = False):

        base_poetry = super(Factory, self).create_poetry_for_pyproject(project, with_groups=with_groups)
        return self._upgrade(base_poetry, io, disable_plugins)

    def create_poetry(
            self,
            cwd: Optional[Path] = None,
            io: Optional[IO] = None,
            disable_plugins: bool = False,
            profiles: Optional[ProfilesActivationData] = None
    ) -> Poetry:
        base_poetry = super(Factory, self).create_poetry(cwd, profiles=profiles)
        return self._upgrade(base_poetry, io, disable_plugins)

    def _upgrade(
            self,
            base_poetry: Poetry,
            io: Optional[IO] = None,
            disable_plugins: bool = False):

        if io is None:
            io = NullIO()

        locker = Locker(
            base_poetry.pyproject.project_management_files / "lock.toml", base_poetry.local_config
        )

        # Loading global configuration
        config = self.create_config(io)

        # Loading local configuration

        def apply_config(p: PyProject):
            if p.parent:
                apply_config(p.parent)

            local_config_file = TOMLFile(base_poetry.pyproject.project_management_files / "config.toml")
            if local_config_file.exists():
                if io.is_debug():
                    io.write_line(
                        "Loading configuration file {}".format(local_config_file.path)
                    )

                config.merge(local_config_file.read())

        apply_config(base_poetry.pyproject)

        # Load local sources
        repositories = {}
        existing_repositories = config.get("repositories", {})
        for source in base_poetry.pyproject.poetry_config.get("source", []):
            name = source.get("name")
            url = source.get("url")
            if name and url:
                if name not in existing_repositories:
                    repositories[name] = {"url": url}

        config.merge({"repositories": repositories})

        poetry = Poetry(
            base_poetry.file.path,
            base_poetry.pyproject,
            base_poetry.package,
            locker,
            config,
        )

        # Configuring sources
        self.configure_sources(
            poetry, poetry.local_config.get("source", []), config, io
        )

        plugin_manager = PluginManager("plugin", disable_plugins=disable_plugins)
        plugin_manager.load_plugins()
        poetry.set_plugin_manager(plugin_manager)
        plugin_manager.activate(poetry, io)

        return poetry

    @classmethod
    def get_package(cls, name: str, version: str) -> ProjectPackage:
        return ProjectPackage(name, version, version)

    @classmethod
    def create_config(cls, io: Optional[IO] = None) -> Config:
        if io is None:
            io = NullIO()

        config = Config()

        # Load global config
        config_file = TOMLFile(Path(CONFIG_DIR) / "config.toml")
        if config_file.exists():
            if io.is_debug():
                io.write_line(
                    "<debug>Loading configuration file {}</debug>".format(
                        config_file.path
                    )
                )

            config.merge(config_file.read())

        config.set_config_source(FileConfigSource(config_file))

        # Load global auth config
        auth_config_file = TOMLFile(Path(CONFIG_DIR) / "auth.toml")
        if auth_config_file.exists():
            if io.is_debug():
                io.write_line(
                    "<debug>Loading configuration file {}</debug>".format(
                        auth_config_file.path
                    )
                )

            config.merge(auth_config_file.read())

        config.set_auth_config_source(FileConfigSource(auth_config_file))

        return config

    @classmethod
    def configure_sources(
            cls, poetry: "Poetry", sources: List[Dict[str, str]], config: "Config", io: "IO"
    ) -> None:
        for source in sources:
            repository = cls.create_legacy_repository(source, config)
            is_default = source.get("default", False)
            is_secondary = source.get("secondary", False)
            if io.is_debug():
                message = "Adding repository {} ({})".format(
                    repository.name, repository.url
                )
                if is_default:
                    message += " and setting it as the default one"
                elif is_secondary:
                    message += " and setting it as secondary"

                io.write_line(message)

            poetry.pool.add_repository(repository, is_default, secondary=is_secondary)

        # Put PyPI last to prefer private repositories
        # unless we have no default source AND no primary sources
        # (default = false, secondary = false)
        if poetry.pool.has_default():
            if io.is_debug():
                io.write_line("Deactivating the PyPI repository")
        else:
            default = not poetry.pool.has_primary_repositories()
            poetry.pool.add_repository(PyPiRepository(), default, not default)

    @classmethod
    def create_legacy_repository(
            cls, source: Dict[str, str], auth_config: Config
    ) -> "LegacyRepository":
        from .repositories.legacy_repository import LegacyRepository
        from .utils.helpers import get_cert
        from .utils.helpers import get_client_cert

        if "url" in source:
            # PyPI-like repository
            if "name" not in source:
                raise RuntimeError("Missing [name] in source.")
        else:
            raise RuntimeError("Unsupported source specified")

        name = source["name"]
        url = source["url"]

        return LegacyRepository(
            name,
            url,
            config=auth_config,
            cert=get_cert(auth_config, name),
            client_cert=get_client_cert(auth_config, name),
        )

    @classmethod
    def create_pyproject_from_package(
            cls, package: "ProjectPackage", path: "Path"
    ) -> None:
        import tomlkit

        from poetry.layouts.layout import POETRY_DEFAULT

        pyproject = tomlkit.loads(POETRY_DEFAULT)
        content = pyproject["tool"]["poetry"]

        content["name"] = package.name
        content["version"] = package.version.text
        content["description"] = package.description
        content["authors"] = package.authors

        dependency_section = content["dependencies"]
        dependency_section["python"] = package.python_versions

        for dep in package.requires:
            constraint = tomlkit.inline_table()
            if dep.is_vcs():
                constraint[dep.vcs] = dep.source_url

                if dep.reference:
                    constraint["rev"] = dep.reference
            elif dep.is_file() or dep.is_directory():
                constraint["path"] = dep.source_url
            else:
                constraint["version"] = dep.pretty_constraint

            if not dep.marker.is_any():
                constraint["markers"] = str(dep.marker)

            if dep.extras:
                constraint["extras"] = list(sorted(dep.extras))

            if len(constraint) == 1 and "version" in constraint:
                constraint = constraint["version"]

            dependency_section[dep.name] = constraint

        path.joinpath("pyproject.toml").write_text(
            pyproject.as_string(), encoding="utf-8"
        )
