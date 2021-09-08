import pandas as pd
from lxml import etree
from dotmap import DotMap
from pathlib import Path
from typing import NamedTuple
from ..shared_classes import TextChunk, LetterList
from ..alignment_algorithms import TextAlignments
from .text_loader import TextLoader
import numpy as np


class AltoInputPosition(NamedTuple):
    line_id: str
    word_index: int


class AltoAlignmentMap(NamedTuple):
    input_position: AltoInputPosition
    output_idx: int


class AltoXMLTextLoader(TextLoader):
    def __init__(
        self, file_paths: list[Path], estimated_number_of_lines_per_page: int = 60
    ):
        self.__serialized_xml = pd.DataFrame()
        self.__estimated_number_of_lines_per_page = estimated_number_of_lines_per_page
        super().__init__(file_paths)
        self._input_output_map: list[AltoAlignmentMap] = []

    def _load(self) -> LetterList:
        self.import_ocr_texts()
        tokens: list[int] = []
        token_idx_count = 0
        for _, row in self.__serialized_xml.iterrows():
            chunk_start_idx = token_idx_count
            for token_idx, token in enumerate(row.txt):
                token_idx_count += 1
                tokens.append(ord(token))
                self._input_output_map.append(
                    AltoAlignmentMap(
                        AltoInputPosition(str(row.line_ID), token_idx), len(tokens) - 1
                    )
                )
            chunk_end_idx = token_idx_count
            if chunk_start_idx < chunk_end_idx:
                self._text_chunk_indices.append(
                    TextChunk(chunk_start_idx, chunk_end_idx)
                )
        self._output: LetterList = np.array(tokens)

        return super()._load()

    @staticmethod
    def __poly_from_coords(x: int, y: int, w: int, h: int):
        return f"{x} {y} {x + w} {y} {x + w} {y + h} {x} {y + h} {x} {y}"

    def import_ocr_texts(self):
        self._input_output_map = []
        self.__serialized_xml = pd.DataFrame(
            {
                "order": pd.Series([], dtype=pd.UInt16Dtype()),
                "img": pd.Series([], dtype=pd.UInt16Dtype()),
                "zone": pd.Series([], dtype=pd.Float64Dtype()),
                "zone_on_page": pd.Series([], dtype=pd.UInt16Dtype()),
                "line": pd.Series([], dtype=pd.UInt16Dtype()),
                "y_region": pd.Series([], dtype=pd.UInt16Dtype()),
                "x_region": pd.Series([], dtype=pd.UInt16Dtype()),
                "h_region": pd.Series([], dtype=pd.UInt16Dtype()),
                "w_region": pd.Series([], dtype=pd.UInt16Dtype()),
                "y": pd.Series([], dtype=pd.UInt16Dtype()),
                "x": pd.Series([], dtype=pd.UInt16Dtype()),
                "h": pd.Series([], dtype=pd.UInt16Dtype()),
                "w": pd.Series([], dtype=pd.UInt16Dtype()),
                "img_name": pd.Series([], dtype=pd.StringDtype()),
                "region_ID": pd.Series([], dtype=pd.StringDtype()),
                "line_ID": pd.Series([], dtype=pd.StringDtype()),
                "baseline": pd.Series([], dtype=pd.StringDtype()),
                "polygon": pd.Series([], dtype=pd.StringDtype()),
                "txt": pd.Series([], dtype=pd.StringDtype()),
                "aligned_txt": pd.Series([], dtype=pd.StringDtype()),
                "cumul": pd.Series([], dtype=pd.Float64Dtype()),
                "length": pd.Series([], dtype=pd.UInt16Dtype()),
                "imgHeight": pd.Series([], dtype=pd.UInt16Dtype()),
                "imgWidth": pd.Series([], dtype=pd.UInt16Dtype()),
                "regionpolygon": pd.Series([], dtype=pd.StringDtype()),
                "regiontype": pd.Series([], dtype=pd.StringDtype()),
                "regiontagID": pd.Series([], dtype=pd.StringDtype()),
                "linetype": pd.Series([], dtype=pd.StringDtype()),
                "linetagID": pd.Series([], dtype=pd.StringDtype()),
                "xml_filename": pd.Series([], dtype=pd.StringDtype()),
            },
            index=range(
                len(self._file_paths) * self.__estimated_number_of_lines_per_page
            ),
        )  # Start with a reasonably sized table
        order = 0
        image_count = 0
        cumulative_text_length = 0

        for xml_file_path in self._file_paths:
            with open(xml_file_path, "rb") as xml_data:
                events = ("start", "end")
                needed_elements = DotMap(
                    {
                        "file_name": "{http://www.loc.gov/standards/alto/ns-v4#}fileName",
                        "page": "{http://www.loc.gov/standards/alto/ns-v4#}Page",
                        "description": "{http://www.loc.gov/standards/alto/ns-v4#}Description",
                        "other_tag": "{http://www.loc.gov/standards/alto/ns-v4#}OtherTag",
                        "text_block": "{http://www.loc.gov/standards/alto/ns-v4#}TextBlock",
                        "polygon": "{http://www.loc.gov/standards/alto/ns-v4#}Polygon",
                        "text_line": "{http://www.loc.gov/standards/alto/ns-v4#}TextLine",
                        "string": "{http://www.loc.gov/standards/alto/ns-v4#}String",
                    }
                )
                image_filename = ""
                image_height = 0
                image_width = 0
                tag_dict = {}

                zone_on_page_count = 0
                region_id = ""
                region_type_id = ""
                x_region = 0
                y_region = 0
                w_region = 0
                h_region = 0
                region_polygon = ""
                last_parent_tag = ""

                line_in_zone_count = 0
                line_id = ""
                line_type_id = ""
                x = 0
                y = 0
                w = 0
                h = 0
                line_polygon = ""
                line_baseline = ""
                line_text = ""

                for action, element in etree.iterparse(
                    xml_data, events=events, tag=needed_elements.values()
                ):
                    if action == "start":
                        if element.tag == needed_elements.text_line:
                            line_in_zone_count += 1
                            line_id = element.attrib["ID"]
                            line_type_id = element.attrib.get("TAGREFS", "")
                            y = int(float(element.attrib.get("VPOS", 0)))
                            x = int(float(element.attrib.get("HPOS", 0)))
                            h = int(float(element.attrib.get("HEIGHT", 0)))
                            w = int(float(element.attrib.get("WIDTH", 0)))
                            line_baseline = element.attrib.get("BASELINE", "")
                            last_parent_tag = element.tag

                        elif element.tag == needed_elements.string:
                            line_text = element.attrib.get("CONTENT", "")

                        elif element.tag == needed_elements.polygon:
                            if last_parent_tag == needed_elements.text_line:
                                line_polygon = element.attrib.get(
                                    "POINTS", self.__poly_from_coords(x, y, w, h)
                                )
                            elif last_parent_tag == needed_elements.text_block:
                                region_polygon = element.attrib.get(
                                    "POINTS",
                                    self.__poly_from_coords(
                                        x_region, y_region, w_region, h_region
                                    ),
                                )

                        elif element.tag == needed_elements.text_block:
                            zone_on_page_count += 1
                            line_in_zone_count = 0
                            region_id = element.attrib["ID"]
                            region_type_id = element.attrib.get("TAGREFS", "")
                            y_region = int(float(element.attrib.get("VPOS", 0)))
                            x_region = int(float(element.attrib.get("HPOS", 0)))
                            h_region = int(float(element.attrib.get("HEIGHT", 0)))
                            w_region = int(float(element.attrib.get("WIDTH", 0)))
                            last_parent_tag = element.tag

                        elif element.tag == needed_elements.other_tag:
                            if "ID" in element.attrib:
                                tag_dict[element.attrib["ID"]] = element.attrib.get(
                                    "LABEL", ""
                                )

                        elif element.tag == needed_elements.page:
                            image_height = int(float(element.attrib.get("HEIGHT", 0)))
                            image_width = int(float(element.attrib.get("WIDTH", 0)))

                        elif element.tag == needed_elements.file_name:
                            image_count += 1
                            image_filename = element.text

                    if action == "end":
                        if element.tag == needed_elements.text_line:
                            line_length = len(line_text)
                            cumulative_text_length += line_length
                            new_row = [
                                order,
                                image_count,
                                int(f"{image_count}0{zone_on_page_count:02}"),
                                zone_on_page_count,
                                line_in_zone_count,
                                y_region,
                                x_region,
                                h_region,
                                w_region,
                                y,
                                x,
                                h,
                                w,
                                image_filename,
                                region_id,
                                line_id,
                                line_baseline,
                                line_polygon,
                                line_text,
                                "".join([" " for x in line_text]),
                                cumulative_text_length,
                                line_length,
                                image_height,
                                image_width,
                                region_polygon,
                                tag_dict.get(region_type_id, ""),
                                region_type_id,
                                tag_dict.get(line_type_id, ""),
                                line_type_id,
                                xml_file_path.name,
                            ]
                            if order < len(self.__serialized_xml):
                                self.__serialized_xml.at[
                                    order, self.__serialized_xml.columns
                                ] = new_row
                            else:
                                self.__serialized_xml.append(
                                    pd.DataFrame(
                                        [new_row], columns=self.__serialized_xml.columns
                                    )
                                )

                            order += 1
                        element.clear()

        # Crop to only rows with values
        self.__serialized_xml = self.__serialized_xml.loc[
            self.__serialized_xml.first_valid_index() : self.__serialized_xml.last_valid_index()
        ]
        self.__serialized_xml["img_name"] = self.__serialized_xml.img_name.astype(
            "category"
        )
        self.__serialized_xml["region_ID"] = self.__serialized_xml.region_ID.astype(
            "category"
        )
        self.__serialized_xml["line_ID"] = self.__serialized_xml.line_ID.astype(
            "category"
        )
        self.__serialized_xml["baseline"] = self.__serialized_xml.baseline.astype(
            "category"
        )
        self.__serialized_xml["polygon"] = self.__serialized_xml.polygon.astype(
            "category"
        )
        self.__serialized_xml["txt"] = self.__serialized_xml.txt.astype("category")
        self.__serialized_xml["aligned_txt"] = self.__serialized_xml.aligned_txt.astype(
            pd.StringDtype()
        )
        self.__serialized_xml[
            "regionpolygon"
        ] = self.__serialized_xml.regionpolygon.astype("category")
        self.__serialized_xml["regiontype"] = self.__serialized_xml.regiontype.astype(
            "category"
        )
        self.__serialized_xml["regiontagID"] = self.__serialized_xml.regiontagID.astype(
            "category"
        )
        self.__serialized_xml["linetype"] = self.__serialized_xml.linetype.astype(
            "category"
        )
        self.__serialized_xml["linetagID"] = self.__serialized_xml.linetagID.astype(
            "category"
        )
        self.__serialized_xml[
            "xml_filename"
        ] = self.__serialized_xml.xml_filename.astype("category")

    def emend_original_with_aligned_text(
        self, alignment_pairs: TextAlignments, aligned_text: LetterList
    ) -> pd.DataFrame:
        # TODO: the emandation is not working quite right.
        alignment_pairs_dict: dict[int, list[int]] = {}
        for alignment in alignment_pairs.alignments:
            if alignment.query_idx not in alignment_pairs_dict:
                alignment_pairs_dict[alignment.query_idx] = []

            alignment_pairs_dict[alignment.query_idx].append(alignment.target_idx)

        input_to_aligned_text_map: list[AltoAlignmentMap] = []
        for input_position, output_idx in [
            (x.input_position, x.output_idx) for x in self._input_output_map
        ]:
            if output_idx in alignment_pairs_dict:
                for align_idx in alignment_pairs_dict[output_idx]:
                    input_to_aligned_text_map.append(
                        AltoAlignmentMap(input_position, align_idx)
                    )
                    pass

        input_to_aligned_text_map_dict: dict[str, list[int]] = {}
        # Yeah, that's a hacky bunch of shit in the middle to make the input key unique (it's almost the weekend and I don't want to think about the "right" way to do it)
        garbage = "@#$%^&"
        for alignment in input_to_aligned_text_map:
            unique_input_key = f"{alignment.input_position.line_id}{garbage}{alignment.input_position.word_index}"
            if unique_input_key not in alignment_pairs_dict:
                input_to_aligned_text_map_dict[unique_input_key] = []

            input_to_aligned_text_map_dict[unique_input_key].append(
                alignment.output_idx
            )

        # aligned_transcription: list[str] = []
        used_alinment_text_indices: list[int] = []
        for idx, entry in self.__serialized_xml.iterrows():
            line_text = ""
            for char_idx in range(len(entry.txt)):
                unique_input_key = f"{entry['line_ID']}{garbage}{char_idx}"
                if unique_input_key not in input_to_aligned_text_map_dict:
                    line_text += entry.txt[char_idx]
                    continue

                for alignment_idx in input_to_aligned_text_map_dict[unique_input_key]:
                    if alignment_idx not in used_alinment_text_indices:
                        used_alinment_text_indices.append(alignment_idx)
                        line_text += chr(aligned_text[alignment_idx])
            self.__serialized_xml.at[idx, "aligned_txt"] = line_text

        return self.__serialized_xml

    def replace_original_with_aligned_text(
        self, alignment_pairs: TextAlignments, aligned_text: LetterList
    ) -> pd.DataFrame:
        # TODO: as written this was originally going to be used to correct individual letters in the original
        # I repurposed it to simply replace the text with its match, but that can probably be done more simply.
        alignment_pairs_dict: dict[int, list[int]] = {}
        for alignment in alignment_pairs.alignments:
            if alignment.query_idx not in alignment_pairs_dict:
                alignment_pairs_dict[alignment.query_idx] = []

            alignment_pairs_dict[alignment.query_idx].append(alignment.target_idx)

        input_to_aligned_text_map: list[AltoAlignmentMap] = []
        for input_position, output_idx in [
            (x.input_position, x.output_idx) for x in self._input_output_map
        ]:
            if output_idx in alignment_pairs_dict:
                for align_idx in alignment_pairs_dict[output_idx]:
                    input_to_aligned_text_map.append(
                        AltoAlignmentMap(input_position, align_idx)
                    )
                    pass

        input_to_aligned_text_map_dict: dict[str, list[int]] = {}
        # Yeah, that's a hacky bunch of shit in the middle to make the input key unique (it's almost the weekend and I don't want to think about the "right" way to do it)
        garbage = "@#$%^&"
        for alignment in input_to_aligned_text_map:
            unique_input_key = f"{alignment.input_position.line_id}{garbage}{alignment.input_position.word_index}"
            if unique_input_key not in alignment_pairs_dict:
                input_to_aligned_text_map_dict[unique_input_key] = []

            input_to_aligned_text_map_dict[unique_input_key].append(
                alignment.output_idx
            )

        # aligned_transcription: list[str] = []
        used_alinment_text_indices: list[int] = []
        for idx, entry in self.__serialized_xml.iterrows():
            line_text = ""
            for char_idx in range(len(entry.txt)):
                unique_input_key = f"{entry['line_ID']}{garbage}{char_idx}"
                # if unique_input_key not in input_to_aligned_text_map_dict:
                #     line_text += entry.txt[char_idx]
                #     continue
                if unique_input_key in input_to_aligned_text_map_dict:
                    for alignment_idx in input_to_aligned_text_map_dict[
                        unique_input_key
                    ]:
                        if alignment_idx not in used_alinment_text_indices:
                            used_alinment_text_indices.append(alignment_idx)
                            line_text += chr(aligned_text[alignment_idx])
            self.__serialized_xml.at[idx, "aligned_txt"] = line_text

        return self.__serialized_xml
