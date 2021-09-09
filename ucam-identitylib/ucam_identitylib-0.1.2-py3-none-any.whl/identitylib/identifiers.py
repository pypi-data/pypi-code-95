from typing import Optional, List, Callable, Dict
from collections import namedtuple
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, eq=True)
class IdentifierScheme:
    """
    A class which containing the information needed to represent an identifier scheme.

    """

    identifier: str  # the actual string which identifiers this scheme
    common_name: str  # a common name for this identifier (e.g. CRSid or USN)
    # a dict of aliases - each value being a previous representation of this identifier
    # keyed on a brief description of that alias
    aliases: Dict[str, str]
    value_parser: Optional[Callable] = None  # a parser for the value of an id with this scheme

    def __str__(self):
        """
        Always return the scheme identifier as the string representation.

        """
        return self.identifier


class IdentifierSchemes:
    """
    A holder for all identifier schemes used within identity systems.

    """

    """
    Person identifiers.

    """

    CRSID = IdentifierScheme(
        'v1.person.identifiers.cam.ac.uk',
        'CRSid',
        {
            'deprecated': 'person.crs.identifiers.uis.cam.ac.uk',
            'deprecated-versioned': 'person.v1.crs.identifiers.cam.ac.uk',
        }
    )

    USN = IdentifierScheme(
        'person.v1.student-records.university.identifiers.cam.ac.uk',
        'USN',
        {
            'deprecated': 'person.camsis.identifiers.admin.cam.ac.uk',
            'deprecated-versioned': 'person.v1.ust.identifiers.cam.ac.uk',
        }
    )

    STAFF_NUMBER = IdentifierScheme(
        'person.v1.human-resources.university.identifiers.cam.ac.uk',
        'Staff Number',
        {
            'deprecated': 'person.chris.identifiers.admin.cam.ac.uk',
            'deprecated-versioned': 'person.v1.uhr.identifiers.cam.ac.uk',
        }
    )

    BOARD_OF_GRADUATE_STUDIES = IdentifierScheme(
        'person.v1.board-of-graduate-studies.university.identifiers.cam.ac.uk',
        'Board of Graduate Studies Identifier',
        {
            'deprecated': 'person.bgs.identifiers.admin.cam.ac.uk',
        }
    )

    LEGACY_CARDHOLDER = IdentifierScheme(
        'person.v1.legacy-card.university.identifiers.cam.ac.uk',
        'Legacy cardholder Identifier',
        {
            'deprecated': 'person.legacy_card.identifiers.admin.cam.ac.uk',
        }
    )

    """
    Institution identifiers.

    """

    STUDENT_INSTITUTION = IdentifierScheme(
        'institution.v1.student-records.university.identifiers.cam.ac.uk',
        'Student Institution',
        {
            'deprecated': 'institution.v1.ust.identifiers.cam.ac.uk',
        }
    )

    HR_INSTITUTION = IdentifierScheme(
        'institution.v1.human-resources.university.identifiers.cam.ac.uk',
        'Human Resources Institution',
        {
            'deprecated': 'institution.v1.uhr.identifiers.cam.ac.uk',
        }
    )

    LEGACY_CARD_INSTITUTION = IdentifierScheme(
        'institution.v1.legacy-card.university.identifiers.cam.ac.uk',
        'Legacy Card Institution',
        {
            'deprecated': 'inst.legacy_card.identifiers.admin.cam.ac.uk',
        }
    )

    """
    Misc. identifiers.

    """

    STUDENT_ACADEMIC_PLAN = IdentifierScheme(
        'academic-plan.v1.student-records.university.identifiers.cam.ac.uk',
        'Student Academic Plan',
        {
            'deprecated': 'academicPlan.v1.ust.identifiers.cam.ac.uk',
        }
    )

    CARD = IdentifierScheme(
        'card.v1.card.university.identifiers.cam.ac.uk',
        'Card Identifier',
        {
            'deprecated': 'card.card.identifiers.uis.cam.ac.uk',
        }
    )

    LEGACY_TEMP_CARD = IdentifierScheme(
         'temporary-card.v1.card.university.identifiers.cam.ac.uk',
         'Temporary Card Identifier',
         {
             'deprecated': 'temp_id.card.identifiers.uis.cam.ac.uk'
         }
    )

    MIFARE_ID = IdentifierScheme(
        'mifare-identifier.v1.card.university.identifiers.cam.ac.uk',
        'Mifare Identifier',
        {
            'deprecated': 'mifare_id.card.identifiers.uis.cam.ac.uk',
        },
        value_parser=(
            lambda v: v.lstrip('0') or '0'  # fallback to '0' to avoid stripping '000' to ''
        )
    )

    MIFARE_NUMBER = IdentifierScheme(
        'mifare-number.v1.card.university.identifiers.cam.ac.uk',
        'Mifare Number',
        {
            'deprecated': 'mifare_number.card.identifiers.uis.cam.ac.uk',
        }
    )

    BARCODE = IdentifierScheme(
        'barcode.v1.card.university.identifiers.cam.ac.uk',
        'Card Barcode',
        {
            'deprecated': 'barcode.identifiers.lib.cam.ac.uk',
        }
    )

    CARD_LOGO = IdentifierScheme(
        'card-logo.v1.card.university.identifiers.cam.ac.uk',
        'Card Logo Identifier',
        {
            'deprecated': 'card_logo.card.identifiers.uis.cam.ac.uk',
        }
    )

    PHOTO = IdentifierScheme(
        'photo.v1.photo.university.identifiers.cam.ac.uk',
        'Photo Identifier',
        {
            'deprecated': 'photo_id.photo.identifiers.uis.cam.ac.uk',
        }
    )

    LEGACY_PHOTO = IdentifierScheme(
        'photo.v1.legacy-card.university.identifiers.cam.ac.uk',
        'Legacy Photo Identifier',
        {
            'deprecated': 'photo.legacy_card.identifiers.admin.cam.ac.uk',
        }
    )

    LEGACY_CARD = IdentifierScheme(
        'card.v1.legacy-card.university.identifiers.cam.ac.uk',
        'Legacy Card Identifier',
        {
            'deprecated': 'card.legacy_card.identifiers.admin.cam.ac.uk',
        }
    )

    @staticmethod
    @lru_cache()
    def get_registered_schemes() -> List[IdentifierScheme]:
        """
        Returns the list of registered identifier schemes.

        """
        return [
            prop for prop in vars(IdentifierSchemes).values() if (
                isinstance(prop, IdentifierScheme)
            )
        ]

    @staticmethod
    def from_string(identifier_scheme: str, find_by_alias: bool = False):
        """
        Return an instance of an identifier scheme from a string representation.
        If `find_by_alias` is true identifier schemes will be matched based on
        the alias as well as.

        """
        matching_scheme = next((
            scheme for scheme in IdentifierSchemes.get_registered_schemes() if (
                scheme.identifier == identifier_scheme or
                find_by_alias and identifier_scheme in scheme.aliases.values()
            )
        ), None)

        if not matching_scheme:
            raise ValueError(f'Invalid identifier scheme {identifier_scheme}')

        return matching_scheme


class Identifier(namedtuple('Identifier', ['value', 'scheme'])):
    """
    A representation of an identifer, in the form of 'value' and 'scheme'

    """

    @staticmethod
    def from_string(
        value: str, *,
        fallback_scheme: Optional[IdentifierScheme] = None,
        find_by_alias: bool = False,
    ) -> 'Identifier':
        """
        Parse a `<value>@<scheme>` string into an identifier pair.

        """
        parsed_value: Optional[str] = None
        scheme: Optional[IdentifierScheme] = None

        parts = value.split('@')
        if len(parts) == 2:
            parsed_value = parts[0]
            scheme = IdentifierSchemes.from_string(parts[1], find_by_alias)
        elif len(parts) == 1 and fallback_scheme is not None:
            parsed_value = value
            scheme = fallback_scheme
        else:
            raise ValueError(f'Invalid identifier {value}')

        parsed_value = scheme.value_parser(parsed_value) if scheme.value_parser else parsed_value
        return Identifier(parsed_value, scheme)

    def __str__(self):
        """
        Parse an identifier back to string form.

        """

        return f'{self.value}@{self.scheme}'
