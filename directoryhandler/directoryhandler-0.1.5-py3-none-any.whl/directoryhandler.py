import csv
import json
import os
import platform
import shutil
from collections import OrderedDict
from os.path import isdir, isfile, join
from jsondatahelper import clean_for_storage as standardize
from lxml import etree as ET

UNKNOWN_FILE_EXTENSION = "unknown"
DEF_DIR_FILTERS = [
    "__pycache__",
    "vscode",
    "py",
    "ds_store",
    ".DS_Store",
    ".git",
    ".idea",
]

MAC_SPLIT_CHAR = "/"
WINDOWS_SPLIT_CHAR = "\\"
PLATFORM_SPLIT_CHARS = {"windows": WINDOWS_SPLIT_CHAR, "mac": MAC_SPLIT_CHAR}
DEFAULT_PATH_SPLIT_CHAR = MAC_SPLIT_CHAR


def identify_path_split_type():
    try:
        return PLATFORM_SPLIT_CHARS[platform.system().lower()]
    except KeyError:
        return DEFAULT_PATH_SPLIT_CHAR


class DirectoryHandler:
    def __init__(
        self, file_exts=[], ext_filters=DEF_DIR_FILTERS, directory=os.getcwd()
    ):
        self.recognized_file_exts = file_exts
        self.extention_filters = ext_filters
        self.root_path = str(directory)
        self.path_split_char = identify_path_split_type()
        self.scan(directory)

    def scan(self, directory=os.getcwd()):
        """
        Refresh & Update governed directories and folders.
        """
        self.organized_files = OrderedDict()
        self.folder_list = []
        self.filter_cwd(directory)
        self.init_folder_objects()
        self.compile_file_list()
        return self

    def compile_file_list(self):
        self.file_list = []
        for file_set in self.organized_files.values():
            for file in file_set:
                self.file_list.append(file)

    def __repr__(self):
        s = ""
        for key, val in self.organized_files.items():
            if not key == UNKNOWN_FILE_EXTENSION:
                s = s + str(key).upper() + "\n"
                for item in val:
                    s = s + "-->" + str(item) + "\n"
        return s

    def passes_filter(self, path):
        """
        Utility function used to filter out un-wanted/un-needed folders.
        """

        for filter_name in self.extention_filters:
            filter_name = filter_name.upper()
            path = path.upper()
            if filter_name in path or (filter_name in path.split(self.path_split_char)):
                return False

        return True

    def filter_directory(self, current_directory):
        """
        Gathers all directories, and sub-directories.
        Filters out non-important directories.
        """
        self.master_dir_list = []
        self.levels = []

        for path in [directory[0] for directory in os.walk(current_directory)]:

            if self.passes_filter(path):
                level = path.count(self.path_split_char)
                if not level == 0:  # If the line is not empty
                    self.levels.append(level)
                    self.master_dir_list.append(path)

    def init_folder_objects(self):
        self.folder_list = []
        for dir_idx, path in enumerate(self.master_dir_list):
            self.folder_list.append(
                Directory(path, dir_idx, self.levels[dir_idx], self)
            )

    def add_file(self, file):
        """
        Adds file to master list.
        Called in file class when file is found.
        """

        if self.recognized_file_exts != []:

            if file.ext and file.ext in self.recognized_file_exts:

                self.verify_extension(file.ext)
                self.organized_files[file.ext].append(file)

            elif not file.ext in self.extention_filters:

                self.verify_extension(UNKNOWN_FILE_EXTENSION)
                self.organized_files[UNKNOWN_FILE_EXTENSION].append(file)

        elif self.passes_filter(file.path):

            self.verify_extension(file.ext)
            self.organized_files[file.ext].append(file)

    def verify_extension(self, extension):
        """
        Adds file extension to recognized extensions.
        """
        try:
            self.organized_files[extension]
        except KeyError:
            self.organized_files[extension] = []

    def get_files_by_ext(self, extension):
        """
        Returns all files of given file extension.
        """
        try:
            return self.organized_files[extension]
        except KeyError:
            print("That file extention does not exist!")
            return []

    def make_directory(self, path=None, name=None):
        created = False
        if path:
            if not self.exists(path):
                os.makedirs(path)
                created = True
        elif name:
            path = self.root_path + self.path_split_char + name
            if not self.exists(path):
                os.makedirs(path)
                created = True
        if created:
            self.scan()

    def make_file(self, file_name, insertion_path=None, data=None):

        if insertion_path:
            path = insertion_path
        else:
            path = self.root_path

        file_path = path + self.path_split_char + file_name

        if file_name.split(".")[1] == "json":
            with open(file_path, "w+", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            f = open(file_path, "w")
            f.write(str(data))
            f.close()

        self.scan()

        return self.find_files_by_name(file_name, return_first_found=True)

    def exists(self, path):
        if not isdir(path) and not isfile(path):
            return False
        return True

    def rmtree(self, directory):
        try:
            shutil.rmtree(directory)
        except FileNotFoundError as e:
            print(e)

    def delete_file(self, file_obj):
        if not isinstance(file_obj, str):
            # ext = file_obj.ext
            file_obj = file_obj.path

        try:
            os.remove(file_obj)
            self.scan()

        except FileNotFoundError as e:
            print(e)

    def find_files_by_name(self, file_name_to_find, return_first_found=False):
        found_files = []
        if file_name_to_find:
            split_file_name = file_name_to_find.split(".")
            if len(split_file_name) == 2:
                name = split_file_name[0]
                ext = split_file_name[1]
                for file in self.get_files_by_ext(ext):
                    if file.name == name:
                        if return_first_found:
                            return file
                        found_files.append(file)

            elif len(split_file_name) > 2:

                for file_list in self.organized_files.values():
                    for file in file_list:
                        if file.file_string == file_name_to_find and file:
                            if return_first_found:
                                return file.path
                            found_files.append(file)

            else:
                for file_list in self.organized_files.values():
                    for file in file_list:
                        if file.name == file_name_to_find:
                            if return_first_found:
                                return file
                            found_files.append(file)

        return found_files

    def find_file_by_path(self, path_to_find):
        for file_list in self.organized_files.values():
            for file in file_list:
                if file.path == path_to_find:
                    return file

    def find_file_in(self, folder_name, file_name):
        return self.find_folder_by_name(
            folder_name, return_first_found=True
        ).find_file_by_name(file_name)

    def find_folder_by_name(self, folder_name, return_first_found=True):
        found_folders = []

        for folder in self.folder_list:
            if folder.name.lower() == folder_name.lower():
                if return_first_found:
                    return folder
                else:
                    found_folders.append(folder)
        return found_folders

    def find_dir_via_path(self, folder_sub_path):
        for folder in self.folder_list:
            if folder_sub_path in folder.path:
                return folder

    def get_all_files_in(self, sub_path):
        self.scan()
        found_files = []
        for file_set in self.organized_files.values():  # All File Types
            for file in file_set:
                if sub_path in file.path:
                    found_files.append(file)
        return found_files

    def read_file(self, file_name, file_extention="json"):
        for file in self.organized_files[file_extention]:
            if file_name in file.name:
                return file.read()
        return None


class File:
    def __init__(self, file_string, path, handler_reference):
        self.file_string = file_string
        self.name, self.ext = self.check_for_file_extention(file_string)
        self.path = str(path) + +file_string
        self.handler_reference = handler_reference
        self.path_split_char = self.handler_reference.path_split_char
        self.handler_reference.add_file(self)
        self.associations = {}

    def check_for_file_extention(self, file_string):
        try:
            name, ext = file_string.split(".")
        except ValueError:
            name, ext = file_string.split("."), UNKNOWN_FILE_EXTENSION
        return name, ext

    def get_association_names(self):
        return self.associations.keys()

    def write(self, data):
        ext = self.ext.lower()
        if ext == "json":
            if data:
                with open(self.path, "w+", encoding="utf-8") as f:
                    json.dump(
                        standardize(data),
                        f,
                        ensure_ascii=True,
                        indent=4,
                    )
        else:
            print("Can't write to that file format!")

    def read(self):
        ext = self.ext.lower()
        if ext == "json":
            with open(self.path, "r+") as file_contents:
                try:
                    result = json.load(file_contents)
                    return convert_bytes(result)
                except json.decoder.JSONDecodeError:
                    print(
                        "There was a decoding error for file:",
                        self.path,
                        "please double check the syntax!",
                    )
                    return None

        elif ext == "csv":
            return CsvFile(file=self).to_dict()

        elif ext == "xml":
            return ET.parse(self.path).getroot()

        return None

    def update(self, new_data):
        if self.ext.lower() == "json":
            with open(self.path, "r+") as f:
                f.seek(0)  # rewind
                json.dump(
                    standardize(new_data),
                    f,
                    ensure_ascii=True,
                    indent=4,
                )
                f.truncate()

    def associate(self, association_name, association):
        self.associations[association_name] = association

    def to_json(self, output_dir):

        if self.associations:
            new_json_name = output_dir + self.path_split_char + self.name + ".json"
            association_collection = {}

            for association_name, dictionary in self.associations.items():
                association_collection[association_name] = dictionary

            with open(new_json_name, "w", encoding="utf-8") as f:
                json.dump(association_collection, f, ensure_ascii=False, indent=2)
        else:
            print("No associations have been made with that file yet!")

    def __repr__(self):
        return self.path


class CsvFile:
    def __init__(self, file):
        self.__build(file)
        self.get_rows()

    def __build(self, file):
        if isinstance(file, str):
            self.__build_by_path(file)
        else:
            self.__build_by_file_obj(file)

    def __build_by_path(self, file_path):
        self.file_string = file_path.split(self.path_split_char)[-1]
        self.name, self.ext = self.file_string.split(".")
        self.path = file_path
        # self.starting_row = starting_row

    def __build_by_file_obj(self, file):
        self.file_string = file.file_string
        self.name = file.name
        self.ext = file.ext
        self.path = file.path

        # self.starting_row = starting_row

    def get_rows(self):
        self.rows = []
        with open(self.path, "r", encoding="utf-8-sig") as f:
            for row in csv.reader(f):
                self.rows.append(row)

    def to_dict(self):

        self.as_dict = {}
        if len(self.rows) > 0:
            headers = self.rows[0]
            for i, header in enumerate(headers):
                if header:
                    self.as_dict[header] = []
                    for j, row in enumerate(self.rows):
                        if j > 0:
                            try:
                                self.as_dict[header].append(row[i])
                            except IndexError:
                                pass

        return self.as_dict


def convert_bytes(loaded_json):
    for key, val in loaded_json.items():
        if isinstance(val, dict):
            loaded_json[key] = convert_bytes(val)
        elif isinstance(val, list):
            for index, item in enumerate(val):
                if isinstance(item, dict):
                    loaded_json[key][index] = convert_bytes(item)
                elif isinstance(item, str) and item.startswith("b'"):
                    loaded_json[key][index] = bytes.fromhex(item.split("b'")[1])
        elif isinstance(val, str) and val.startswith("b'"):
            loaded_json[key] = bytes.fromhex(val.split("b'")[1])

    return loaded_json


class Directory:
    def __init__(self, path, index, level, handler_reference):
        self.children = []
        self.path = path
        self.index = index
        self.level = level
        self.handler_reference = handler_reference
        self.path_split_char = self.handler_reference.path_split_char
        self.name = path.split(self.path_split_char)[-1]
        self.files = self.gather_files()
        self.parent = self.get_parent_folder_name()
        self.gather_children_folders()
        self.dict_rep = {
            "Name": self.name,
            "Files": self.files,
            "Parent": self.parent,
            "Children": self.children,
        }

    def gather_files(self):
        self.files = [
            File(f, self.path, self.handler_reference)
            for f in os.listdir(self.path)
            if isfile(join(self.path, f))
        ]
        return self.files

    def gather_children_folders(self):
        self.children = [f for f in os.listdir(self.path) if isdir(join(self.path, f))]
        # self.children_folder_objs = [
        #     self.handler_reference.find_folder_by_name(obj) for obj in self.children
        # ]

    def get_parent_folder_name(self):
        return self.path.replace(self.path_split_char + self.name, "").split(
            self.path_split_char
        )[-1]

    def find_folder_by_name(self, folder_name):
        for folder in self.children:
            if folder_name in folder:
                return folder
        return None

    def find_file_by_name(self, file_name):
        for file in self.files:
            if file.name == file_name:
                return file
        print("File of name:", file_name, "not found in folder:", self.name)
        return None

    def find_files_by_ext(self, extention):
        found_files = []
        for file in self.files:
            if file.ext == extention:
                found_files.append(file)
        return found_files

    def __repr__(self):
        s = ""
        for key, val in self.dict_rep.items():
            s = s + key + "\n"
            if isinstance(val, list):
                for item in val:
                    s = s + str(item) + "\n"
            else:
                s = s + val + "\n"
        return s
