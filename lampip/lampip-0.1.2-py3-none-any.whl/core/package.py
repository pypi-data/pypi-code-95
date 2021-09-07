import hashlib
import os
import os.path as op
import sys

import boto3
import sh
from termcolor import cprint

from .cloudformation import get_cf_resources


def _md5sum(filename: str) -> str:
    m = hashlib.md5()
    with open(filename, "rb") as fp:
        m.update(fp.read())
    return m.hexdigest()


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
    return layername + "_" + _md5sum("requirements.txt") + "_" + ver + ".zip"


def make_package(layername: str, ver: str):
    """Run `pip install' in the docker container and zip artifacts."""
    assert ver in {"3.6", "3.7", "3.8"}
    zipbasename = _target_zip_basename(layername, ver)
    cprint(f"Start to make {op.join('dist', zipbasename)}", "green")
    if op.exists(op.join("dist", zipbasename)):
        print(f"SKIP: {op.join('dist', zipbasename)} already exists")
        return
    curdir = op.abspath(os.curdir)
    cmd = (
        "mkdir python && "
        "pip3 install -r /volumepoint/requirements.txt -t python && "
        "mkdir -p /volumepoint/dist && "
        f"zip -r9 /volumepoint/dist/{zipbasename} ."
    )
    _docker(
        "run",
        "--rm",
        "-v",
        f"{curdir}:/volumepoint",
        f"lambci/lambda:build-python{ver}",
        "sh",
        "-c",
        cmd,
    )
    print("DONE")


def _full_layername(layername: str, ver: str):
    suffix = "-py" + ver.replace(".", "")
    return layername + suffix


def upload_package(layername: str, ver: str, description: str):
    assert ver in {"3.6", "3.7", "3.8"}
    zipbasename = _target_zip_basename(layername, ver)
    cf_resources = get_cf_resources()
    s3 = boto3.resource("s3")
    cprint(f"Start to upload {op.join('dist', zipbasename)}", "green")

    bucketname = cf_resources["DeploymentBucketName"]
    s3.Bucket(bucketname).upload_file(op.join("dist", zipbasename), zipbasename)
    print(f"Put the package file: s3://{bucketname}/{zipbasename}")

    lambdafunc = boto3.client("lambda")
    full_layername = _full_layername(layername, ver)
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

    print("DONE")
