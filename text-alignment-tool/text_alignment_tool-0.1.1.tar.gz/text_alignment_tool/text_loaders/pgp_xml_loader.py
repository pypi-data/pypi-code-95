from lxml import etree
from pathlib import Path
from typing import NamedTuple
from io import BufferedReader
import cursive_re

from ..shared_classes import TextChunk, LetterList
from .text_loader import TextLoader
import numpy as np


class PgpXmlTeiInputPosition(NamedTuple):
    filename: str
    line_number: str
    word_index: int


class PgpXmlTeiAlignmentMap(NamedTuple):
    input_position: PgpXmlTeiInputPosition
    output_idx: int


class PgpXmlTeiTextLoader(TextLoader):
    def __init__(self, file_paths: list[Path]):
        super().__init__(file_paths)
        self._input_output_map: list[PgpXmlTeiAlignmentMap] = []

    def _load(self) -> LetterList:
        self.parse_pgp_tei_files()
        return super()._load()

    @staticmethod
    def close_open_brackets(text: str):
        if not text:
            return text

        unclosed_line_beginning = (
            cursive_re.beginning_of_line()
            + cursive_re.zero_or_more(cursive_re.none_of("["))
            + cursive_re.text("]")
        )
        unclosed_line_beginning_re = cursive_re.compile(unclosed_line_beginning)
        if unclosed_line_beginning_re.match(text):
            text = "[" + text

        if unclosed_line_beginning_re.match(
            text[::-1].replace("[", ";").replace("]", "[").replace(";", "]")
        ):
            text = text + "]"

        return text

    def parse_pgp_tei_files(self):
        events = ("start", "end")
        needed_elements = {
            "tei_header": "{http://www.tei-c.org/ns/1.0}teiHeader",
            "text": "{http://www.tei-c.org/ns/1.0}text",
            "body": "{http://www.tei-c.org/ns/1.0}body",
            "div": "{http://www.tei-c.org/ns/1.0}div",
            "l": "{http://www.tei-c.org/ns/1.0}l",
        }
        for file in self._file_paths:
            with open(file, "rb") as xml_data:
                self.parse_tei(xml_data, file.name, events, needed_elements)

    def parse_tei(
        self,
        xml_data: BufferedReader,
        filename: str,
        events: tuple[str, str],
        needed_elements: dict,
    ):
        letter_list: list[int] = []
        block = -1
        line = -1
        response = {"part": []}
        token_idx_count = 0
        text_chunk_indices: list[TextChunk] = []

        for action, element in etree.iterparse(
            xml_data, events=events, tag=needed_elements.values()
        ):
            if action == "start":
                if element.tag == needed_elements["tei_header"]:
                    response["header_metadata"] = etree.tostring(element).decode()

                elif element.tag == needed_elements["div"]:
                    response["part"].append({"block": [{"lines": []}]})
                    block += 1
                    line = -1

                elif element.tag == needed_elements["l"]:
                    line_number = element.attrib.get("n", "")
                    text = self.close_open_brackets(element.text)
                    if text:
                        chunk_start_idx = len(self._output)
                        line += 1
                        for idx, token in enumerate(text):
                            token_idx_count += 1
                            letter_list.append(ord(token))
                            self._input_output_map.append(
                                PgpXmlTeiAlignmentMap(
                                    PgpXmlTeiInputPosition(filename, line_number, idx),
                                    len(self._output) - 1,
                                )
                            )
                        chunk_end_idx = len(self._output) - 1
                        if chunk_start_idx < chunk_end_idx:
                            text_chunk_indices.append(
                                TextChunk(chunk_start_idx, chunk_end_idx)
                            )

            if action == "end":
                if element.tag in [
                    needed_elements["tei_header"],
                    needed_elements["div"],
                ]:
                    element.clear()

        self._output: LetterList = np.array(letter_list)
        self._text_chunk_indices = text_chunk_indices
