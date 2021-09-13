# Copyright 2021 Karlsruhe Institute of Technology
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
import json
from copy import deepcopy
from io import BytesIO

import qrcode
from flask_babel import gettext as _
from flask_login import current_user

from .extras import is_nested_type
from .models import File
from .models import RecordLink
from .schemas import FileSchema
from .schemas import RecordLinkSchema
from .schemas import RecordSchema
from .utils import get_permitted_record_links
from kadi.lib.conversion import parse_datetime_string
from kadi.lib.format import filesize
from kadi.lib.format import pretty_type_name
from kadi.lib.pdf import PDF
from kadi.lib.resources.utils import get_linked_resources
from kadi.lib.web import url_for
from kadi.modules.collections.models import Collection
from kadi.modules.collections.schemas import CollectionSchema


class RecordPDF(PDF):
    """Record PDF generation class.

    :param record: The record to generate a PDF from.
    :param extras: (optional) The extra metadata of the record to print, which can be
        used to e.g. exclude certain values beforehand. Defaults to the full extra
        metadata of the given record.
    :param exclude_creator: (optional) Flag indicating whether information about the
        given record's creator should be excluded.
    :param exclude_links: (optional) Either a flag or a string indicating whether to
        exclude all (``True``), outgoing (``"out"``) or incoming (``"in"``) links of
        the given record with other records.
    :param exclude_collections: (optional) Flag indicating whether to exclude
        information about collections the given record is part of.
    :param user: (optional) The user to check for various access permissions when
        generating the PDF. Defaults to the current user.
    """

    def __init__(
        self,
        record,
        extras=None,
        exclude_creator=False,
        exclude_links=False,
        exclude_collections=False,
        user=None,
    ):
        self.record = record
        self.extras = extras if extras is not None else record.extras
        self.exclude_creator = exclude_creator
        self.exclude_collections = exclude_collections
        self.exclude_links = exclude_links
        self.user = user if user is not None else current_user

        super().__init__(title=self.record.title)

        self.print_overview()
        self.ln(h=15)
        self.print_extras()
        self.ln(h=15)
        self.print_files()

        if self.exclude_links is not True:
            self.ln(h=15)
            self.print_record_links()

        if not self.exclude_collections:
            self.ln(h=15)
            self.print_collections()

    def _print_heading(self, txt):
        # Basic heuristic to try avoiding widowed headings.
        if self.will_page_break(self.font_size + 10):
            self.add_page()

        self.start_section(txt)
        self.set_font(size=10, style="B")
        self.write(txt=txt)
        self.ln(h=self.font_size + 1)
        self.set_draw_color(r=150, g=150, b=150)
        self.line(self.l_margin, self.y, self.w - self.r_margin, self.y)
        self.set_draw_color(r=0, g=0, b=0)

    def _print_placeholder(self, txt):
        self.set_font(size=10, style="I")
        self.set_text_color(r=150, g=150, b=150)
        self.write(txt=txt)
        self.set_text_color(r=0, g=0, b=0)
        self.ln()

    def print_overview(self):
        """Print the record overview, i.e. the basic metadata of the record."""
        self.start_section(_("Overview"))

        # Top right header content.
        image_size = 20
        view_record_url = url_for("records.view_record", id=self.record.id)
        image = qrcode.make(view_record_url)
        cursor_x = self.x
        cursor_y = self.y
        start_x = self.w - self.r_margin - image_size

        self.image(
            image.get_image(),
            x=start_x,
            y=cursor_y,
            w=image_size,
            h=image_size,
            link=view_record_url,
        )
        self.rect(start_x, cursor_y, image_size, image_size)
        self.set_xy(start_x, cursor_y + image_size + 2)
        self.set_font(size=8)
        self.set_text_color(r=150, g=150, b=150)
        self.cell(w=image_size, txt=f"ID: {self.record.id}", align="C")
        self.set_text_color(r=0, g=0, b=0)
        self.set_xy(cursor_x, cursor_y)

        # Top left header content.
        cell_width = self.epw * 0.85

        self.set_font(size=13, style="B")
        self.multi_cell(cell_width, txt=self.record.title, align="L")
        self.ln(h=2)

        self.set_font(size=10)
        self.multi_cell(cell_width, txt=f"@{self.record.identifier}", align="L")
        self.ln(h=5)

        if self.record.type:
            self.set_font(style="B")
            self.multi_cell(
                cell_width, txt="{}: {}".format(_("Type"), self.record.type), align="L"
            )
            self.ln(h=15)
        else:
            self.ln(h=10)

        # Description.
        if self.record.description:
            self.set_font(family="DejaVuSansMono")
            self.write(txt=self.record.description)
            self.set_font(family="DejaVuSans")
        else:
            self._print_placeholder(_("No description."))

        self.ln(h=self.font_size + 15)

        # Creator.
        if not self.exclude_creator:
            self.set_font(size=10)
            self.write(txt="{} ".format(_("Created by")))
            self.set_font(style="B")
            self.write(
                txt=self.record.creator.identity.displayname,
                link=url_for("accounts.view_user", id=self.record.creator.id),
            )
            self.ln(h=self.font_size + 3)

        # Creation date.
        self.set_font()
        self.write(
            txt="{} {}".format(
                _("Created at"), self.format_date(self.record.created_at)
            )
        )
        self.ln(h=self.font_size)

        # License and tags.
        if self.record.license or self.record.tags.count() > 0:
            self.ln(h=5)
            self.set_draw_color(r=150, g=150, b=150)
            self.line(self.l_margin, self.y, self.w - self.r_margin, self.y)
            self.set_draw_color(r=0, g=0, b=0)
            self.ln(h=5)

            if self.record.license:
                self.set_font(style="B")
                self.write(txt="{}: ".format(_("License")))
                self.set_font()
                self.write(txt=self.record.license.title, link=self.record.license.url)
                self.ln()

            if self.record.tags.count() > 0:
                if self.record.license:
                    self.ln(h=3)

                self.set_font(style="B")
                self.write(txt="{}: ".format(_("Tags")))
                self.set_font()
                self.write(txt="; ".join([tag.name for tag in self.record.tags]))
                self.ln()

    def print_extras(self):
        """Print the extra metadata of the record."""
        self._print_heading(_("Extra metadata"))
        self.ln(h=5)

        if self.extras:
            self.set_font(size=9)
            self.set_draw_color(r=200, g=200, b=200)
            self._print_extras(self.extras)
            self.set_draw_color(r=0, g=0, b=0)
        else:
            self._print_placeholder(txt=_("No extra metadata."))

    def _print_extras(self, extras, depth=0):
        for index, extra in enumerate(extras):
            self._print_extra(index, extra, depth)

            if is_nested_type(extra["type"]):
                self._print_extras(extra["value"], depth=depth + 1)

        if depth == 0:
            self.line(self.l_margin, self.y, self.w - self.r_margin, self.y)

    def _set_nested_color(self, depth):
        if depth % 2 == 1:
            self.set_fill_color(r=240, g=240, b=240)
        else:
            self.set_fill_color(r=256, g=256, b=256)

    def _print_extra(self, index, extra, depth):
        nested_margin = 5
        column_width = (self.epw - nested_margin * depth) / 10

        # Calculate the maximum height the cells require.
        key_width = column_width * 8
        value_width = 0
        unit_width = 0
        type_width = column_width * 2

        key_txt = extra.get("key", f"({index + 1})")
        value_txt = ""
        unit_txt = ""
        type_txt = pretty_type_name(extra["type"]).capitalize()

        if not is_nested_type(extra["type"]):
            key_width = column_width * 4

            if extra.get("unit"):
                value_width = column_width * 3
                unit_width = column_width
                unit_txt = extra["unit"]
            else:
                value_width = column_width * 4

            value_txt = json.dumps(extra["value"])

            if extra["value"] is not None:
                if extra["type"] == "str":
                    value_txt = extra["value"]
                elif extra["type"] == "date":
                    date_time = parse_datetime_string(extra["value"])
                    value_txt = self.format_date(date_time, include_micro=True)

        max_height = self.calculate_max_height(
            [
                (key_width, key_txt, "B" if is_nested_type(extra["type"]) else ""),
                (value_width, value_txt, ""),
                (unit_width, unit_txt, ""),
                (type_width, type_txt, ""),
            ]
        )
        cell_height = max_height + 2
        page_break = False

        if self.will_page_break(cell_height):
            self.line(self.l_margin, self.y, self.w - self.r_margin, self.y)
            self.add_page()
            page_break = True

        cursor_y = self.y

        # Print the "boxes" of the nested parent metadata entry, which automatically
        # gives us the correct left margin.
        for i in range(0, depth):
            self._set_nested_color(i)
            self.cell(w=nested_margin, h=cell_height, border="L", fill=True)

        self._set_nested_color(depth)

        if is_nested_type(extra["type"]):
            self.set_font(style="B")
            key_border = "LT"
        else:
            key_border = "LTB"

        cursor_x = self.x
        self.cell(w=key_width, h=cell_height, border=key_border, fill=True)
        self.set_xy(cursor_x, cursor_y + 1)
        self.multi_cell(key_width, txt=key_txt, align="L")
        self.set_xy(self.x, cursor_y)
        self.set_font()

        if not is_nested_type(extra["type"]):
            if extra["value"] is None:
                self.set_font(style="I")

            cursor_x = self.x
            self.cell(w=value_width, h=cell_height, border="TB", fill=True)
            self.set_xy(cursor_x, cursor_y + 1)
            self.multi_cell(value_width, txt=value_txt, align="L")
            self.set_xy(self.x, cursor_y)
            self.set_font()

            if extra.get("unit"):
                cursor_x = self.x
                self.cell(w=unit_width, h=cell_height, border="TB", fill=True)
                self.set_xy(cursor_x, cursor_y + 1)
                self.set_text_color(r=150, g=150, b=150)
                self.multi_cell(unit_width, txt=unit_txt, align="R")
                self.set_xy(self.x, cursor_y)

        if is_nested_type(extra["type"]):
            type_border = "RT"
        else:
            type_border = "RTB"

        cursor_x = self.x
        self.cell(w=type_width, h=cell_height, border=type_border, fill=True)
        self.set_xy(cursor_x, cursor_y + 1)
        self.set_text_color(r=150, g=150, b=150)
        self.multi_cell(type_width, txt=type_txt, align="R")
        self.set_text_color(r=0, g=0, b=0)
        self.set_y(cursor_y)
        self.ln(h=cell_height)

        # Draw this line at the end so it is completely on top of the cells.
        if page_break:
            self.line(self.l_margin, cursor_y, self.w - self.r_margin, cursor_y)

    def print_files(self):
        """Print the files of the record."""
        self._print_heading(_("Files"))

        if self.record.active_files.count() > 0:
            self.set_font()

            for file in self.record.active_files.order_by(File.created_at):
                self.ln(h=5)

                # Calculate the maximum height the cells require.
                name_width = self.epw * 0.85
                size_width = self.epw * 0.15

                name_txt = file.name
                size_txt = filesize(file.size)

                max_height = self.calculate_max_height(
                    [(name_width, name_txt, ""), (size_width, size_txt, "")]
                )

                if self.will_page_break(max_height):
                    self.add_page()

                cursor_y = self.y

                self.multi_cell(
                    name_width,
                    txt=name_txt,
                    link=url_for(
                        "records.view_file", record_id=self.record.id, file_id=file.id
                    ),
                    align="L",
                    ln=3,
                )
                self.set_text_color(r=150, g=150, b=150)
                self.multi_cell(size_width, txt=size_txt, align="R")
                self.set_text_color(r=0, g=0, b=0)
                self.set_y(cursor_y)
                self.ln(h=max_height)
        else:
            self.ln(h=5)
            self._print_placeholder(txt=_("No files."))

    def print_record_links(self):
        """Print the links of the record with other records."""
        self._print_heading(_("Record links"))

        direction = None

        if self.exclude_links == "in":
            direction = "to"
        elif self.exclude_links == "out":
            direction = "from"

        record_links = get_permitted_record_links(
            self.record, direction=direction, user=self.user
        ).order_by(RecordLink.created_at.desc())

        if record_links.count() > 0:
            for record_link in record_links:
                self.set_font()
                self.ln(h=5)

                # Calculate the maximum height the cells require.
                record_width = self.epw * 0.35
                link_width = self.epw * 0.3

                record_from_txt = f"@{record_link.record_from.identifier}"
                record_link_txt = record_link.name
                record_to_txt = f"@{record_link.record_to.identifier}"

                max_height = self.calculate_max_height(
                    [
                        (record_width, record_from_txt, ""),
                        (link_width, record_link_txt, ""),
                        (record_width, record_to_txt, ""),
                    ]
                )

                if self.will_page_break(max_height):
                    self.add_page()

                cursor_y = self.y

                if record_link.record_from == self.record:
                    self.set_font(style="I")

                self.multi_cell(
                    record_width,
                    txt=f"@{record_link.record_from.identifier}",
                    link=url_for("records.view_record", id=record_link.record_from.id),
                    align="L",
                    ln=3,
                )
                self.set_font()
                self.set_text_color(r=150, g=150, b=150)
                self.multi_cell(link_width, txt=record_link.name, align="L", ln=3)
                self.set_text_color(r=0, g=0, b=0)

                if record_link.record_to == self.record:
                    self.set_font(style="I")

                self.multi_cell(
                    record_width,
                    txt=f"@{record_link.record_to.identifier}",
                    link=url_for("records.view_record", id=record_link.record_to.id),
                    align="L",
                )
                self.set_y(cursor_y)
                self.ln(h=max_height)
        else:
            self.ln(h=5)
            self._print_placeholder(txt=_("No record links."))

    def print_collections(self):
        """Print the collections the record is part of."""
        self._print_heading(_("Collections"))

        collections = get_linked_resources(
            Collection, self.record.collections, user=self.user
        ).order_by(Collection.last_modified.desc())

        if collections.count() > 0:
            self.set_font()

            for collection in collections:
                self.ln(h=5)
                self.write(
                    txt=f"@{collection.identifier}",
                    link=url_for("collections.view_collection", id=collection.id),
                )
                self.ln()
        else:
            self.ln(h=5)
            self._print_placeholder(txt=_("No collections."))


