# -*- coding: utf-8 -*-
# from plone.app.upgrade.utils import loadMigrationProfile
#
#
# def reload_gs_profile(context):
#     loadMigrationProfile(context, "profile-library.core:default")


def geolocation_behavior(context):
    context.runAllImportStepsFromProfile("profile-collective.faceted.map:default")
    context.runImportStepFromProfile("profile-library.core:default", "typeinfo")
