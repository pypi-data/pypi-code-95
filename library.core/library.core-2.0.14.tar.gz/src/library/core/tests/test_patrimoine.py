# -*- coding: utf-8 -*-
from library.core.content.patrimoine import InvalidFileSizeError
from library.core.content.patrimoine import fileSize
from library.core.testing import LIBRARY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.field import NamedFile

import unittest


class TestPatrimoine(unittest.TestCase):

    layer = LIBRARY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.patrimoine = api.content.create(
            container=self.portal, type="patrimoine", title="Patrimoine"
        )

    def test_filesize(self):
        # original value in patrimoine : 30000000
        file = NamedFile()
        file.data = "0" * 30000000
        self.patrimoine.fichier_pdf = NamedBlobFile(
            data=file.data, filename=u"bigfile.pdf"
        )
        self.assertTrue(fileSize(self.patrimoine.fichier_pdf))
        file = NamedFile()
        file.data = "0" * 30000001
        self.patrimoine.fichier_pdf = NamedBlobFile(
            data=file.data, filename=u"bigfile.pdf"
        )
        with self.assertRaises(InvalidFileSizeError):
            self.assertRaises(
                InvalidFileSizeError, fileSize(self.patrimoine.fichier_pdf)
            )
