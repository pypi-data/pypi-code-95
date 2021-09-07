import click

from savvihub.cli._base import VesslGroup, vessl_argument
from savvihub.cli._util import (
    Endpoint,
    generic_prompter,
    print_data,
    print_table,
    print_volume_files,
    prompt_choices,
)
from savvihub.cli.organization import organization_name_option
from savvihub.dataset import (
    copy_dataset_volume_file,
    create_dataset,
    delete_dataset_volume_file,
    download_dataset_volume_file,
    list_dataset_volume_files,
    list_datasets,
    read_dataset,
    upload_dataset_volume_file,
)


def dataset_name_prompter(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    datasets = list_datasets()
    return prompt_choices("Dataset", [x.name for x in datasets])


@click.command(name="dataset", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=dataset_name_prompter
)
@organization_name_option
def read(name: str):
    dataset = read_dataset(dataset_name=name)
    print_data(
        {
            "ID": dataset.id,
            "Name": dataset.name,
            "Organization": dataset.organization.name,
            "Versioning": dataset.is_version_enabled,
            "Volume ID": dataset.volume_id,
            "Source": dataset.source.type,
        }
    )
    print(
        f"For more info: {Endpoint.dataset.format(dataset.organization.name, dataset.name)}"
    )


@cli.vessl_command()
@organization_name_option
def list():
    datasets = list_datasets()
    print_table(
        datasets,
        ["ID", "Name", "Status", "Files", "Source"],
        lambda x: [x.id, x.name, x.status, x.file_count, x.source.type],
    )


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=generic_prompter("Dataset name")
)
@click.option("-m", "--description", type=click.STRING)
@click.option(
    "-e",
    "--external-path",
    type=click.STRING,
    help="AWS S3 or Google Cloud Storage bucket URL (starts with `s3://` or `gs://`).",
)
@click.option("--aws-role-arn", type=click.STRING, help="Required for S3 datasets.")
@click.option("--enable-versioning", is_flag=True)
@click.option(
    "--version-path",
    type=click.STRING,
    help="Required to version AWS S3 or Google Cloud Storage dataset.",
)
@organization_name_option
def create(
    name: str,
    description: str,
    external_path: str,
    aws_role_arn: str,
    enable_versioning: bool,
    version_path: str,
):
    dataset = create_dataset(
        dataset_name=name,
        description=description,
        is_version_enabled=enable_versioning,
        external_path=external_path,
        aws_role_arn=aws_role_arn,
        version_path=version_path,
    )
    print(
        f"Created '{dataset.name}'."
        f"For more info: {Endpoint.dataset.format(dataset.organization.name, dataset.name)}"
    )


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=dataset_name_prompter
)
@click.option("-p", "--path", type=click.Path(), default="", help="Defaults to root.")
@click.option("-r", "--recursive", is_flag=True)
@organization_name_option
def list_files(
    name: str,
    path: str,
    recursive: bool,
):
    files = list_dataset_volume_files(
        dataset_name=name,
        path=path,
        need_download_url=False,
        recursive=recursive,
    )
    print_volume_files(files)


@cli.vessl_command()
@vessl_argument(
    "name",
    type=click.STRING,
    required=True,
    prompter=dataset_name_prompter,
)
@vessl_argument(
    "source",
    type=click.Path(exists=True),
    required=True,
    prompter=generic_prompter("Source path"),
)
@vessl_argument(
    "dest",
    type=click.Path(),
    required=True,
    prompter=generic_prompter("Destination path"),
)
@organization_name_option
def upload(name: str, source: str, dest: str):
    upload_dataset_volume_file(
        dataset_name=name,
        source_path=source,
        dest_path=dest,
    )
    print(f"Uploaded {source} to {dest}.")


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=dataset_name_prompter
)
@vessl_argument(
    "source", type=click.Path(), required=True, prompter=generic_prompter("Source path")
)
@vessl_argument(
    "dest",
    type=click.Path(),
    required=True,
    prompter=generic_prompter("Destination path"),
)
@organization_name_option
def download(name: str, source: str, dest: str):
    download_dataset_volume_file(
        dataset_name=name,
        source_path=source,
        dest_path=dest,
    )
    print(f"Downloaded {source} to {dest}.")


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=dataset_name_prompter
)
@vessl_argument(
    "source", type=click.Path(), required=True, prompter=generic_prompter("Source path")
)
@vessl_argument(
    "dest",
    type=click.Path(),
    required=True,
    prompter=generic_prompter("Destination path"),
)
@click.option("-r", "--recursive", is_flag=True, help="Required if directory.")
@organization_name_option
def copy(name: str, source: str, dest: str, recursive: bool):
    copy_dataset_volume_file(
        dataset_name=name,
        source_path=source,
        dest_path=dest,
        recursive=recursive,
    )
    print(f"Copied {source} to {dest}.")


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=dataset_name_prompter
)
@vessl_argument(
    "path", type=click.Path(), required=True, prompter=generic_prompter("File path")
)
@click.option("-r", "--recursive", is_flag=True, help="Required if directory.")
@organization_name_option
def delete_file(name: str, path: str, recursive: bool):
    files = delete_dataset_volume_file(
        dataset_name=name,
        path=path,
        recursive=recursive,
    )
    print(f"Deleted {path} ({len([x for x in files if not x.is_dir])} file(s)).")
