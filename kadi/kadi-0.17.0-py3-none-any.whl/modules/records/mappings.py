# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from copy import deepcopy

from elasticsearch_dsl import Boolean
from elasticsearch_dsl import Date
from elasticsearch_dsl import Document
from elasticsearch_dsl import Double
from elasticsearch_dsl import InnerDoc
from elasticsearch_dsl import Keyword
from elasticsearch_dsl import Long
from elasticsearch_dsl import MetaField
from elasticsearch_dsl import Nested
from elasticsearch_dsl import Text

from .extras import is_nested_type
from kadi.lib.search.core import MappingMixin


class ExtraMapping(InnerDoc):
    """Base search mapping for extra record metadata.

    See :attr:`.Record.extras`.
    """

    key = Text(
        required=True,
        analyzer=MappingMixin.trigram_analyzer,
        fields={"keyword": Keyword()},
    )


class ExtraMappingString(ExtraMapping):
    """Search mapping for extra record metadata as string.

    See :attr:`.Record.extras`.
    """

    value = Text(analyzer=MappingMixin.trigram_analyzer, fields={"keyword": Keyword()})


class ExtraMappingInteger(ExtraMapping):
    """Search mapping for extra record metadata as integer.

    Uses long values for the internal representation. See :attr:`.Record.extras`.
    """

    value = Long()

    unit = Text()


class ExtraMappingFloat(ExtraMapping):
    """Search mapping for extra record metadata as float.

    Uses double values for the internal representation. See :attr:`.Record.extras`.
    """

    value = Double()

    unit = Text()


class ExtraMappingBoolean(ExtraMapping):
    """Search mapping for extra record metadata as boolean.

    See :attr:`.Record.extras`.
    """

    value = Boolean()


class ExtraMappingDate(ExtraMapping):
    """Search mapping for extra record metadata as date.

    See :attr:`.Record.extras`.
    """

    value = Date(default_timezone="UTC")


class RecordMapping(Document, MappingMixin):
    """Search mapping for records.

    See :class:`.Record`.
    """

    class Meta:
        """Container to store meta class attributes."""

        dynamic = MetaField(False)

    identifier = Text(
        required=True,
        analyzer=MappingMixin.trigram_analyzer,
        fields={"text": Text(), "keyword": Keyword()},
    )

    title = Text(
        required=True,
        analyzer=MappingMixin.trigram_analyzer,
        fields={"text": Text(), "keyword": Keyword()},
    )

    plain_description = Text(required=True)

    created_at = Date(required=True, default_timezone="UTC")

    last_modified = Date(required=True, default_timezone="UTC")

    extras_str = Nested(ExtraMappingString)

    extras_int = Nested(ExtraMappingInteger)

    extras_float = Nested(ExtraMappingFloat)

    extras_bool = Nested(ExtraMappingBoolean)

    extras_date = Nested(ExtraMappingDate)

    @classmethod
    def _flatten_extras(cls, extras, key_prefix=""):
        flat_extras = []

        for index, extra in enumerate(extras):
            if is_nested_type(extra["type"]):
                flat_extras += cls._flatten_extras(
                    extra["value"],
                    key_prefix=f"{key_prefix}{extra.get('key', index + 1)}.",
                )
            else:
                new_extra = deepcopy(extra)

                if "key" in extra:
                    new_extra["key"] = f"{key_prefix}{extra['key']}"
                else:
                    new_extra["key"] = f"{key_prefix}{index + 1}"

                flat_extras.append(new_extra)

        return flat_extras

    @classmethod
    def create_document(cls, obj):
        """Create a new document to be indexed in ElasticSearch.

        :param obj: The object to be indexed.
        :param document: The mapping class instance.
        :return: The created document.
        """
        document = super().create_document(obj)

        type_container = {
            "extras_str": [],
            "extras_int": [],
            "extras_float": [],
            "extras_bool": [],
            "extras_date": [],
        }

        flat_extras = cls._flatten_extras(obj.extras)
        for extra in flat_extras:
            new_extra = {"key": extra["key"], "value": extra["value"]}

            if "unit" in extra:
                new_extra["unit"] = extra["unit"]

            type_container[f"extras_{extra['type']}"].append(new_extra)

        for type_name, extras in type_container.items():
            setattr(document, type_name, extras)

        return document
