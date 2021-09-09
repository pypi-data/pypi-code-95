#!/usr/bin/env python
# Tested on GITHub/Travis
# on your machine, just run pytest in this directory or execute it to get outputs
#

import pytest

from a2p2.jmmc import Catalog

oidbValidId = 38681

spicaCatName = "spica"
#spicaCatName = "spica_2021_07_08"


class CustomCatalog(Catalog):
    def __init__(self, catalogName):
        Catalog.__init__(self, catalogName,
                         url="http://localhost:8080/exist/restxq/catalogs")
#                )


def test_same_id():
    has_same_id("oidb", oidbValidId)


def test_same_id2():
    has_same_id("oidb", oidbValidId)


def has_same_id(catname, id):
    c = CustomCatalog(catname)
    r = c.getRow(id)
    assert r["id"] == id
    print("We are ok with catalog %s id %s" % (catname, id))
    return

def test_protected():
    spica = CustomCatalog(spicaCatName)
    try:
        spica.getRow(1)
        spicaIsProtected = False
    except:
        spicaIsProtected = True

    assert spicaIsProtected


def test_public():
    oidb = CustomCatalog("oidb")
    try:
        oidb.getRow(oidbValidId)
        oidbIsPublic = True
    except:
        oidbIsPublic = False
    assert oidbIsPublic

def test_simple_update():
    c = CustomCatalog(spicaCatName)
    v=2
    c.updateRow(1, { "target_priority_pi" : v } )
    priority = c.getRow(1)["target_priority_pi"]
    assert priority==v

def test_simple_update_with_str_as_json_input():
    c = CustomCatalog(spicaCatName)
    v=2
    c.updateRow(1, '{"target_priority_pi":%d}'%v)
    priority = c.getRow(1)["target_priority_pi"]
    assert priority==v


def test_duplicated_col_update():
    c = CustomCatalog(spicaCatName)

    c.updateRow(1, {"target_priority_pi":1, "target_priority_pi":2})
    priority = c.getRow(1)["target_priority_pi"]
    assert priority==2

    c.updateRow(1, {"target_priority_pi":1, "TARGET_PRIORITY_PI":2})
    priority = c.getRow(1)["target_priority_pi"]
    assert priority==2

def test_reject_bad_col():
    # TODO 
    # updateRow(1,{"wrong_key":42})
    assert False
