import sys
from ..alignment_algorithms.alignment_algorithm import (
    AlignmentKey,
)
from ..alignment_algorithms.local_alignment import local_alignment
from typing import Union
from ..alignment_algorithms import AlignmentException, TextAlignments
from .aligner import AlignmentOperation, QueryTargetAlignment
from ..alignment_algorithms import AlignmentAlgorithm
from ..shared_classes import TextChunk, LetterList
from ..text_loaders import TextLoader
from ..text_transformers import TextTransformer


def debugger_is_active() -> bool:
    """Return if the debugger is currently active"""
    gettrace = getattr(sys, "gettrace", lambda: None)
    return gettrace() is not None


class TextAlignmentTool:
    """
    The text alignment tool provides a context within which
    a custom and extensible pipeline of operations can be
    carried out. It tracks each operation in the pipeline
    process and facilitates user defined text alignment
    operations.
    """

    def __init__(self, query_loader: TextLoader, target_loader: TextLoader):
        if debugger_is_active():
            # In debugging mode, inject some root level utilities
            # to make it easire to visualize the text and chunks
            main_mod = sys.modules["__main__"]
            main_mod.__builtins__["dbg"] = DebugHelper()
            pass

        self.__query_loader: TextLoader = query_loader
        self.__target_loader: TextLoader = target_loader
        self.__operation_list: list[AlignmentOperation] = []
        self.__load_texts()

    def __load_texts(self):
        no_operation_query_transform = TextTransformer()
        no_operation_query_transform.load_input(
            self.__query_loader.output,
            self.__query_loader.text_chunk_indices,
            no_transform=True,
        )
        self.__operation_list.append(
            AlignmentOperation(no_operation_query_transform, None, None)
        )

        no_operation_target_transform = TextTransformer()
        no_operation_target_transform.load_input(
            self.__target_loader.output,
            self.__target_loader.text_chunk_indices,
            no_transform=True,
        )
        self.__operation_list.append(
            AlignmentOperation(None, no_operation_target_transform, None)
        )

    def query_text_transforms(self, query_transformers: list[TextTransformer]):
        """
        Apply any number of transformations to the query text
        in the order submitted.
        """

        for transformer in query_transformers:
            latest_query_transformer = self.__latest_query_transform
            transformer.load_input(
                latest_query_transformer.output,
                latest_query_transformer.text_chunk_indices,
            )
            self.__operation_list.append(AlignmentOperation(transformer, None, None))

    def query_text_transform(self, query_transformers: TextTransformer):
        """
        Apply one transformations to the query text.
        """

        self.query_text_transforms([query_transformers])

    def target_text_transforms(self, target_transformers: list[TextTransformer]):
        """
        Apply any number of transformations to the target text
        in the order submitted.
        """

        for transformer in target_transformers:
            latest_target_transformer = self.__latest_target_transform
            transformer.load_input(
                latest_target_transformer.output,
                latest_target_transformer.text_chunk_indices,
            )
            self.__operation_list.append(AlignmentOperation(None, transformer, None))

    def target_text_transform(self, target_transformer: TextTransformer):
        """
        Apply one transformations to the target text.
        """

        self.target_text_transforms([target_transformer])

    def align_texts(self, alignment_algorithms: list[AlignmentAlgorithm]):
        """
        Apply any number of alignment operations to the query and target
        texts in the order specified.
        """

        for alignment_algorithm in alignment_algorithms:
            latest_query_text = self.__latest_query_text
            latest_query_text_chunk_indices = self.__latest_query_text_chunk_indices
            latest_target_text = self.__latest_target_text
            latest_target_text_chunk_indices = self.__latest_target_text_chunk_indices
            alignment_algorithm.load_texts(
                latest_query_text,
                latest_target_text,
                latest_query_text_chunk_indices,
                latest_target_text_chunk_indices,
            )
            alignment_algorithm.align()
            self.__operation_list.append(
                AlignmentOperation(None, None, alignment_algorithm)
            )

    def align_text(self, alignment_algorithm: AlignmentAlgorithm):
        """
        Apply a single alignment operation to the query and target
        texts.
        """

        self.align_texts([alignment_algorithm])

    def collect_all_alignments(self) -> list[list[QueryTargetAlignment]]:
        """Based on the latest alignment, calculate all possible correspondances
        between every stage of the query and the target transformation
        pipeline.

        Returns:
            list[list[QueryTargetAlignment]]: this 2D list contains every possible
            alignment of the query and target. The 1st axis tracks the query text
            from latest to earliest. The 2nd axis tracks the target text from
            latest to earliest.
        """
        results: list[list[QueryTargetAlignment]] = []

        # Collect all possible query and target transforms
        query_transforms: list[AlignmentOperation] = [
            x
            for x in self.__operation_list
            if x.query_transformation is not None  # or x.alignment is not None
        ]
        target_transforms: list[AlignmentOperation] = [
            x
            for x in self.__operation_list
            if x.target_transformation is not None  # or x.alignment is not None
        ]

        latest_alignment: TextAlignments = self.latest_alignment._alignment
        for query_alignment_operation in reversed(query_transforms):
            # if alignment_operation.alignment is not None:
            #     latest_alignment = alignment_operation.alignment._alignment
            if (
                latest_alignment is not None
                and query_alignment_operation.query_transformation is not None
            ):
                stored_alignment: Union[TextAlignments, None] = None
                current_query_target_alignment: list[QueryTargetAlignment] = []
                current_query_text = (
                    query_alignment_operation.query_transformation.input
                )
                current_query_text_chunks = (
                    query_alignment_operation.query_transformation.input_text_chunk_indices
                )
                aligned_query_to_current_query: dict[int, list[int]] = {}
                for (
                    input_output_map_entry
                ) in query_alignment_operation.query_transformation.input_output_map:
                    if input_output_map_entry[1] not in aligned_query_to_current_query:
                        aligned_query_to_current_query[input_output_map_entry[1]] = []
                    aligned_query_to_current_query[input_output_map_entry[1]].append(
                        input_output_map_entry[0]
                    )

                # latest_alignment: Union[TextAlignments, None] = None
                for target_alignment_operation in reversed(target_transforms):
                    # if alignment_operation.alignment is not None:
                    #     latest_alignment = alignment_operation.alignment._alignment
                    if (
                        latest_alignment is not None
                        and target_alignment_operation.target_transformation is not None
                    ):
                        # latest_alignment = (
                        #     alignment_operation.target_transformation.apply_alignment(
                        #         latest_alignment
                        #     )
                        # )
                        current_target_text = (
                            target_alignment_operation.target_transformation.input
                        )
                        current_target_text_chunks = (
                            target_alignment_operation.target_transformation.input_text_chunk_indices
                        )
                        aligned_target_to_current_target: dict[int, list[int]] = {}
                        for (
                            input_output_map_entry
                        ) in (
                            target_alignment_operation.target_transformation.input_output_map
                        ):
                            if (
                                input_output_map_entry[1]
                                not in aligned_target_to_current_target
                            ):
                                aligned_target_to_current_target[
                                    input_output_map_entry[1]
                                ] = []
                            aligned_target_to_current_target[
                                input_output_map_entry[1]
                            ].append(input_output_map_entry[0])

                        new_alignment = TextAlignments()
                        for alignment in latest_alignment.alignments:
                            for query_idx in aligned_query_to_current_query.get(
                                alignment.query_idx, []
                            ):
                                for target_idx in aligned_target_to_current_target.get(
                                    alignment.target_idx, []
                                ):
                                    new_alignment.alignments.append(
                                        AlignmentKey(query_idx, target_idx)
                                    )
                        current_query_target_alignment.append(
                            QueryTargetAlignment(
                                new_alignment,
                                current_query_text,
                                current_target_text,
                                current_query_text_chunks,
                                current_target_text_chunks,
                                query_alignment_operation.query_transformation.__class__.__name__,
                                target_alignment_operation.target_transformation.__class__.__name__,
                            )
                        )

                        latest_alignment = new_alignment
                        if stored_alignment is None:
                            stored_alignment = latest_alignment

                if stored_alignment is not None:
                    latest_alignment = stored_alignment
                results.append(current_query_target_alignment)

        return results

    # def find_alignment_to_query(self) -> list[QueryTargetAlignment]:
    #     """
    #     Walk the latest alignment mapping back to the earliest
    #     form of the target text.
    #     """

    #     query_transforms: list[AlignmentOperation] = [
    #         x
    #         for x in self.__operation_list
    #         if x.query_transformation is not None or x.alignment is not None
    #     ]
    #     latest_target_text = self.__latest_target_text
    #     latest_alignment: Union[TextAlignments, None] = None
    #     alignment_history: list[QueryTargetAlignment] = []
    #     for alignment_operation in reversed(query_transforms):
    #         if alignment_operation.alignment is not None:
    #             latest_alignment = alignment_operation.alignment._alignment
    #         if (
    #             latest_alignment is not None
    #             and alignment_operation.query_transformation is not None
    #         ):
    #             latest_alignment = (
    #                 alignment_operation.query_transformation.apply_alignment(
    #                     latest_alignment
    #                 )
    #             )
    #             alignment_history.append(
    #                 QueryTargetAlignment(
    #                     latest_alignment,
    #                     alignment_operation.query_transformation.input,
    #                     alignment_operation.query_transformation.input_text_chunk_indices,
    #                     latest_target_text,
    #                 )
    #             )

    #     return alignment_history

    # def find_alignment_to_target(self) -> list[QueryTargetAlignment]:
    #     """
    #     Walk the latest alignment mapping back to the earliest
    #     form of the query text.
    #     """

    #     target_transforms: list[AlignmentOperation] = [
    #         x
    #         for x in self.__operation_list
    #         if x.target_transformation is not None or x.alignment is not None
    #     ]
    #     latest_query_text = self.__latest_query_text
    #     latest_alignment: Union[TextAlignments, None] = None
    #     alignment_history: list[QueryTargetAlignment] = []
    #     for alignment_operation in reversed(target_transforms):
    #         if alignment_operation.alignment is not None:
    #             latest_alignment = alignment_operation.alignment._alignment
    #         if (
    #             latest_alignment is not None
    #             and alignment_operation.target_transformation is not None
    #         ):
    #             latest_alignment = (
    #                 alignment_operation.target_transformation.apply_alignment(
    #                     latest_alignment
    #                 )
    #             )
    #             alignment_history.append(
    #                 QueryTargetAlignment(
    #                     latest_alignment,
    #                     alignment_operation.target_transformation.input,
    #                     alignment_operation.target_transformation.input_text_chunk_indices,
    #                     latest_query_text,
    #                 )
    #             )

    #     return alignment_history

    @property
    def latest_alignment(self) -> AlignmentAlgorithm:
        alignments = [
            x.alignment for x in self.__operation_list if x.alignment is not None
        ]

        if alignments:
            return alignments[-1]

        raise AlignmentException("No alignment found")

    @property
    def __latest_operation(self) -> AlignmentOperation:
        return self.__operation_list[-1]

    @property
    def __latest_query_operation_text_chunks(self) -> list[TextChunk]:
        transformer = [
            x for x in self.__operation_list if x.query_transformation is not None
        ][-1].query_transformation
        return transformer.text_chunk_indices if transformer is not None else []

    @property
    def __latest_target_operation_text_chunks(self) -> list[TextChunk]:
        transformer = [
            x for x in self.__operation_list if x.target_transformation is not None
        ][-1].target_transformation
        return transformer.text_chunk_indices if transformer is not None else []

    @property
    def __latest_query_text(self) -> LetterList:
        return self.__latest_query_transform.output

    @property
    def __latest_query_text_chunk_indices(self) -> list[TextChunk]:
        return (
            self.__latest_operation.alignment.output_query_text_chunk_indices
            if self.__latest_operation.alignment is not None
            else self.__latest_query_operation_text_chunks
        )

    @property
    def __latest_query_transform(self) -> TextTransformer:
        return self.__query_text_operations[-1]

    @property
    def __query_text_operations(self) -> list[TextTransformer]:
        return [
            x.query_transformation
            for x in self.__operation_list
            if x.query_transformation is not None
        ]

    @property
    def __latest_target_text(self) -> LetterList:
        return self.__latest_target_transform.output

    @property
    def __latest_target_text_chunk_indices(self) -> list[TextChunk]:
        return (
            self.__latest_operation.alignment.output_target_text_chunk_indices
            if self.__latest_operation.alignment is not None
            else self.__latest_target_operation_text_chunks
        )

    @property
    def __latest_target_transform(self) -> TextTransformer:
        return self.__target_text_operations[-1]

    @property
    def __target_text_operations(self) -> list[TextTransformer]:
        return [
            x.target_transformation
            for x in self.__operation_list
            if x.target_transformation is not None
        ]

    def check(self):
        pass


class DebugHelper:
    """
    The Debug helper provides several convenience methods for inspecting
    the text inside the alignment tool.
    """

    def __init__(self):
        pass

    @staticmethod
    def display_text_region(text: LetterList, start_idx: int, end_idx: int) -> str:
        """
        Print out a human readable representation of the letter list
        for the section between the start_idx and end_idx.
        """

        text_chunk = "".join([chr(x) for x in text[start_idx:end_idx]])
        print(text_chunk)
        return text_chunk

    @classmethod
    def display_text_chunk(cls, text: LetterList, chunk: TextChunk) -> str:
        """
        Print out a human readable representation of the letter list
        for the specified text chunk.
        """

        return cls.display_text_region(text, chunk.start_idx, chunk.end_idx + 1)

    @classmethod
    def display_text_chunks(
        cls, text: LetterList, chunks: list[TextChunk]
    ) -> list[str]:
        """
        Print out a human readable representation of the letter list
        for the specified text chunks.
        """

        return [cls.display_text_chunk(text, x) for x in chunks]

    @classmethod
    def display_text(cls, text: LetterList) -> str:
        """
        Print out a human readable representation of the entire
        letter list.
        """

        return cls.display_text_region(text, 0, len(text) - 1)
