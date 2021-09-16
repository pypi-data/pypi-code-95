# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from library.core.testing import LIBRARY_CORE_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that library.core is properly installed."""

    layer = LIBRARY_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if library.core is installed."""
        self.assertTrue(self.installer.isProductInstalled("library.core"))

    def test_browserlayer(self):
        """Test that ILibraryCoreLayer is registered."""
        from library.core.interfaces import ILibraryCoreLayer
        from plone.browserlayer import utils

        self.assertIn(ILibraryCoreLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = LIBRARY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstallProducts(["library.core"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if library.core is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled("library.core"))

    def test_browserlayer_removed(self):
        """Test that ILibraryCoreLayer is removed."""
        from library.core.interfaces import ILibraryCoreLayer
        from plone.browserlayer import utils

        self.assertNotIn(ILibraryCoreLayer, utils.registered_layers())
