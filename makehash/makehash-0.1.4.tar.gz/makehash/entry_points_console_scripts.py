# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

def makehash():
    from click_anno import command
    from .main import make_hash
    command(make_hash)()

def verifyhash():
    from click_anno import command
    from .main import verify_hash
    command(verify_hash)()
