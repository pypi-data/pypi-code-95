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

wanted = ["SESSION", "VC_SESSION", "REDIS_PASSWORD", "REDISPASSWORD", "HEROKU_API", "BOT_TOKEN"]

save, conf = {}, []


# Class Var Clean up
def cleanup_cache(var):
    os_stuff()
    for z in wanted:
        if z in list(var.__dict__.keys()):
            save.update({z: var.__dict__[z]})
            setattr(var, z, "")
    if not conf:
        conf.append(var)

# Env clean up
def os_stuff():
    all = os.environ
    for z in list(all.keys()):
        if z in wanted:
            all.update({z: ""})

# Getting them back for re-start & soft update
def call_back():
    for z in save:
        setattr(conf[0], z, save[z])
        os.environ[z] = save[z]
    

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
