# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility


def has_behavior(type_name, behavior_name):
    """Check if a behavior is on portal_type"""
    fti = getUtility(IDexterityFTI, name=type_name)
    if not fti:
        return
    behaviors = list(fti.behaviors)
    if behavior_name not in behaviors:
        return False
    else:
        return True


def add_behavior(type_name, behavior_name):
    """Add a behavior to a type"""
    fti = getUtility(IDexterityFTI, name=type_name)
    if not fti:
        return
    behaviors = list(fti.behaviors)
    if behavior_name not in behaviors:
        behaviors.append(behavior_name)
        fti._updateProperty("behaviors", tuple(behaviors))


def remove_behavior(type_name, behavior_name):
    """Add a behavior to a type"""
    fti = getUtility(IDexterityFTI, name=type_name)
    if not fti:
        return
    behaviors = list(fti.behaviors)
    if behavior_name in behaviors:
        behaviors.remove(behavior_name)
        fti._updateProperty("behaviors", tuple(behaviors))
