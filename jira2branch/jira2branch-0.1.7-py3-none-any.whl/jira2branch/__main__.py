import os
import re
import string
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

import click
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
from halo import Halo
from jira import JIRA, JIRAError
from unidecode import unidecode


class JIRACredentials:
    file = ''
    url = ''
    username = ''
    password = ''
    email = ''
    token = ''


def get_credentials() -> Optional[JIRACredentials]:
    secrets = JIRACredentials()
    secrets_file_path = Path.home().joinpath('.j2b')
    secrets_file_name = 'secrets.ini'
    secrets_file = secrets_file_path.joinpath(secrets_file_name)

    secrets.file = str(secrets_file)

    if secrets_file.exists():
        parser = ConfigParser()
        parser.read(secrets_file)
        jira_credentials_section = parser["JIRA CREDENTIALS"]
        secrets.url = jira_credentials_section.get("url")
        secrets.email = jira_credentials_section.get("email")
        secrets.token = jira_credentials_section.get("token")
        secrets.username = jira_credentials_section.get("username")
        secrets.password = jira_credentials_section.get("password")
    else:
        os.makedirs(secrets_file_path, exist_ok=True)
        secrets_file.touch()
        with secrets_file.open('w') as f:
            f.writelines(["[JIRA CREDENTIALS]\n\n",
                          "# url = \n",
                          "# email = \n",
                          "# username = \n",
                          "# password = \n",
                          "# token = \n"])
        click.echo(f'Created empty secrets file under {secrets_file}, please configure it first')
        return None

    return secrets


def get_jira_rest_endpoint() -> JIRA:
    credentials = get_credentials()

    if not credentials and (not credentials.email or not credentials.token):
        click.secho(f"Invalid configuration, please check {credentials.file}", fg='red')
        exit()

    spinner = Halo(text='Connecting to JIRA API', spinner='dots')
    spinner.start()

    jira = None

    if credentials.email and credentials.token:
        try:
            jira = JIRA(credentials.url, basic_auth=(credentials.email, credentials.token),
                        validate=True)
        except JIRAError as error:
            print(error)
            exit(1)
        finally:
            spinner.stop()
        return jira
    elif credentials.username and credentials.password:
        try:
            jira = JIRA(credentials.url, auth=(credentials.username, credentials.password),
                        validate=True)
        except JIRAError as error:
            print(error)
            exit(1)
        finally:
            spinner.stop()
        return jira
    else:
        spinner.stop()
        raise IOError(
            f"Invalid or missing credentials file! Check {credentials.file}, I might have created it for you")


def get_branch_name_from_issue(issue_id: str) -> str:
    jira = None
    issue = None

    try:
        jira = get_jira_rest_endpoint()
    except IOError:
        click.secho('Failed to connect to JIRA, please check configuration', fg='red')
        exit()

    try:
        spinner = Halo(text=f'Fetching JIRA issue {issue_id}', spinner='dots')
        spinner.start()
        issue = jira.issue(issue_id)
        spinner.stop()
    except JIRAError as error:
        print(error)
        exit(1)

    issue_type = issue.fields.issuetype.name

    if 'task' in str.lower(issue_type):
        issue_type = 'feat'
    else:
        issue_type = 'fix'

    title = f'{issue.fields.summary}'

    return Utils.issue_title_to_branch_name(issue_id, title, issue_type)


