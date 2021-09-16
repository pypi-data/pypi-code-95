# -*- coding: utf-8 -*-
from library.core.testing import LIBRARY_CORE_INTEGRATION_TESTING
from library.core.utils import add_behavior
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.formwidget.geolocation.geolocation import Geolocation

import unittest


class TestGeolocation(unittest.TestCase):

    layer = LIBRARY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.patrimoine = api.content.create(
            container=self.portal, type="patrimoine", title="Patrimoine"
        )

    def test_is_geolocated(self):
        add_behavior(
            "patrimoine", "collective.geolocationbehavior.geolocation.IGeolocatable"
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = catalog(UID=self.patrimoine.UID())[0]
        self.assertEqual(self.patrimoine.geolocation, None)
        self.patrimoine.geolocation = Geolocation(latitude="55.0", longitude="5.0")
        is_geolocated = catalog.getIndexDataForRID(brain.getRID())["is_geolocated"]
        self.assertFalse(is_geolocated)
        # reindex
        catalog.catalog_object(brain.getObject(), idxs=["is_geolocated"])
        is_geolocated = catalog.getIndexDataForRID(brain.getRID())["is_geolocated"]
        self.assertTrue(is_geolocated)

    def test_false_if_no_geolocation(self):
        add_behavior(
            "patrimoine", "collective.geolocationbehavior.geolocation.IGeolocatable"
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = catalog(UID=self.patrimoine.UID())[0]
        self.assertEqual(self.patrimoine.geolocation, None)
        # reindex
        catalog.catalog_object(brain.getObject(), idxs=["is_geolocated"])
        is_geolocated = catalog.getIndexDataForRID(brain.getRID())["is_geolocated"]
        self.assertFalse(is_geolocated)

    def test_false_if_no_longitude_or_longitude_eq_0(self):
        add_behavior(
            "patrimoine", "collective.geolocationbehavior.geolocation.IGeolocatable"
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = catalog(UID=self.patrimoine.UID())[0]
        self.assertEqual(self.patrimoine.geolocation, None)
        self.patrimoine.geolocation = Geolocation(latitude="55.0")
        # reindex
        catalog.catalog_object(brain.getObject(), idxs=["is_geolocated"])
        is_geolocated = catalog.getIndexDataForRID(brain.getRID())["is_geolocated"]
        self.assertFalse(is_geolocated)
        self.patrimoine.geolocation = Geolocation(longitude="0.0", latitude="55.0")
        # reindex
        catalog.catalog_object(brain.getObject(), idxs=["is_geolocated"])
        is_geolocated = catalog.getIndexDataForRID(brain.getRID())["is_geolocated"]
        self.assertFalse(is_geolocated)

    def test_false_if_no_latitude_or_latiude_eq_0(self):
        add_behavior(
            "patrimoine", "collective.geolocationbehavior.geolocation.IGeolocatable"
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = catalog(UID=self.patrimoine.UID())[0]
        self.assertEqual(self.patrimoine.geolocation, None)
        self.patrimoine.geolocation = Geolocation(longitude="5.0")
        # reindex
        catalog.catalog_object(brain.getObject(), idxs=["is_geolocated"])
        is_geolocated = catalog.getIndexDataForRID(brain.getRID())["is_geolocated"]
        self.assertFalse(is_geolocated)
        self.patrimoine.geolocation = Geolocation(longitude="5.0", latitude="0.0")
        # reindex
        catalog.catalog_object(brain.getObject(), idxs=["is_geolocated"])
        is_geolocated = catalog.getIndexDataForRID(brain.getRID())["is_geolocated"]
        self.assertFalse(is_geolocated)

    def test_false_if_no_latitude_and_no_longitude(self):
        add_behavior(
            "patrimoine", "collective.geolocationbehavior.geolocation.IGeolocatable"
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = catalog(UID=self.patrimoine.UID())[0]
        self.assertEqual(self.patrimoine.geolocation, None)
        self.patrimoine.geolocation = "Kamoulox"
        # reindex
        catalog.catalog_object(brain.getObject(), idxs=["is_geolocated"])
        is_geolocated = catalog.getIndexDataForRID(brain.getRID())["is_geolocated"]
        self.assertFalse(is_geolocated)
