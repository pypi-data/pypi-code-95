# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from product.recaptcha_invisible.testing import PRODUCT_RECAPTCHA_INVISIBLE_INTEGRATION_TESTING  # noqa: E501,I001

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that product.recaptcha_invisible is properly installed."""

    layer = PRODUCT_RECAPTCHA_INVISIBLE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if product.recaptcha_invisible is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'product.recaptcha_invisible'))

    def test_browserlayer(self):
        """Test that IProductRecaptchaInvisibleLayer is registered."""
        from plone.browserlayer import utils
        from product.recaptcha_invisible.interfaces import IProductRecaptchaInvisibleLayer
        self.assertIn(
            IProductRecaptchaInvisibleLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = PRODUCT_RECAPTCHA_INVISIBLE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['product.recaptcha_invisible'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if product.recaptcha_invisible is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'product.recaptcha_invisible'))

    def test_browserlayer_removed(self):
        """Test that IProductRecaptchaInvisibleLayer is removed."""
        from plone.browserlayer import utils
        from product.recaptcha_invisible.interfaces import IProductRecaptchaInvisibleLayer
        self.assertNotIn(
            IProductRecaptchaInvisibleLayer,
            utils.registered_layers())
