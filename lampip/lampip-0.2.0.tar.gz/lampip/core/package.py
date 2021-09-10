import os
import os.path as op
import shutil
import sys
from datetime import datetime
from tempfile import TemporaryDirectory

import boto3
import sh
from termcolor import cprint

from .cloudformation import get_cf_resources
from .config import Config


def _docker(*args):
    cprint("$", "red", end=" ")
    cprint("docker " + " ".join(args), "green")
    p = None
    try:
        p = sh.docker(*args, _out=sys.stdout, _err=sys.stderr, _bg=True)
        p.wait()
    except KeyboardInterrupt:
        if p is not None:
            p.signal(2)
        sys.exit(2)


def _target_zip_basename(layername: str, ver: str) -> str:
    ts = round(datetime.utcnow().timestamp())
    return f"{layername}_{ts}_{ver}.zip"


def _build_cmd(zipbasename, cfg: Config):
    chains = []

    # ==========================================
    # COPY files on /volumepoint/other_resources
    # ==========================================
    chains.extend(["(test -d /other_resources && cp -RT /other_resources . || echo)"])

    # ===========
    # PIP INSTALL
    # ===========
    chains.extend(
        [
            "mkdir -p python",
            "pip3 install --no-cache-dir -r /volumepoint/requirements.txt -t python",
            "cd python",
        ]
    )

    # ====================================
    # REMOVE UNNECESSARY SNIPPETS OR FILES
    # ====================================
    if cfg.shrink.plotly.remove_jupyterlab_plotly:
        chains.append("(test -d jupyterlab_plotly && rm -rf jupyterlab_plotly || echo)")
    if cfg.shrink.plotly.remove_data_docs:
        chains.append(
            r'''(test -d plotly && (find plotly/validators -name '*.py' | xargs sed --in-place -z -E -e 's/kwargs\.pop\([[:space:]]*"data_docs",[[:space:]]*""".*""",?[[:space:]]*\)/kwargs.pop("data_docs", "")/') || echo)'''  # noqa
        )
    if cfg.shrink.remove_dist_info:
        chains.append("(find . -name '*.dist-info' | xargs rm -rf)")
    chains.append("(find . -name '__pycache__' | xargs rm -rf)")

    # =====
    # PATCH
    # =====
    if cfg.shrink.compile and cfg.shrink.compile_optimize_level >= 2:
        # Compile with optimize_level=2 remove docstrings on python code; and __doc__ attributes gets to be None,
        # Affected by this behavior some codes raises errors.
        chains.append(
            r"""(test -d numpy && (find numpy -name '*.py' | xargs sed --in-place -e 's/dispatcher\.__doc__/""/g') || echo)"""  # noqa
        )

    # =======
    # COMPILE
    # =======
    if cfg.shrink.compile:
        chains.extend(
            [
                f"""python -c 'import compileall; compileall.compile_dir(".", maxlevels=20, optimize={cfg.shrink.compile_optimize_level}, force=True, legacy=True, quiet=2)'""",  # noqa
                "(find . -name '*.py' | xargs rm -rf)",
            ]
        )

    # ===
    # ZIP
    # ===
    chains.extend(
        [
            "cd ..",
            "mkdir -p /volumepoint/dist",
            f"zip -r9 --quiet /volumepoint/dist/{zipbasename} .",
        ]
    )

    return " && ".join(chains)


def _make_package(zipbasename: str, ver: str, cfg: Config):
    """Run `pip install' in the docker container and zip artifacts."""
    cprint(f"Start to make {op.join('dist', zipbasename)}", "green")
    if op.exists(op.join("dist", zipbasename)):
        print(f"SKIP: {op.join('dist', zipbasename)} already exists")
        return
    with TemporaryDirectory() as tmpdir:
        curdir = op.abspath(os.curdir)
        # In order to follow symbolic links, copy files on ./other_resources to tmpdir
        os.makedirs(op.join(curdir, "other_resources"), exist_ok=True)
        other_resources_copy_dir = op.join(tmpdir, "other_resources_copy_dir")
        shutil.copytree(
            op.join(curdir, "other_resources"), other_resources_copy_dir, symlinks=False
        )
        _docker(
            "run",
            "--rm",
            "-v",
            f"{curdir}:/volumepoint",
            "-v",
            f"{other_resources_copy_dir}:/other_resources",
            f"lambci/lambda:build-python{ver}",
            "sh",
            "-c",
            _build_cmd(zipbasename, cfg),
        )
    print(f"DONE: {op.join('dist', zipbasename)} created")


def _full_layername(layername: str, ver: str):
    suffix = "-py" + ver.replace(".", "")
    return layername + suffix


def _upload_package(zipbasename: str, ver: str, full_layername: str, description: str):
    cf_resources = get_cf_resources()
    s3 = boto3.resource("s3")
    cprint(f"Start to upload {op.join('dist', zipbasename)}", "green")

    bucketname = cf_resources["DeploymentBucketName"]
    s3.Bucket(bucketname).upload_file(op.join("dist", zipbasename), zipbasename)
    print(f"Put the package file: s3://{bucketname}/{zipbasename}")

    lambdafunc = boto3.client("lambda")
    res = lambdafunc.publish_layer_version(
        LayerName=full_layername,
        Description=description,
        Content={
            "S3Bucket": bucketname,
            "S3Key": zipbasename,
        },
        CompatibleRuntimes=[f"python{ver}"],
    )
    print(f"Publish the custom layer: {res['LayerVersionArn']}")

    print(f"DONE: {op.join('dist', zipbasename)} created")


def deploy_package(cfg: Config, upload_also=True):
    """Run make_package & upload_package according in accordance with config."""
    for ver in cfg.pyversions:
        # ex. NAME_MD5SUM_py3x.zip
        zipbasename = _target_zip_basename(cfg.layername, ver)
        # ex. NAME-py3x
        fullname = _full_layername(cfg.layername, ver)
        _make_package(zipbasename, ver, cfg)
        if upload_also:
            _upload_package(zipbasename, ver, fullname, cfg.description)
