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
import os

from flask import current_app
from flask_babel import gettext as _
from fpdf import FPDF

from kadi.lib.utils import utcnow


class PDF(FPDF):
    """Base PDF generation class using FPDF.

    :param title: (optional) The title of the PDF, which will appear in the header on
        each page and in the metadata of the PDF itself.
    """

    def __init__(self, title=""):
        self.title = title
        self.generated_at = utcnow()

        fonts_path = current_app.config["FONTS_PATH"]
        super().__init__(font_cache_dir=fonts_path)

        self.add_font(
            "DejaVuSans",
            fname=os.path.join(fonts_path, "dejavu", "DejaVuSans.ttf"),
            uni=True,
        )
        self.add_font(
            "DejaVuSans",
            fname=os.path.join(fonts_path, "dejavu", "DejaVuSans-Bold.ttf"),
            uni=True,
            style="B",
        )
        self.add_font(
            "DejaVuSans",
            fname=os.path.join(fonts_path, "dejavu", "DejaVuSans-Oblique.ttf"),
            uni=True,
            style="I",
        )
        self.add_font(
            "DejaVuSansMono",
            fname=os.path.join(fonts_path, "dejavu", "DejaVuSansMono.ttf"),
            uni=True,
        )

        self.set_font(size=10, family="DejaVuSans")
        self.set_title(self.title)
        self.add_page()

    @staticmethod
    def format_date(date_time, include_micro=False):
        """Format a datetime object in a user-readable manner.

        :param date_time: The datetime object to format.
        :param include_micro: (optional) Flag indicating whether to include microseconds
            in the formatted datetime.
        :return: The formatted datetime string.
        """
        fmt = "%Y-%m-%d %H:%M:%S"
        if include_micro:
            fmt += ".%f"

        return date_time.strftime(f"{fmt} %Z")

    def header(self):
        """Automatically prints a header on each page of the generated PDF."""
        self.set_font(size=10)
        self.truncated_cell(self.epw * 0.85, txt=self.title, align="L")
        self.cell(w=self.epw * 0.15, txt="Kadi4Mat", align="R")
        self.ln(self.font_size + 1)
        self.line(self.l_margin, self.y, self.w - self.r_margin, self.y)
        self.ln(h=5)

    def footer(self):
        """Automatically prints a footer on each page of the generated PDF."""
        self.set_font(size=10)
        self.set_text_color(r=150, g=150, b=150)
        self.set_y(-10)
        self.cell(
            w=self.epw / 2,
            txt="{} {}".format(_("Generated at"), self.format_date(self.generated_at)),
            align="L",
        )
        self.cell(w=self.epw / 2, txt=str(self.page), align="R")

    def truncated_cell(self, w, txt="", **kwargs):
        r"""Print a cell with potentially truncated text based on the cell's width.

        :param w: The width of the cell.
        :param txt: (optional) The text content of the cell.
        :param \**kwargs: Additional keyword arguments to pass to fpdf2's ``cell``
            function.
        """
        truncated_txt = txt

        while self.get_string_width(truncated_txt) > w:
            truncated_txt = truncated_txt[:-1]

        if truncated_txt != txt:
            truncated_txt = f"{truncated_txt[:-3]}..."

        self.cell(w=w, txt=truncated_txt, **kwargs)

    def calculate_max_height(self, contents):
        """Calculate the maximum height that will be required by multiple multi-cells.

        Note that this method always uses the current font family and size for its
        calculations.

        :param contents: A list of tuples containing the width, the text content and the
            font style of each cell.
        :return: The maximum height the cells will require.
        """
        num_lines = 0
        font_style = self.font_style

        for width, text, style in contents:
            self.set_font(style=style)
            num_lines = max(
                num_lines, len(self.multi_cell(width, txt=text, split_only=True))
            )

        # Switch back to the original font style.
        self.set_font(style=font_style)
        return num_lines * self.font_size
