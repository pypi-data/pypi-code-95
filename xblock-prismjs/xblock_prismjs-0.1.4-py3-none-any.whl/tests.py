"""
Tests for prism
"""
import json
import unittest
import mock
import django 

from django.conf import settings

from xblock.field_data import DictFieldData

from prism import PrismXBlock

settings.configure(Debug=True)

django.setup()


class TestPrismXBlock(unittest.TestCase):
    """
    Unit tests for prism xblock
    """
    def make_one(self, **kw):
        """
        Creates a prism XBlock for testing purpose
        """
        field_data = DictFieldData(kw)
        block = PrismXBlock(mock.Mock(), field_data, mock.Mock())
        block.location = mock.Mock(
            block_id="block_id", org="org", course="course", block_type="block_type"
        )
        return block

    def test_fields_xblock(self):
        block = self.make_one()
        self.assertEqual(block.language, "python")
        self.assertEqual(block.theme, "dark")
        self.assertEqual(block.display_name, "Syntax Highlighter")
        self.assertEqual(block.code_data, "print('hello world')")
        self.assertEqual(block.maxheight, 450)
        
    def test_save_settings_prism(self):
        block = self.make_one()

        fields = {
            "display_name": "Test Prism",
            "code_data": "console.log('foo bar')",
            "language": "javascript",
            "theme": "light",
            "maxheight": 550
        }

        block.studio_submit(mock.Mock(method="POST", body= json.dumps(fields).encode('utf-8')))

        self.assertEqual(block.display_name, fields["display_name"])
        self.assertEqual(block.code_data, fields['code_data'])
        self.assertEqual(block.language, fields['language'])
        self.assertEqual(block.theme, fields['theme'])
        self.assertEqual(block.maxheight, fields['maxheight'])

    def test_studio_view(self):
        block = self.make_one()
        fragment = block.studio_view()
        self.assertIn('Display Name', fragment.content)
        self.assertIn('Code', fragment.content)
        self.assertIn('Language', fragment.content)
        self.assertIn('Theme', fragment.content)
        self.assertIn('Save', fragment.content)
        self.assertIn('Cancel', fragment.content)

    def test_student_view(self):
        block = self.make_one()
        fragment = block.student_view()
        self.assertIn('hello world', fragment.content)

    def test_save_settings_on_student_view(self):
        block = self.make_one()

        fields = {
            "display_name": "Test Prism",
            "code_data": "console.log('foo bar')",
            "language": "javascript",
            "theme": "light",
            "maxheight": 550
        }

        block.studio_submit(mock.Mock(method="POST", body= json.dumps(fields).encode('utf-8')))

        self.assertEqual(block.display_name, fields["display_name"])
        self.assertEqual(block.code_data, fields['code_data'])
        self.assertEqual(block.language, fields['language'])
        self.assertEqual(block.theme, fields['theme'])
        self.assertEqual(block.maxheight, fields['maxheight'])

        fragment = block.student_view()
        self.assertIn('foo bar', fragment.content)