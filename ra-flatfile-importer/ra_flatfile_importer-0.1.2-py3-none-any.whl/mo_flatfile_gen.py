#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from itertools import chain

import ra_utils.generate_uuid
from ramodels.mo import Employee
from ramodels.mo import OrganisationUnit
from ramodels.mo.details import Address
from ramodels.mo.details import Engagement
from ramodels.mo.details import Manager

from ra_flatfile_importer.mo_flatfile_model import MOFlatFileFormat
from ra_flatfile_importer.mo_flatfile_model import MOFlatFileFormatChunk


def generate_mo_flatfile(name: str) -> MOFlatFileFormat:
    seed = name

    generate_uuid = ra_utils.generate_uuid.uuid_generator(seed)

    flatfile = MOFlatFileFormat(
        chunks=[
            MOFlatFileFormatChunk(
                org_units=[
                    OrganisationUnit.from_simplified_fields(
                        uuid=generate_uuid(name),
                        user_key=name,
                        name=name,
                        org_unit_type_uuid=generate_uuid("Institution"),
                        org_unit_level_uuid=generate_uuid("N1"),
                        from_date="1967-12-08",
                    )
                    for name in ["Kommune bestyrelse"]
                ],
                employees=[
                    Employee(
                        uuid=generate_uuid(name),
                        givenname=givenname,
                        surname=surname,
                    )
                    for givenname, surname in [
                        ("Kim", "Kontorelev"),
                        ("Simon", "Specialist"),
                        ("Jimmy", "Jurist"),
                    ]
                ],
            ),
            MOFlatFileFormatChunk(
                org_units=[
                    OrganisationUnit.from_simplified_fields(
                        uuid=generate_uuid(name),
                        user_key=name,
                        name=name,
                        org_unit_type_uuid=generate_uuid("Institutionsafsnit"),
                        org_unit_level_uuid=generate_uuid("N2"),
                        parent_uuid=generate_uuid("Kommune bestyrelse"),
                        from_date="2012-04-03",
                    )
                    for name in ["Specialområde"]
                ],
                address=[
                    Address.from_simplified_fields(
                        uuid=generate_uuid("Jimmy Jurist Email"),
                        value="jimmy@example.org",
                        value2=None,
                        address_type_uuid=generate_uuid("EmailEmployee"),
                        org_uuid=generate_uuid(""),
                        from_date="2011-11-11",
                        person_uuid=generate_uuid("Jimmy Jurist"),
                    ),
                    Address.from_simplified_fields(
                        uuid=generate_uuid("Jimmy Jurist Phone"),
                        value="88888888",
                        value2=None,
                        address_type_uuid=generate_uuid("PhoneEmployee"),
                        org_uuid=generate_uuid(""),
                        from_date="2011-11-12",
                        person_uuid=generate_uuid("Jimmy Jurist"),
                    ),
                    Address.from_simplified_fields(
                        uuid=generate_uuid("Kommune bestyrelse Phone"),
                        value="00000000",
                        value2=None,
                        address_type_uuid=generate_uuid("PhoneUnit"),
                        org_uuid=generate_uuid(""),
                        from_date="1930-01-01",
                        org_unit_uuid=generate_uuid("Kommune bestyrelse"),
                    ),
                ],
                manager=[
                    Manager.from_simplified_fields(
                        uuid=generate_uuid("Jimmy leader"),
                        org_unit_uuid=generate_uuid("Kommune bestyrelse"),
                        person_uuid=generate_uuid("Jimmy Jurist"),
                        responsibility_uuids=[
                            generate_uuid("Personale: ansættelse/afskedigelse")
                        ],
                        manager_level_uuid=generate_uuid("Niveau 1"),
                        manager_type_uuid=generate_uuid("Direktør"),
                        from_date="2015-01-02",
                    )
                ],
            ),
            MOFlatFileFormatChunk(
                engagements=list(
                    chain(
                        (
                            Engagement.from_simplified_fields(
                                uuid=generate_uuid(user_key),
                                org_unit_uuid=generate_uuid("Kommune bestyrelse"),
                                person_uuid=generate_uuid("Kim Kontorelev"),
                                job_function_uuid=generate_uuid("Kontorelev"),
                                engagement_type_uuid=generate_uuid("Ansat"),
                                from_date="1970-01-01",
                                to_date=None,
                                primary_uuid=generate_uuid("primary"),
                                user_key=user_key,
                            )
                            for user_key in ["1337"]
                        ),
                        (
                            Engagement.from_simplified_fields(
                                uuid=generate_uuid(user_key),
                                org_unit_uuid=generate_uuid("Kommune bestyrelse"),
                                person_uuid=generate_uuid("Jimmy Jurist"),
                                job_function_uuid=generate_uuid("Jurist"),
                                engagement_type_uuid=generate_uuid("Ansat"),
                                from_date="1990-04-20",
                                to_date=None,
                                primary_uuid=generate_uuid("primary"),
                                user_key=user_key,
                            )
                            for user_key in ["1338"]
                        ),
                        (
                            Engagement.from_simplified_fields(
                                uuid=generate_uuid(user_key),
                                org_unit_uuid=generate_uuid("Specialområde"),
                                person_uuid=generate_uuid("Simon Specialist"),
                                job_function_uuid=generate_uuid("Specialist"),
                                engagement_type_uuid=generate_uuid("Ansat"),
                                from_date="2000-12-31",
                                to_date=None,
                                primary_uuid=generate_uuid("primary"),
                                user_key=user_key,
                            )
                            for user_key in ["1339"]
                        ),
                        (
                            Engagement.from_simplified_fields(
                                uuid=generate_uuid(user_key),
                                org_unit_uuid=generate_uuid("Kommune bestyrelse"),
                                person_uuid=generate_uuid("Simon Specialist"),
                                job_function_uuid=generate_uuid("Specialist"),
                                engagement_type_uuid=generate_uuid("Ansat"),
                                from_date="2001-01-01",
                                to_date=None,
                                primary_uuid=generate_uuid("non-primary"),
                                user_key=user_key,
                            )
                            for user_key in ["x200"]
                        ),
                    )
                ),
            ),
        ],
    )
    return flatfile
