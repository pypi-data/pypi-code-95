# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import product.recaptcha_invisible


class ProductRecaptchaInvisibleLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=product.recaptcha_invisible)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'product.recaptcha_invisible:default')


PRODUCT_RECAPTCHA_INVISIBLE_FIXTURE = ProductRecaptchaInvisibleLayer()


PRODUCT_RECAPTCHA_INVISIBLE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PRODUCT_RECAPTCHA_INVISIBLE_FIXTURE,),
    name='ProductRecaptchaInvisibleLayer:IntegrationTesting',
)


PRODUCT_RECAPTCHA_INVISIBLE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRODUCT_RECAPTCHA_INVISIBLE_FIXTURE,),
    name='ProductRecaptchaInvisibleLayer:FunctionalTesting',
)


PRODUCT_RECAPTCHA_INVISIBLE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PRODUCT_RECAPTCHA_INVISIBLE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='ProductRecaptchaInvisibleLayer:AcceptanceTesting',
)
