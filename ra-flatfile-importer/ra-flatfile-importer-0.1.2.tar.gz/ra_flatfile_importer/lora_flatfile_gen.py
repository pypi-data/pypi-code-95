#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from typing import Callable
from typing import Dict
from typing import Iterator
from typing import List
from typing import Tuple
from typing import Union

import ra_utils.generate_uuid
from ramodels.lora import Facet
from ramodels.lora import Klasse
from ramodels.lora import Organisation

from ra_flatfile_importer.lora_flatfile_model import LoraFlatFileFormat
from ra_flatfile_importer.lora_flatfile_model import LoraFlatFileFormatChunk


def apply(func: Callable) -> Callable:
    return lambda tup: func(*tup)


IN_CLASSES: Dict[str, List[Union[Tuple[str, str, str], str]]] = {
    "engagement_job_function": [
        "Udvikler",
        "Specialkonsulent",
        "Ergoterapeut",
        "Udviklingskonsulent",
        "Specialist",
        "Jurist",
        "Personalekonsulent",
        "Lønkonsulent",
        "Kontorelev",
        "Ressourcepædagog",
        "Pædagoisk vejleder",
        "Skolepsykolog",
        "Støttepædagog",
        "Bogopsætter",
        "Timelønnet lærer",
        "Pædagogmedhjælper",
        "Teknisk Servicemedarb.",
        "Lærer/Overlærer",
    ],
    "association_type": [
        "Formand",
        "Leder",
        "Medarbejder",
        "Næstformand",
        "Projektleder",
        "Projektgruppemedlem",
        "Teammedarbejder",
    ],
    "org_unit_type": [
        "Afdeling",
        "Institutionsafsnit",
        "Institution",
        "Fagligt center",
        "Direktørområde",
    ],
    "org_unit_level": ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8"],
    "responsibility": [
        "Personale: ansættelse/afskedigelse",
        "Beredskabsledelse",
        "Personale: øvrige administrative opgaver",
        "Personale: Sygefravær",
        "Ansvar for bygninger og arealer",
        "Personale: MUS-kompetence",
    ],
    "manager_type": [
        "Direktør",
        "Distriktsleder",
        "Beredskabschef",
        "Sekretariatschef",
        "Systemadministrator",
        "Områdeleder",
        "Centerchef",
        "Institutionsleder",
    ],
    "role_type": [
        "Tillidsrepræsentant",
        "Ergonomiambasadør",
        "Ansvarlig for sommerfest",
    ],
    "leave_type": [
        "Barselsorlov",
        "Forældreorlov",
        "Orlov til pasning af syg pårørende",
    ],
    "employee_address_type": [
        ("AdressePostEmployee", "Postadresse", "DAR"),
        ("PhoneEmployee", "Telefon", "PHONE"),
        ("LocationEmployee", "Lokation", "TEXT"),
        ("EmailEmployee", "Email", "EMAIL"),
    ],
    "manager_address_type": [
        ("EmailManager", "Email", "EMAIL"),
        ("TelefonManager", "Telefon", "PHONE"),
        ("AdressePostManager", "Adresse", "DAR"),
        ("WebManager", "Webadresse", "TEXT"),
    ],
    "org_unit_address_type": [
        ("AddressMailUnit", "Postadresse", "DAR"),
        ("AdressePostRetur", "Returadresse", "DAR"),
        ("AdresseHenvendelsessted", "Henvendelsessted", "DAR"),
        ("LocationUnit", "Lokation", "TEXT"),
        ("Skolekode", "Skolekode", "TEXT"),
        ("Formålskode", "Formålskode", "TEXT"),
        ("Afdelingskode", "Afdelingskode", "TEXT"),
        ("EmailUnit", "Email", "EMAIL"),
        ("PhoneUnit", "Telefon", "PHONE"),
        ("FaxUnit", "Fax", "PHONE"),
        ("EAN", "EAN-nummer", "EAN"),
        ("WebUnit", "Webadresse", "WWW"),
        ("p-nummer", "P-nummer", "PNUMBER"),
    ],
    "manager_level": ["Niveau 1", "Niveau 2", "Niveau 3", "Niveau 4"],
    "time_planning": ["Arbejdstidsplaner", "Dannes ikke", "Tjenestetid"],
    "engagement_type": ["Ansat"],
    "visibility": [
        ("Ekstern", "Må vises eksternt", "PUBLIC"),
        ("Intern", "Må vises internt", "INTERNAL"),
        ("Hemmelig", "Hemmelig", "SECRET"),
    ],
    "primary_type": [
        ("explicitly-primary", "Manuelt primær ansættelse", "5000"),
        ("primary", "Primær", "3000"),
        ("non-primary", "Ikke-primær ansættelse", "0"),
    ],
    "org_unit_hierarchy": [],
}

CLASSES: Dict[str, List[Tuple[str, str, str]]] = {}

for facetbvn, classes in IN_CLASSES.items():
    CLASSES[facetbvn] = list(
        map(
            lambda clazz: clazz if isinstance(clazz, tuple) else (clazz, clazz, "TEXT"),
            classes,
        )
    )


def generate_lora_flatfile(
    name: str, dummy_classes: bool = False
) -> LoraFlatFileFormat:
    seed = name

    generate_uuid = ra_utils.generate_uuid.uuid_generator(seed)

    organisation = Organisation.from_simplified_fields(
        uuid=generate_uuid(""),
        name=name,
        user_key=name,
    )

    def construct_facets(facetbvn: str) -> Facet:
        facet = Facet.from_simplified_fields(
            uuid=generate_uuid(facetbvn),
            user_key=facetbvn,
            organisation_uuid=organisation.uuid,
        )
        return facet

    @apply
    def construct_class(facetbvn: str, user_key: str, title: str, scope: str) -> Klasse:
        klasse = Klasse.from_simplified_fields(
            facet_uuid=generate_uuid(facetbvn),
            uuid=generate_uuid(user_key),
            user_key=user_key,
            title=title,
            scope=scope,
            organisation_uuid=organisation.uuid,
        )
        return klasse

    def yield_class() -> Iterator[Tuple[str, str, str, str]]:
        for facetbvn, classes in CLASSES.items():
            for user_key, title, scope in classes:
                yield facetbvn, user_key, title, scope

    facets = list(map(construct_facets, CLASSES.keys()))
    klasses = list(map(construct_class, yield_class()))

    flatfile = LoraFlatFileFormat(
        chunks=[
            LoraFlatFileFormatChunk(organisation=organisation),
            LoraFlatFileFormatChunk(
                facetter=facets,
            ),
            LoraFlatFileFormatChunk(klasser=klasses if dummy_classes else []),
        ],
    )
    return flatfile
