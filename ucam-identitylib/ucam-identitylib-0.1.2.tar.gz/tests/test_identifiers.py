from unittest import TestCase

from identitylib.identifiers import Identifier, IdentifierSchemes, IdentifierScheme


class IdentifiersTestCase(TestCase):

    def test_identifiers_can_be_parsed(self):
        # standard parsing
        self.assertEqual(
            Identifier.from_string(
                'abc123@person.v1.student-records.university.identifiers.cam.ac.uk'
            ),
            Identifier('abc123', IdentifierSchemes.USN)
        )

        # fallback scheme given - actual scheme in identifier is used
        self.assertEqual(
            Identifier.from_string(
                'xxx@v1.person.identifiers.cam.ac.uk', fallback_scheme=IdentifierSchemes.USN
            ),
            Identifier('xxx', IdentifierSchemes.CRSID)
        )

    def test_identifiers_parse_back_to_strings(self):
        # standard parsing
        self.assertEqual(
            str(Identifier('1000', IdentifierSchemes.STAFF_NUMBER)),
            '1000@person.v1.human-resources.university.identifiers.cam.ac.uk'
        )

        # fallback scheme given - actual scheme in identifier is used
        self.assertEqual(
            Identifier.from_string(
                'xxx@v1.person.identifiers.cam.ac.uk', fallback_scheme=IdentifierSchemes.USN
            ),
            Identifier('xxx', IdentifierSchemes.CRSID)
        )

    def test_mifare_id_removes_padded_zeros(self):
        self.assertEqual(
            Identifier.from_string('0204011010', fallback_scheme=IdentifierSchemes.MIFARE_ID),
            Identifier('204011010', IdentifierSchemes.MIFARE_ID)
        )
        self.assertEqual(
            Identifier.from_string('00001', fallback_scheme=IdentifierSchemes.MIFARE_ID),
            Identifier('1', IdentifierSchemes.MIFARE_ID)
        )
        self.assertEqual(
            Identifier.from_string(
                '000121@mifare-identifier.v1.card.university.identifiers.cam.ac.uk'
            ),
            Identifier('121', IdentifierSchemes.MIFARE_ID)
        )
        self.assertEqual(
            Identifier.from_string('00000', fallback_scheme=IdentifierSchemes.MIFARE_ID),
            Identifier('0', IdentifierSchemes.MIFARE_ID)
        )

    def test_invalid_identifiers_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Invalid identifier scheme cam.ac.uk'):
            Identifier.from_string('123@cam.ac.uk')
        with self.assertRaisesRegex(ValueError, 'Invalid identifier no-scheme'):
            Identifier.from_string('no-scheme')

    def test_identifiers_can_be_created_from_aliases(self):
        self.assertEqual(
            Identifier.from_string('VBE@barcode.identifiers.lib.cam.ac.uk', find_by_alias=True),
            Identifier('VBE', IdentifierSchemes.BARCODE)
        )

        # when we use find_by_alias this should throw
        with self.assertRaisesRegex(
            ValueError,
            'Invalid identifier scheme barcode.identifiers.lib.cam.ac.uk'
        ):
            Identifier.from_string('VBE@barcode.identifiers.lib.cam.ac.uk')

    def test_identifier_schemes_can_be_compared(self):
        self.assertTrue(
            IdentifierSchemes.PHOTO == IdentifierScheme(
                'photo.v1.photo.university.identifiers.cam.ac.uk',
                'Photo Identifier',
                {
                    'deprecated': 'photo_id.photo.identifiers.uis.cam.ac.uk',
                }
            )
        )
