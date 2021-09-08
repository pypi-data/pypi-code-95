from os import path, fsencode, fsdecode, listdir

from unswamp.objects.core import CheckSuite, CheckRun


class DocumentationService():
    _module_root = path.dirname(path.dirname(__file__))
    _data_extension = "json"
    _doc_extension = "html"
    _data_replace_pattern = "//-->DATA-REPLACE<--"
    _prefixes = {
        CheckSuite: "unswamp_suite",
        CheckRun: "unswamp_run"
    }
    ##################################################################################################
    # Constructor
    ##################################################################################################

    def __init__(self, documentation_folder):
        self.documentation_folder = documentation_folder

    ##################################################################################################
    # Methods
    ##################################################################################################
    def store_object(self, obj):
        obj_type = type(obj)
        prefix = self._prefixes[obj_type]
        # TODO: either check if obj has id or then make base type for it
        obj_id = obj.id
        # TODO: bring object version into play as well?
        file_name = f"{prefix}_{obj_id}.{self._data_extension}"
        if obj_type is CheckRun:
            file_name = f"{prefix}_{obj.suite_id}_{obj_id}.{self._data_extension}"
        file_path = path.join(self.documentation_folder, file_name)
        # TODO: check if obj implements method
        json = obj.to_json()
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(json)

    def build_html_documentation(self):
        doc_index = self.build_document_index()
        self.render_html(doc_index)

    def build_document_index(self):
        doc_index = {}
        doc_dir = fsencode(self.documentation_folder)
        for file in listdir(doc_dir):
            file_name = fsdecode(file)
            file_path = path.join(self.documentation_folder, file_name)
            obj_type = self.determine_file_type(file_name)
            if obj_type is not None:
                if obj_type not in doc_index:
                    doc_index[obj_type] = []
                doc_index[obj_type].append(file_path)
        return doc_index

    def determine_file_type(self, file_name):
        if file_name.endswith(f".{self._data_extension}"):
            for key in self._prefixes:
                prefix = self._prefixes[key]
                if file_name.startswith(prefix):
                    return key
        return None

    def render_html(self, doc_index):
        for key in doc_index:
            template_path = path.join(self._module_root, "templates", f"{key.__name__}.{self._doc_extension}")
            with open(template_path, "r", encoding="utf-8") as fh_template:
                template = fh_template.read()
                for data_file in doc_index[key]:
                    with open(data_file, "r", encoding="utf-8") as fh_data:
                        data = fh_data.read()
                        doc_content = template.replace(self._data_replace_pattern, f"var data = {data};")
                        doc_file_path = data_file.replace(self._data_extension, self._doc_extension)
                        with open(doc_file_path, "w", encoding="utf-8") as fh_doc:
                            fh_doc.write(doc_content)



    ##################################################################################################
    # Properties
    ##################################################################################################
    @property
    def documentation_folder(self):
        return self._documentation_folder

    @documentation_folder.setter
    def documentation_folder(self, value):
        self._documentation_folder = value
