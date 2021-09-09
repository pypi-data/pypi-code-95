import re
import uuid

import lxml.etree as ET

from . import parse
from .consts import CCML_DICTIONARY, CHANNEL_STORAGE_FOLDER, ChannelType


# Consts.
XML_TAG_REG = r"<((\/|)+[a-z]+)({gensym})+([a-z]+)"
VOICE_FILE_BASE_URL = "https://cocohub-audio-files.s3.us-east-2.amazonaws.com"


def __convert_from_ccml(text: str, channel_type: ChannelType):
    """
    Handle tag replacement in target text.

    Arguments:
        text: (string) Target text.
        tags_dictionary: (dict) Tags dictionary, key to replace with value.

    Returns:
        CCML text (string).
    """
    result_text = text

    gensym_str = uuid.uuid4().hex[:5]

    channel_tags_mapping = CCML_DICTIONARY[channel_type.value]

    channel_tags = list(channel_tags_mapping.keys())
    common_ccml_tags = list(CCML_DICTIONARY["common"].keys())

    clean_text = parse.remove_invalid_tags(
        text=text, valid_tags=[*channel_tags, *common_ccml_tags]
    )

    # Handle audio tags
    et = ET.fromstring(f"<body>{clean_text}</body>")
    audio_tags = et.xpath(f"//audio")

    for tag in audio_tags:
        hub_id = tag.attrib.get("hub_id") or None
        if hub_id:
            folder_name, file_name = hub_id.split(":")
            tag.attrib[
                "src"
            ] = f"{VOICE_FILE_BASE_URL}/{folder_name}/{CHANNEL_STORAGE_FOLDER[channel_type.value]}/{file_name}"
            del tag.attrib["hub_id"]

    result_text = ET.tounicode(et)[6:-7]

    # Handle special tags
    for ccml_tag, tag_name in channel_tags_mapping.items():
        if tag_name:
            if ":" in tag_name:
                tag_name = tag_name.replace(":", gensym_str)
            result_text = parse.rename_tag(
                text=result_text, tag_name=ccml_tag, new_tag_name=tag_name
            )

    res = re.sub(XML_TAG_REG.format(gensym=gensym_str), "<\g<1>:\g<4>", result_text)

    return res


def ccml_to_aws_polly(text_input):
    """
    Convert CCML tags to AWS Polly SSML tags and remove wrong tags.

    Arguments:
        text_input: (string) CCML input to convert to AWS Polly SSML.

    Returns:
        AWS Polly SSML text (string).
    """

    return __convert_from_ccml(text=text_input, channel_type=ChannelType.AWS_POLLY)


def ccml_to_amazon(text_input):
    """
    Convert CCML tags to Amazon SSML tags and remove wrong tags.

    Arguments:
        text_input: (string) CCML input to convert to Amazon SSML.

    Returns:
        Amazon SSML text (string).
    """
    return __convert_from_ccml(text=text_input, channel_type=ChannelType.AMAZON)


def ccml_to_google(text_input):
    """
    Convert CCML tags to Google SSML tags and remove wrong tags.

    Arguments:
        text_input: (string) CCML input to convert to Google SSML.

    Returns:
        Google SSML text (string).
    """
    return __convert_from_ccml(text=text_input, channel_type=ChannelType.GOOGLE)


def ccml_to_twiml(text_input):
    """
    Convert CCML tags to Twilio SSML(TwiML) tags and remove wrong tags.

    Arguments:
        text_input: (string) CCML input to convert to Twilio SSML(TwiML).

    Returns:
        TwiML text (string).
    """
    return __convert_from_ccml(text=text_input, channel_type=ChannelType.TWILIO)


def ccml_to_amazon_neural(text_input):
    """
    Convert CCML tags to Twilio SSML(TwiML) tags and remove wrong tags.

    Arguments:
        text_input: (string) CCML input to convert to Twilio SSML(TwiML).

    Returns:
        TwiML text (string).
    """
    return __convert_from_ccml(text=text_input, channel_type=ChannelType.AMAZON_NEURAL)
