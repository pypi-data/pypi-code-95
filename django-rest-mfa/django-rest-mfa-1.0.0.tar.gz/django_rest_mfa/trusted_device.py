import string
import secrets
from user_agents import parse


def generate_random_key():
    return "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(20)
    )


def generate_ua_short(ua_string: str) -> str:
    """Generate a short user agent of Device / Operating System / Browser"""
    user_agent = parse(ua_string)
    return "{device} / {os} / {browser}".format(
        device=user_agent.get_device(),
        os=user_agent.get_os(),
        browser=user_agent.browser.family,
    )
