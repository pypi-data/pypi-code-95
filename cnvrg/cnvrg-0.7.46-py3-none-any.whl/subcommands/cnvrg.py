import click
from cnvrg.helpers.auth_helper import CnvrgCredentials
import cnvrg.helpers.logger_helper as logger_helper
from tinynetrc import Netrc

@click.group()
def cnvrg():
    pass

@cnvrg.command()
@click.option("--email")
@click.option("--password")
@click.option("--api")
def login(email=None, password=None, api=None):
    cred = CnvrgCredentials()
    if cred.logged_in: return logger_helper.log_message("Already logged in", level=logger_helper.LEVEL_SUCCESS)
    if not email: email = click.prompt("Please enter your email: ")
    if not password: password = click.prompt("Please enter your password: (hidden)", hide_input=True)
    try:
        cred.login(email, password, api_url=api)
        logger_helper.log_message("Logged in as {username}".format(username=cred.username))
    except Exception as e:
        print(e)
        logger_helper.log_error(e)
        logger_helper.log_message("Cant log in, please check your input params", level=logger_helper.LEVEL_ERROR)



@cnvrg.command()
def logout():
    cred = CnvrgCredentials()
    if cred.logout(): logger_helper.log_message("Logged out successfuly", logger_helper.LEVEL_SUCCESS)
    else: logger_helper.log_message("You are already logged out", logger_helper.LEVEL_SUCCESS)