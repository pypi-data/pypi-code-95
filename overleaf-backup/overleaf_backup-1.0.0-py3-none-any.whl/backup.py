import datetime
import time
import requests

from .exceptions import LoginException, EmptyProjectsException, WrongCookieException


def execute_backup(projects: list, email: str, password: str, url: str, backup_path: str):
    """
    Backups the given overleaf projects to the given backup path once.
    The function uses the given email and password to log into overleaf.
    :param projects: List of overleaf project ID's to backup
    :param email: Email of the overleaf account
    :param password: Password of the overleaf account
    :param url: Link to the overleaf instance (f.e. example.com/overleaf)
    :param backup_path: path where to store the backup files
    :return: None
    """
    if projects is []:
        raise EmptyProjectsException("The list of projects was empty")

    s = requests.session()
    csrf = s.get(url + "/login").text
    csrf = csrf.split("name=\"_csrf\"")
    csrf_token = csrf[1][22:58]

    data = {"email": email, "password": password, "_csrf": csrf_token}
    resp = s.post(url + "/login", data=data, allow_redirects=False)
    if "Found. Redirecting to" not in resp.text:
        raise LoginException("Email, password or URL was wrong, could not log in!")

    for project in projects:
        resp = s.get(url + "/project/" + project + "/download/zip")
        with open(backup_path + project + ".zip", "wb") as fd:
            fd.write(resp.content)


def execute_backup_cookie(projects: list, cookie: str, url: str, backup_path: str):
    """
    Backups the given overleaf projects to the given backup path once.
    The function uses the given session cookie to log into overleaf.
    :param projects: List of overleaf project ID's to backup
    :param cookie: Overlead session cookie
    :param url: Link to the overleaf instance (f.e. example.com/overleaf)
    :param backup_path: path where to store the backup files
    :return: None
    """
    if projects is []:
        raise EmptyProjectsException("The list of projects was empty")

    s = requests.session()
    s.cookies.set(name="sharelatex.sid", value=cookie)
    resp = s.get(url + "/project")

    if resp.status_code == 302:
        raise WrongCookieException("Cookie was wrong, could not log in")

    for project in projects:
        resp = s.get(url + "/project/" + project + "/download/zip")
        with open(backup_path + project + ".zip", "wb") as fd:
            fd.write(resp.content)


class BackupLoop:
    """
    Can be used to backup the given projects in a loop. The time between the backups can be given
    as a time.datetime object when creating an instance, otherwise the default time of 12 hours will be used.
    To start the loop call execute() on a BackupLoop instance.
    """

    def __init__(self, projects: list, email: str, password: str, url: str, backup_path: str,
                 interval: datetime.timedelta = datetime.timedelta(hours=12)):
        if projects is []:
            raise EmptyProjectsException("The list of projects was empty")
        self.projects = projects
        self.email = email
        self.password = password
        self.url = url
        self.backup_path = backup_path
        self.interval = interval.total_seconds()
        self.cookie = None
        self.cookie_expiry = None

    def _login(self):
        s = requests.session()
        csrf = s.get(self.url + "/login").text
        csrf = csrf.split("name=\"_csrf\"")
        csrf_token = csrf[1][22:58]

        data = {"email": self.email, "password": self.password, "_csrf": csrf_token}
        resp = s.post(self.url + "/login", data=data, allow_redirects=False)
        if "Found. Redirecting to /project" not in resp.text:
            raise LoginException("Email, password or URL was wrong, could not log in!")
        cookie_value = ""
        cookie_expiry = datetime.datetime.now()
        for cookie in s.cookies:
            if cookie.name == "sharelatex.sid":
                cookie_value = cookie.value
                cookie_expiry = datetime.datetime.fromtimestamp(cookie.expires)
        return cookie_value, cookie_expiry

    def _cookie_expired(self):
        if self.cookie is None:
            return True
        if datetime.datetime.now() > self.cookie_expiry:
            return True
        return False

    def execute(self):
        """
        Executes a loop to backup the given projects after a specific time.
        :return: None
        """
        while True:
            if self._cookie_expired():
                self.cookie, self.cookie_expiry = self._login()
            execute_backup_cookie(self.projects, self.cookie, self.url, self.backup_path)
            time.sleep(self.interval)