def _filter_extras(extras, exclude_extras, use_indices=False):
    filtered_extras = []

    if not isinstance(exclude_extras, dict):
        exclude_extras = {}

    for index, extra in enumerate(extras):
        filter_key = str(index) if use_indices else extra.get("key", str(index))

        # If the dictionary corresponding to the key is empty, the whole extra is
        # excluded.
        if (
            filter_key in exclude_extras
            and isinstance(exclude_extras[filter_key], dict)
            and len(exclude_extras[filter_key]) == 0
        ):
            continue

        new_extra = deepcopy(extra)

        if is_nested_type(extra["type"]):
            new_extra["value"] = _filter_extras(
                extra["value"], exclude_extras.get(filter_key), use_indices=use_indices
            )

        filtered_extras.append(new_extra)

    return filtered_extras


def _get_json_data(record, export_filter, user):
    # Unnecessary meta attributes to exclude in all resources, also depending on whether
    # user information should be excluded.
    if export_filter.get("user", False):
        exclude_attrs = ["_actions", "_links", "creator"]
    else:
        exclude_attrs = ["_actions", "_links", "creator._actions", "creator._links"]

    # Collect the basic metadata of the record and exclude filtered extra metadata if
    # necessary.
    schema = RecordSchema(exclude=["extras", *exclude_attrs])
    data = schema.dump(record)

    extras = record.extras
    exclude_extras = export_filter.get("extras")

    if exclude_extras:
        extras = _filter_extras(
            extras, exclude_extras, export_filter.get("extras_use_indices", False)
        )

    data["extras"] = extras

    # Include all record files as "files".
    files = record.active_files.order_by(File.last_modified.desc())
    schema = FileSchema(many=True, exclude=exclude_attrs)
    data["files"] = schema.dump(files)

    # If not excluded completely, include all, only outgoing or only incoming record
    # links as "links". Only the basic metadata is included for each record, while the
    # current record is always excluded completely, regardless of link direction.
    exclude_links = export_filter.get("links", False)

    if exclude_links is not True:
        direction = None

        if exclude_links == "in":
            direction = "to"
        elif exclude_links == "out":
            direction = "from"

        record_links = get_permitted_record_links(
            record, direction=direction, user=user
        ).order_by(RecordLink.created_at.desc())

        data["links"] = []

        for record_link in record_links:
            exclude_record_field = "record_from"
            exclude_attrs_field = "record_to"

            if record_link.record_to_id == record.id:
                exclude_record_field = "record_to"
                exclude_attrs_field = "record_from"

            schema = RecordLinkSchema(
                exclude=[
                    "_actions",
                    "_links",
                    exclude_record_field,
                    *(f"{exclude_attrs_field}.{attr}" for attr in exclude_attrs),
                ]
            )
            data["links"].append(schema.dump(record_link))

    # If not excluded, include all collections the record is part of as "collections".
    # Only the basic metadata is included for each collection.
    if not export_filter.get("collections", False):
        collections = get_linked_resources(
            Collection, record.collections, user=user
        ).order_by(Collection.last_modified.desc())

        schema = CollectionSchema(many=True, exclude=exclude_attrs)
        data["collections"] = schema.dump(collections)

    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def _get_pdf_data(record, export_filter, user):
    extras = record.extras
    exclude_extras = export_filter.get("extras")

    if exclude_extras:
        extras = _filter_extras(
            extras, exclude_extras, export_filter.get("extras_use_indices", False)
        )

    exclude_links = export_filter.get("links", False)

    if exclude_links == "both":
        exclude_links = True

    pdf = RecordPDF(
        record,
        extras=extras,
        exclude_creator=export_filter.get("user", False),
        exclude_links=exclude_links,
        exclude_collections=export_filter.get("collections", False),
        user=user,
    )

    pdf_data = BytesIO()
    pdf.output(pdf_data)
    pdf_data.seek(0)

    return pdf_data