def create_branch(branch_name, push=False, source_branch='develop'):
    try:
        repo = Repo(Path.cwd())
        #  check if dirty
        if repo.is_dirty():
            click.secho("Current working dir not clean, please commit or stash your changes first", fg='red')
            exit(1)

        #  check if a branch by this name already exists locally
        click.secho('Checking if branch already exists on local repository...')
        if check_if_branch_is_local(repo, branch_name):
            click.secho('Local branch already exists, switching to it', fg='blue')
            switch_to_branch(repo, branch_name)
            exit()

        #  check if a branch by this name already exists on remote
        spinner = Halo(text='Checking if branch already exists on remote repository...', spinner='dots')
        spinner.start()
        if check_if_branch_name_available(repo, branch_name):
            click.secho('Branch name IS available', fg='green')
        else:
            click.secho('A remote branch by that name already exists... aborting', fg='green')
            exit()
        spinner.stop()

        #  we're good to go
        #  create MR branch from latest develop
        try:
            spinner = Halo(text='Fetching all remote branches', spinner='dots')
            spinner.start()
            repo.git.execute(['git', 'fetch', '--all'])
            spinner.stop()
            click.secho('Fetched all remote branches', fg='green')
        except Exception as err:
            print(err)
            spinner.stop()
        try:
            source = f'origin/{source_branch}'
            spinner = Halo(text=f'Creating local branch {branch_name} from {source}', spinner='dots')
            spinner.start()
            repo.git.execute(['git', 'checkout', '-b', branch_name, source])
            spinner.stop()
            click.secho(f'Created local branch {branch_name}', fg='green')
        except Exception as err:
            click.secho('Failed to create local branch...')
            print(err)
            spinner.stop()

        # setting remote tracking branch
        upstream_branch_command = ['git', 'push', '-u', 'origin', f'{branch_name}']
        if push:
            repo.git.execute(upstream_branch_command)
        else:
            click.secho('NOTE: Branch NOT pushed to remote (use with -p to push automatically)', fg='blue')
            click.secho('Whenever you decide to push your changes to remote use the following command:', fg='blue')
            upstream_branch_command = ' '.join(upstream_branch_command)
            click.secho(''.ljust(len(upstream_branch_command), '#'))
            click.echo(f' > {upstream_branch_command}')
            click.secho(''.ljust(len(branch_name), '#'))
        click.secho('Switching to new branch. Good luck!', fg='green')

    except InvalidGitRepositoryError as err:
        click.secho(err, fg='red')
        exit(1)
    except NoSuchPathError as err:
        click.secho(err, fg='red')
        exit(1)


def check_if_branch_is_local(repo, branch_name) -> bool:
    result = repo.git.execute(['git', 'branch', '--list', branch_name])
    if not result:
        return False
    return True


def check_if_branch_name_available(repo, branch_name) -> bool:
    remote_branch = repo.git.execute(['git', 'ls-remote', '--heads', 'origin', branch_name])
    if remote_branch:
        return False
    return True


def switch_to_branch(repo, branch_name):
    repo.git.execute(['git', 'checkout', branch_name])


class Utils:

    @staticmethod
    def issue_title_to_branch_name(issue_id: str, title: str, issue_type: str) -> str:

        separator = '-'

        title = unidecode(title)  # replace non ascii characters
        title = title.replace(' ', separator)  # no spaces

        title = re.sub(r'[^\w\d-]', separator, title)  # replace all non word, non digit characters
        title = re.sub(r'-+', separator, title)  # remove repetitions
        title = re.sub(r'^-', '', title)  # trim start
        title = re.sub(r'-$', '', title)  # trim end
        title = title.strip()  # trim both ends

        title = str.lower(title)

        allowed_chars = string.ascii_letters + string.digits + '-'

        branch_title = ''
        for c in title:
            if c in allowed_chars:
                branch_title += c

        branch_title = f'{issue_type}/{issue_id}_{branch_title}'

        # keep the branch name under 255 chars
        branch_title = branch_title[:255]

        return branch_title


@click.command()
@click.argument('issue_id_or_url')
@click.option('-n', '--name-only', is_flag=True, default=False,
              help='Generates the branch name and prints it, no actual branch will be created (default is False)')
@click.option('-p', '--push', is_flag=True, default=False,
              help='Push newly created branch to remote (default is False)')
def cli(issue_id_or_url, name_only, push):
    """Simple program that takes a JIRA issue ID and creates a new local and tracking remote branch"""

    if '/' in issue_id_or_url:
        issue_id_or_url = issue_id_or_url.split('/')[-1]

    # print(os.getcwd())
    # repo = Repo(os.getcwd())
    # assert not repo.bare

    branch_name = get_branch_name_from_issue(issue_id_or_url)
    # print(branch_name, end='\n')
    # sys.stdout.write(branch_name)

    if name_only:
        click.secho('BRANCH NAME: '.ljust(len(branch_name), '#'))
        click.echo(branch_name)
        click.secho(''.rjust(len(branch_name), '#'))
        if not check_if_branch_name_available(Repo(Path.cwd()), branch_name):
            click.secho(f'WARNING: a remote branch by that name already exists', fg='red')
    else:
        create_branch(branch_name, push)


if __name__ == '__main__':
    cli()
