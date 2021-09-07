import os
import shutil
import tempfile

import click
from indico_install.cluster_manager import ClusterManager
from indico_install.config import D_PATH, REMOTE_TEMPLATES_PATH, yaml
from indico_install.utils import options_wrapper, run_cmd
from indico_install.utils import run_cmd


def helm3_install(dependency, default_values_path):
    """
    Helm3 install a given chart
    """
    click.echo(f"Installing {dependency['name']}")
    if not all(key in dependency.keys() for key in ["name", "repository", "version"]):
        click.secho(f"Unable to install {dependency.get('name')}: expected keys not present")
        return
    default_values = (
        "-f " + str(default_values_path) if default_values_path.is_file() else ""
    )
    repo_name = dependency.get("repoName", f"{dependency['name']}-repository")
    namespace = (
        f"--namespace {dependency.get('namespace')}"
        if dependency.get("namespace")
        else ""
    )
    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as override_yaml:
        override_yaml.write(
            yaml.dump(dependency.get("values", {}), default_flow_style=False).encode(
                "utf-8"
            )
        )
        override_yaml.flush()
        run_cmd(f"helm3 repo add {repo_name} {dependency['repository']}")
        run_cmd("helm3 repo update", silent=True)
        run_cmd(
            f"helm3 install {namespace} {dependency['name']} {repo_name}/{dependency['name']} --create-namespace {default_values} -f {override_yaml.name} --version {dependency['version']}"
        )


def fetch_defaults(remote_path):
    """
    Fetch default helm values from updraft
    """
    remote_helm_values_path = (
        REMOTE_TEMPLATES_PATH + remote_path + "/helm-values.tar.gz"
    )
    local_directory = (
        D_PATH / "helm-values" / "".join(c for c in str(remote_path) if c.isalnum)
    )
    if not local_directory.parent.exists():
        local_directory.parent.mkdir(exist_ok=True, parents=True)
    if local_directory.is_dir():
        shutil.rmtree(local_directory)
    click.secho(
        f"Downloading indico default helm values to {local_directory}", fg="yellow"
    )
    os.makedirs(local_directory, exist_ok=True)
    run_cmd(
        f"wget {remote_helm_values_path} -O - | " f"tar -xz -C {local_directory}",
        silent=False,
    )
    assert (local_directory).is_dir(), f"Unable to download version {remote_path}"
    return local_directory / "helm-values"


@click.command("install")
@click.argument("charts", required=False, nargs=-1)
@click.pass_context
@options_wrapper()
def install(ctx, cluster_manager=None, charts=None, yes=False):
    """
    Install helm charts from sources defined in the 'dependencies' section of the cluster manager config. Install any number of available charts with the CHART argument

    Example 1
    Install the cert-manager helm chart as specified in the cluster manager config:
    indico install cert-manager

    Example 2
    Install all helm charts specified in the cluster manager config:
    indico install
    """
    cluster_manager = cluster_manager or ClusterManager()
    helm_defaults_path = fetch_defaults(cluster_manager.indico_version)
    deps = cluster_manager.cluster_config.get("dependencies", {})
    if not deps:
        click.secho(
            "No helm chart dependencies specified in the cluster manager configmap"
        )
        return
    for dependency in deps:
        if charts and not [
            chart for chart in charts if chart in dependency.get("name")
        ]:
            continue
        if yes or click.confirm(f"Ready to install {dependency.get('name')} chart?"):
            helm3_install(dependency, helm_defaults_path)
