class CoreData:
    RELS_FOLDER_NAME = '_rels'

class ContentTypeOverride:
    EXTENDED_PROPERTIES = 'application/vnd.openxmlformats-officedocument.extended-properties+xml'
    CORE_PROPERTIES = 'application/vnd.openxmlformats-package.core-properties+xml'
    CUSTOM_PROPERTIES = 'application/vnd.openxmlformats-officedocument.custom-properties+xml'
    SHAREDSTRINGS = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml'
    STYLES = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml',
    ]
    THEME = [
        'application/vnd.openxmlformats-officedocument.theme+xml',
    ]
    MAIN = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml'
    WORKSHEET = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml',
    ]
