# -*- coding: utf-8 -*-

import re
from typing import Optional, List, Any


class TagsProcessor:
    """
    Helper class to extract and process search tags from objects.
    The search tags can be kept individually or embedded as hash tags inside text
    like "This text has #hash_tag that can be used for search."
    """
    __NORMALIZE_REGEX = re.compile(r'([_#])+')
    __COMPRESS_REGEX = re.compile(r'([ _#])+')
    __SPLIT_REGEX = re.compile(r'([,;])+')
    __HASHTAG_REGEX = re.compile(r'#\w+')

    @staticmethod
    def normalize_tag(tag: str) -> Optional[str]:
        """
        Normalizes a tag by replacing special symbols like '_' and '#' with spaces.
        When tags are normalized then can be presented to user in similar shape and form.

        :param tag: the tag to normalize.
        :return: a normalized tag.
        """
        res = re.sub(TagsProcessor.__NORMALIZE_REGEX, ' ', tag).strip()
        if res:
            return res
        else:
            return None

    @staticmethod
    def compress_tag(tag: str) -> str:
        """
        Compress a tag by removing special symbols like spaces, '_' and '#'
        and converting the tag to lower case.
        When tags are compressed they can be matched in search queries.

        :param tag: the tag to compress.
        :return: a compressed tag.
        """
        res = re.sub(TagsProcessor.__COMPRESS_REGEX, '', tag).lower()
        if res:
            return res
        else:
            return None

    @staticmethod
    def equal_tags(tag1: str, tag2: str) -> bool:
        """
        Compares two tags using their compressed form.

        :param tag1: the first tag.
        :param tag2: the second tag.
        :return: true if the tags are equal and false otherwise.
        """
        if tag1 is None and tag2 is None:
            return True
        if tag1 is None or tag2 is None:
            return False
        return TagsProcessor.compress_tag(tag1) == TagsProcessor.compress_tag(tag2)

    @staticmethod
    def normalize_tags(tags: List[str]) -> List[str]:
        """
        Normalizes a list of tags.

        :param tags: the tags to normalize.
        :return: a list with normalized tags.
        """
        return list(map(TagsProcessor.normalize_tag, tags))

    @staticmethod
    def normalize_tag_list(tag_list: str) -> List[str]:
        """
        Normalizes a comma-separated list of tags.

        :param tag_list: a comma-separated list of tags to normalize.
        :return: a list with normalized tags.
        """
        tags = re.split(TagsProcessor.__SPLIT_REGEX, tag_list)
        # Remove separators
        for index in range(len(tags)):
            tags = tags[:index + 1] + tags[index + 2:]

        return TagsProcessor.normalize_tags(tags)

    @staticmethod
    def compress_tags(tags: List[str]) -> List[str]:
        """
        Compresses a comma-separated list of tags.

        :param tags: a comma-separated list of tags to compress.
        :return: a list with compressed tags.
        """
        return list(map(TagsProcessor.compress_tag, tags))

    @staticmethod
    def compress_tag_list(tag_list: str) -> List[str]:
        """
        Compresses a comma-separated list of tags.

        :param tag_list: a comma-separated list of tags to compress.
        :return: a list with compressed tags.
        """
        tags = re.split(TagsProcessor.__SPLIT_REGEX, tag_list)
        # Remove separators
        for index in range(len(tags)):
            tags = tags[:index + 1] + tags[index + 2:]
        return TagsProcessor.compress_tags(tags)

    @staticmethod
    def extract_hash_tags(text: str) -> List[str]:
        """
        Extracts hash tags from a text.

        :param text: a text that contains hash tags
        :return: a list with extracted and compressed tags.
        """
        tags = []

        if text != '':
            hash_tags = re.findall(TagsProcessor.__HASHTAG_REGEX, text)
            tags = TagsProcessor.compress_tags(hash_tags)

        # del duplicates
        unique_tags = []
        for i in tags:
            if i not in unique_tags:
                unique_tags.append(i)

        return unique_tags

    @staticmethod
    def __extract_string(field: Any) -> str:
        if field is None:
            return ''
        if type(field) == str:
            return field
        if hasattr(field, '__dict__'):
            return ''

        result = ''

        for prop in field:
            result += ' ' + TagsProcessor.__extract_string(field[prop])

        return result

    @staticmethod
    def extract_hash_tags_from_value(obj: Any, *search_fields: str) -> List[str]:
        """
        Extracts hash tags from selected fields in an object.

        :param obj: an object which contains hash tags.
        :param search_fields: a list of fields in the objects where to extract tags
        :return: a list of extracted and compressed tags.
        """
        # create obj (only for python)
        obj = type('obj', (), obj)

        tags = TagsProcessor.compress_tags(obj.tags)

        for field in search_fields:
            text = TagsProcessor.__extract_string(eval('obj.' + field))
            if text != '':
                hash_tags = re.findall(TagsProcessor.__HASHTAG_REGEX, text)
                tags = tags + TagsProcessor.compress_tags(hash_tags)

        # del duplicates
        unique_tags = []
        for i in tags:
            if i not in unique_tags:
                unique_tags.append(i)

        return unique_tags
