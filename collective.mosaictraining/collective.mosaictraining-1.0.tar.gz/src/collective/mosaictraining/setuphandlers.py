# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from collective.mosaictraining.importcontent import import_content


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'collective.mosaictraining:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Create the Mosaic training guide pages and images
    import_content(context)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
