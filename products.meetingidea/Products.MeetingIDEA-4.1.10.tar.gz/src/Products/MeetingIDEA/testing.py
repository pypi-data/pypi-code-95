
# -*- coding: utf-8 -*-
from plone.app.testing import FunctionalTesting
from plone.testing import z2
from plone.testing import zca
from Products.MeetingCommunes.testing import MCLayer

import Products.MeetingIDEA


MIDEA_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                           package=Products.MeetingIDEA,
                           name='MIDEA_ZCML')

MIDEA_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MIDEA_ZCML),
                               name='MIDEA_Z2')

MIDEA_TESTING_PROFILE = MCLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingIDEA,
    additional_z2_products=('imio.dashboard',
                            'Products.MeetingIDEA',
                            'Products.MeetingCommunes',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow',
                            'Products.PasswordStrength'),
    gs_profile_id='Products.MeetingIDEA:testing',
    name="MIDEA_TESTING_PROFILE")

MIDEA_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MIDEA_TESTING_PROFILE,), name="MIDEA_TESTING_PROFILE_FUNCTIONAL")