def _get_qr_data(record):
    image = qrcode.make(url_for("records.view_record", id=record.id))

    image_data = BytesIO()
    image.save(image_data, format="PNG")
    image_data.seek(0)

    return image_data


def get_export_data(record, export_type, export_filter=None, user=None):
    """Export a record in a given format.

    :param record: The record to export.
    :param export_type: The export format, one of ``"json"``, ``"pdf"`` or ``"qr"``.
    :param export_filter: (optional) A dictionary specifying various filters in order to
        exclude certain information from the returned export data. Currently only usable
        in combination with the ``"json"`` and ``"pdf"`` export types.

        **Example:**

        .. code-block:: python3

            {
                # Whether user information about the creator of the record or any linked
                # resource should be excluded.
                "user": False,
                # Whether to exclude information about collections the record is part
                # of.
                "collections": False,
                # Whether to exclude all (True), outgoing ("out") or incoming ("in")
                # links of the record with other records.
                "links": False,
                # A dictionary specifying a filter mask of extra metadata to exclude.
                # Depending on "extras_use_indices", each key of the dictionary
                # specifies either a key or an index (as string) that should be
                # excluded. As shown in the example below, the value of each key can
                # either be an empty dictionary, to exclude the whole extra including
                # all of its potentially nested values, or another dictionary with the
                # same possibilities as in the parent dictionary.
                "extras": {"sample_key": {}, "sample_list": {"0": {}}},
                # Whether to use indices instead of keys for the extra metadata filter
                # mask.
                "extras_use_indices": False,
            }

    :param user: (optional) The user to check for various access permissions when
        generating the export data. Defaults to the current user.
    :return: The exported record data, depending on the given export type, or ``None``
        if an unknown export type was given.
    """
    export_filter = export_filter if export_filter is not None else {}
    user = user if user is not None else current_user

    if export_type == "json":
        return _get_json_data(record, export_filter, user)

    if export_type == "pdf":
        return _get_pdf_data(record, export_filter, user)

    if export_type == "qr":
        return _get_qr_data(record)

    return None
