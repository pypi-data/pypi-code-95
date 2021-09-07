import xml.etree.ElementTree as ET
import os
import glob
from firstimpression import file

from firstimpression.constants import APIS, TEMP_FOLDER, LOCAL_INTEGRATED_FOLDER, ENGLISH_INDEX, DUTCH_INDEX
from firstimpression.file import update_directories_api, check_too_old, write_root_to_xml_files, download_install_media, list_files_dir, xml_to_root
from firstimpression.time import change_language, parse_string_to_string
from firstimpression.text import remove_emoji
from firstimpression.scala import variables, Log
from firstimpression.api.request import request_json

##################################################################################################
# LOGGING
##################################################################################################

script = 'Instagram'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['insta']

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

LOCAL_PATH = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME)

URL = 'https://fi-api.io/instagram_post/'
BASE_URL_IMAGES = 'https://socials-bucket.s3.eu-central-1.amazonaws.com'

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################

def run_api(api_key, max_minutes, max_characters, max_items, language, tags):

    debug.log('folder name: {}'.format(NAME))
        
    max_file_age = 60 * max_minutes

    debug.log('max_file_age: {}'.format(max_file_age))

    if language == 'NL':
        debug.log('change language to dutch')
        change_language(DUTCH_INDEX)
        datetime_format_new = '%d %B %Y'
        language_index = DUTCH_INDEX
    else:
        debug.log('change language to english')
        change_language(ENGLISH_INDEX)
        datetime_format_new = '%B %d %Y'
        language_index = ENGLISH_INDEX

    headers = {
        'Authorization': 'Token {}'.format(api_key)
    }

    tags = tags.split(';')

    update_directories_api(NAME)

    params = {
        'number_of_posts': max_items
    }

    for tag in tags:
        root = ET.Element("root")
        if not (tag is None or tag == ''):
            params['tag'] = tag
            xml_temp_path = os.path.join(TEMP_FOLDER, NAME, 'instagram_{}.xml'.format(tag))
        else:
            params.pop('tag', None)
            xml_temp_path = os.path.join(TEMP_FOLDER, NAME, 'instagram.xml')
        
        debug.log('file path temp: {} - local: {}'.format(xml_temp_path, LOCAL_PATH))
        
        if check_too_old(xml_temp_path, max_file_age):

            response_json, is_error = request_json(URL, headers, params, False)

            if is_error:
                if response_json['type'] == 'ERROR':
                    error.log('request {} -> {}'.format(response_json['reason'], response_json['message']))
                elif response_json['type'] == 'WARN':
                    warn.log('request {} -> {}'.format(response_json['reason'], response_json['message']))
                break

            for post in response_json:
                root.append(parse_post(post, max_characters, language_index, datetime_format_new))
    
            write_root_to_xml_files(root, xml_temp_path, NAME)
        else:
            debug.log('File not old enough')      
    
def check_api(max_minutes, tag, min_items):
    svars = variables()

    max_file_age = 60 * max_minutes + 2

    debug.log('max_file_age: {}'.format(max_file_age))

    if tag is '' or tag is None:
        file_name = 'instagram[*.xml'
    else:
        file_name = 'instagram_{}*.xml'.format(tag)

    file_path = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, file_name)

    debug.log('local path: {}'.format(file_path))

    file_path = sorted(glob.glob(file_path))

    if len(file_path) > 0:
        file_path = file_path[-1]
        debug.log('glob filepath: {}'.format(file_path))

        if check_too_old(file_path, max_file_age):
            svars['skipscript'] = True
            info.log('file too old')
        else:
            svars['skipscript'] = False
            amount_items = len(xml_to_root(file_path))

            if amount_items < min_items:
                svars['skipscript'] = True
                info.log('{} has to less post to show'.format(tag))
    else:
        warn.log('File does not exists')
        svars['skipscript'] = True


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_media(post):
    return post.get('media', None)


def get_message(post):
    return post.get('message', '')


def get_creation_date(post):
    return post.get('created_at', '')[:19]

def get_likes(post):
    return post.get('likes', 0)


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################

def crop_message(text, max_length, language):
    if language == 1:
        append_text = "Lees verder op Instagram"
    else:
        append_text = "Read more on Instagram"

    if len(text) > max_length:
        return text[:max_length-3] + "...\n{}".format(append_text)
    else:
        return text


def parse_post(post, max_characters, language_index, datetime_format_new):
    item = ET.Element("item")
    ET.SubElement(item, "likes").text = str(get_likes(post))
    ET.SubElement(item, "message").text = crop_message(remove_emoji(get_message(post)), max_characters, language_index)
    ET.SubElement(item, "created_time").text = parse_string_to_string(get_creation_date(post), DATETIME_FORMAT, datetime_format_new)

    thumbnail_url = get_media(post)
    if thumbnail_url is None:
        debug.log('image not found so using placeholder')
        media_link = 'Content:\\placeholders\\img.png'
    else:
        media_link = download_install_media(thumbnail_url, TEMP_FOLDER, NAME)
    
    ET.SubElement(item, "media").text = media_link

    if media_link.endswith("mp4"):
        ET.SubElement(item, "media_type").text = "video"
    else:
        ET.SubElement(item, "media_type").text = "image"
    
    return item

