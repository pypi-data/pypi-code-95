import subprocess

import click
from typing import List

from loguru import logger

from pbt.config import PBTConfig
from pbt.diff import RemoteDiff
from pbt.package import search_packages, topological_sort, update_versions
from pbt.pypi import PyPI


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "-p",
    "--package",
    multiple=True,
    help="Specify the package that we want to build. If empty, build all packages",
)
@click.option(
    "-e",
    "--editable",
    is_flag=True,
    help="Whether to install dependencies in editable mode",
)
@click.option("--cwd", default="", help="Override current working directory")
def make(package: List[str], editable: bool = False, cwd: str = ""):
    """Make package"""
    pbt_cfg = PBTConfig.from_dir(cwd)
    packages = search_packages(pbt_cfg)

    if len(package) == 0:
        make_packages = set(packages.keys())
    else:
        make_packages = set(package)

    if len(make_packages.difference(packages.keys())) > 0:
        raise Exception(
            f"Passing unknown packages: {make_packages.difference(packages.keys())}. Available options: {list(packages.keys())}"
        )

    visited_pkgs = {}
    for pkg_name in make_packages:
        pkg = packages[pkg_name]
        dep_pkgs = pkg.all_inter_dependencies()
        for dep_name in topological_sort(dep_pkgs):
            if dep_name not in visited_pkgs:
                # TODO: optimize this code as we don't need to rebuild if we are install in editable mode
                visited_pkgs[dep_name] = dep_pkgs[dep_name].build(pbt_cfg)
                if visited_pkgs[dep_name] and dep_name in pkg.dependencies:
                    # update if there is a change in the dependency make it no longer compatible,
                    if not pkg.is_package_compatible(dep_pkgs[dep_name]):
                        pkg.update_package_version(dep_pkgs[dep_name])
            if visited_pkgs[dep_name]:
                pkg.install_dep(
                    dep_pkgs[dep_name], pbt_cfg, editable=editable, no_build=True
                )

    update_versions(list(visited_pkgs.keys()), packages)
    return


@click.command()
@click.option("--cwd", default="", help="Override current working directory")
def update(cwd: str = ""):
    pbt_cfg = PBTConfig.from_dir(cwd)
    packages = search_packages(pbt_cfg)
    update_versions(list(packages.keys()), packages, force=True)


@click.command()
@click.option(
    "-p",
    "--package",
    multiple=True,
    help="Specify the package that we want to build. If empty, build all packages",
)
@click.option("--cwd", default="", help="Override current working directory")
def publish(package: str, cwd: str = ""):
    pbt_cfg = PBTConfig.from_dir(cwd)
    packages = search_packages(pbt_cfg)

    if len(package) == 0:
        publish_packages = set(packages.keys())
    else:
        publish_packages = set(package)

    if len(publish_packages.difference(packages.keys())) > 0:
        raise Exception(
            f"Passing unknown packages: {publish_packages.difference(packages.keys())}. Available options: {list(packages.keys())}"
        )

    all_pub_pkgs = {}
    for pkg_name in publish_packages:
        pkg = packages[pkg_name]
        dep_pkgs = pkg.all_inter_dependencies()

        all_pub_pkgs[pkg.name] = pkg
        all_pub_pkgs.update(dep_pkgs)

    update_versions(all_pub_pkgs.keys(), packages)
    pypi = PyPI.get_instance()
    has_error = False

    all_pub_pkgs = [
        all_pub_pkgs[pkg_name] for pkg_name in topological_sort(all_pub_pkgs)
    ]
    pkg2diff = {}

    for pkg in all_pub_pkgs:
        remote_pkg_version, remote_pkg_hash = pypi.get_latest_version_and_hash(
            pkg.name
        ) or (None, None)
        diff = RemoteDiff.from_pkg(pkg, pbt_cfg, remote_pkg_version, remote_pkg_hash)
        if not diff.is_version_diff and diff.is_content_changed:
            logger.error(
                "Package {} has been modified, but its version hasn't been updated",
                pkg.name,
            )
            has_error = True
        pkg2diff[pkg.name] = diff

    if has_error:
        raise Exception(
            "Stop publishing because some packages have been modified but their versions haven't been updated. Please see the logs for more information"
        )

    for pkg in all_pub_pkgs:
        if pkg2diff[pkg.name].is_version_diff:
            logger.info("Publish package {}", pkg.name)
            pkg.publish()


cli.add_command(make)
cli.add_command(publish)


if __name__ == "__main__":
    cli()
