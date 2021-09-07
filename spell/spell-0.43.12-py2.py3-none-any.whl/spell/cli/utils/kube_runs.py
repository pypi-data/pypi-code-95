import os
import click

import spell.cli.utils  # for __file__ introspection
from spell.cli.utils.cluster_utils import kubectl

runs_manifests_dir = os.path.join(
    os.path.dirname(spell.cli.utils.__file__), "kube_manifests", "spell-run"
)

#########################
# Runs
#########################


# must be executed with elevated permissions (crd)
def add_argo():
    kubectl(
        "apply",
        "-f",
        os.path.join(runs_manifests_dir, "argo"),
        "-n",
        "spell-run",
    )


def create_reg_secret():
    docker_email = click.prompt("Enter your Dockerhub email")
    docker_username = click.prompt("Enter your Dockerhub username")
    docker_pass = click.prompt("Enter your Dockerhub password", hide_input=True)
    # Create secret used by Kaniko to push to a user's registry
    # Delete Secret if it exists
    kubectl(
        "delete",
        "secret",
        "docker-registry",
        "regcred",
        "-n",
        "spell-run",
        "--ignore-not-found",
    )
    kubectl(
        "create",
        "secret",
        "docker-registry",
        "regcred",
        "--docker-server=https://index.docker.io/v1/",
        f"--docker-username={docker_username}",
        f"--docker-password={docker_pass}",
        f"--docker-email={docker_email}",
        "-n",
        "spell-run",
    )

    # Create ConfigMap containing docker username
    # Delete if it exists
    kubectl(
        "delete",
        "configmap",
        "dockerusername",
        "-n",
        "spell-run",
        "--ignore-not-found"
    )
    kubectl(
        "create",
        "configmap",
        "dockerusername",
        f"--from-literal=username={docker_username}",
        "-n",
        "spell-run",
    )
