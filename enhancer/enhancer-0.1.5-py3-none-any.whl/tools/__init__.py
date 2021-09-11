"""

This Is For Security Purpose Only
As Many Noobs Using Cheap Tricks To Hack userbot.
We here to save them

~ @TeamUltroid

"""

# Lol You Are So desperate.
# You came all here just to see this
# 😂😂😂😂

import os

_discared = ["SESSION", "VC_SESSION", "REDIS_PASSWORD", "REDISPASSWORD", "HEROKU_API", "BOT_TOKEN"]

_get_sys, _conf = {}, []


# Class Var Clean up
def cleanup_cache(var):
    os_stuff()
    for z in _discared:
        if z in var.__dict__.keys():
            _get_sys.update({z: var.__dict__[z]})
            setattr(var, z, "")
    if not _conf:
        _conf.append(var)

# Env clean up
def os_stuff():
    all = os.environ
    for z in all.keys():
        if z in _discared:
            all.update({z: ""})

# Getting them back for re-start & soft update
def call_back():
    for z in _get_sys:
        if _get_sys[z]:
            setattr(_conf[0], z, _get_sys[z])
            os.environ[z] = _get_sys[z]
    

DANGER = [
    "SESSION",
    "HEROKU_API",
    "base64",
    "bash",
    "call_back",
    "get_me()",
    "exec",
    "phone",
    "REDIS_PASSWORD",
    "load_addons",
    "load_plugins",
    "load_vc",
    "load_manager",
    "load_pmbot",
    "load_assistant",
    "plugin_loader",
    "os.system",
    "subprocess",
    "await locals()",
    "aexec",
    ".session.save()",
    ".auth_key.key",
    "INSTA_USERNAME",
    "INSTA_PASSWORD",
    "INSTA_SET",
]
