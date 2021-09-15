import logging
import os
import pathlib
import shutil
from typing import List, Optional
from urllib.parse import urlparse
from urllib.request import urlopen

import regex as re
import stanza
from bs4 import BeautifulSoup
from langdetect import detect
from pelecanus import PelicanJson

from texta_mlp.document import Document
from texta_mlp.entity_mapper import EntityMapper
from texta_mlp.utils import parse_bool_env
from texta_mlp.exceptions import LanguageNotSupported


# Languages supported by default.
DEFAULT_LANG_CODES = ("et", "ru", "en", "ar")

# URLs for default Entity Mapper data sources.
ENTITY_MAPPER_DATA_URLS = (
    "https://packages.texta.ee/texta-resources/entity_mapper/addresses.json",
    "https://packages.texta.ee/texta-resources/entity_mapper/companies.json",
    "https://packages.texta.ee/texta-resources/entity_mapper/currencies.json"
)

# URLs for Concatenator data sources.
CONCATENATOR_DATA_FILES = (
    "https://packages.texta.ee/texta-resources/concatenator/months.txt",
    "https://packages.texta.ee/texta-resources/concatenator/not_entities.txt",
    "https://packages.texta.ee/texta-resources/concatenator/space_between_not_ok.txt",
)

# Location of the resource dir where models are downloaded
DEFAULT_RESOURCE_DIR = os.getenv("TEXTA_MLP_DATA_DIR", os.path.join(os.getcwd(), "data"))

# Data refresh means deleting all existing models and downloading new ones
REFRESH_DATA = parse_bool_env("TEXTA_MLP_REFRESH_DATA", False)

# List of all analyzers supported by MLP
SUPPORTED_ANALYZERS = (
    "lemmas",
    "pos_tags",
    "transliteration",
    "ner",
    "addresses",
    "emails",
    "phone_strict",
    "entities",
    "namemail",
    "bounded",
    "currency_sum",
    "sentences"
)

# Here we define languages with NER support to avoid Stanza trying to load them for languages without NER support.
# This significantly increases performance for languages without NER.
# https://stanfordnlp.github.io/stanza/available_models.html#available-ner-models
STANZA_NER_SUPPORT = ("ar", "zh", "nl", "en", "fr", "de", "ru", "es", "uk")


class MLP:

    def __init__(
            self,
            language_codes=DEFAULT_LANG_CODES,
            default_language_code=DEFAULT_LANG_CODES[0],
            use_default_language_code=True,
            resource_dir: str = DEFAULT_RESOURCE_DIR,
            logging_level="error",
            use_gpu=True,
            refresh_data=REFRESH_DATA
    ):
        self.supported_langs = language_codes
        self.logger = logging.getLogger()
        self.default_lang = default_language_code
        self.use_default_lang = use_default_language_code
        self.resource_dir = resource_dir

        self._stanza_pipelines = {}
        self.logging_level = logging_level
        self.use_gpu = use_gpu
        self.stanza_resource_path = pathlib.Path(self.resource_dir) / "stanza"

        self.resource_dir_pathlib = pathlib.Path(resource_dir)
        self.not_entities_path = self.resource_dir_pathlib / "concatenator" / "not_entities.txt"
        self.space_between_not_ok_path = self.resource_dir_pathlib / "concatenator" / "space_between_not_ok.txt"
        self.months_path = self.resource_dir_pathlib / "concatenator" / "months.txt"

        self.prepare_resources(refresh_data)

        self._entity_mapper = None
        self.loaded_entity_files = []

        self.not_entities = self._load_not_entities()
        self.space_between_not_ok = self._load_space_between_not_ok()
        self.months = self._load_months()
        self.concat_resources = {
            "months": self.months,
            "space_between_not_ok": self.space_between_not_ok,
            "not_entities": self.not_entities
        }


    def prepare_resources(self, refresh_data):
        """
        Prepares all resources for MLP.
        """
        # delete data if refresh asked
        if refresh_data:
            shutil.rmtree(self.resource_dir)
            self.logger.info("MLP data directory deleted.")
        # download resources
        self.download_stanza_resources(self.resource_dir, self.supported_langs, logger=self.logger)
        self.download_entity_mapper_resources(self.resource_dir, logger=self.logger)
        self.download_concatenator_resources(self.resource_dir, logger=self.logger)


    @staticmethod
    def download_stanza_resources(resource_dir: str, supported_langs: List[str], logger=None):
        """
        Downloads Stanza resources if not present in resources directory.
        By default all is downloaded into data directory under package directory.
        """
        model_types = ["depparse", "lemma", "pos", "tokenize"]
        stanza_resource_path = pathlib.Path(resource_dir) / "stanza"
        if logger:
            logger.info(f"Downloading Stanza models into the directory: {str(stanza_resource_path)}")

        stanza_resource_path.mkdir(parents=True, exist_ok=True)  # Create the directories with default permissions including parents.
        for language_code in supported_langs:
            # rglob is for recursive filename pattern matching, if it matches nothing
            # then the necessary files do not exist and we should download them.
            lang_dir_exists = True if list(stanza_resource_path.rglob("{}*".format(language_code))) else False
            model_folders_exists = all([(stanza_resource_path / language_code / model_type).exists() for model_type in model_types])
            if not (lang_dir_exists and model_folders_exists):
                stanza.download(language_code, str(stanza_resource_path))


    @staticmethod
    def download_entity_mapper_resources(resource_dir: str, logger=None, entity_mapper_urls: tuple = ENTITY_MAPPER_DATA_URLS):
        entity_mapper_resource_path = pathlib.Path(resource_dir) / "entity_mapper"
        entity_mapper_resource_path.mkdir(parents=True, exist_ok=True)
        for url in entity_mapper_urls:
            file_name = urlparse(url).path.split("/")[-1]
            file_path = entity_mapper_resource_path / file_name
            if not file_path.exists():
                if logger: logger.info(f"Downloading entity mapper file {file_name} into the directory: {url}")
                response = urlopen(url)
                content = response.read().decode()
                with open(file_path, "w", encoding="utf8") as fh:
                    fh.write(content)


    def _load_entity_mapper(self):
        # create Entity Mapper instance
        data_dir = os.path.join(self.resource_dir, "entity_mapper")
        data_files = [os.path.join(data_dir, path) for path in os.listdir(data_dir)]
        self.loaded_entity_files = data_files
        return EntityMapper(data_files)


    @staticmethod
    def normalize_input_text(text: str) -> str:
        """
        Normalizes input text so it won't break anything.
        :param: str text: Input text.
        :return: Normalized text.
        """
        text = str(text)
        bs = BeautifulSoup(text, "lxml")
        text = bs.get_text(' ')  # Remove html.
        text = re.sub('(\n){2,}', '\n\n', text)
        text = re.sub('( )+', ' ', text)
        text = text.strip()
        return text


    def detect_language(self, text: str) -> Optional[str]:
        """
        Detects language of input text.
        If language not in supported list, language is defaulted or exception raised.
        :param: str text: Text to be analyzed.
        :return: Language code.
        """
        # try to detect language
        try:
            lang = detect(text)
        except:
            lang = None
        return lang


    def generate_document(self, raw_text: str, analyzers: List[str], json_object: dict = None, doc_paths="text", lang=None):
        processed_text = MLP.normalize_input_text(raw_text)
        # detect language
        if not lang:
            lang = self.detect_language(processed_text)
        '''
        check if detected language is supported if the language is not supported it will use default_lang to load
        stanza models yet keep the document lang as the detected language
        '''
        if lang not in self.supported_langs:
            analysis_lang = self.default_lang
            sentences, entities, e = self._get_stanza_tokens(analysis_lang, processed_text) if processed_text else ([], [], "")
        else:
            analysis_lang = lang
            sentences, entities, e = self._get_stanza_tokens(analysis_lang, processed_text) if processed_text else ([], [], "")

        document = Document(
            original_text=processed_text,
            dominant_language_code=lang,
            analysis_lang=analysis_lang,
            stanza_sentences=sentences,
            stanza_entities=entities,
            analyzers=analyzers,
            json_doc=json_object,
            doc_path=doc_paths,
            entity_mapper=self.get_entity_mapper(),
            concat_resources=self.concat_resources,
            error=e
        )
        return document


    @staticmethod
    def _load_analyzers(analyzers, supported_analyzers):
        if analyzers == ["all"]:
            return [analyzer for analyzer in supported_analyzers if analyzer != "all"]
        return [analyzer for analyzer in analyzers if (analyzer in supported_analyzers and analyzer != "all")]


    def get_entity_mapper(self):
        if self._entity_mapper is None:
            self._entity_mapper = self._load_entity_mapper()
        return self._entity_mapper

    def get_stanza_pipeline(self, lang: str):
        if lang not in self._stanza_pipelines:
            try:
                self._stanza_pipelines[lang] = stanza.Pipeline(
                    lang=lang,
                    dir=str(self.stanza_resource_path),
                    processors=self._get_stanza_processors(lang),
                    use_gpu=self.use_gpu,
                    logging_level=self.logging_level,
                )

            # This is for CUDA OOM exceptions. Fall back to CPU if needed.
            except RuntimeError:
                self._stanza_pipelines[lang] = stanza.Pipeline(
                    lang=lang,
                    dir=str(self.stanza_resource_path),
                    processors=self._get_stanza_processors(lang),
                    use_gpu=False,
                    logging_level=self.logging_level,
                )

        return self._stanza_pipelines[lang]


    def _get_stanza_tokens(self, lang: str, raw_text: str):
        sentences = []
        entities = []
        e = ""
        try:
            pipeline = self.get_stanza_pipeline(lang)(raw_text)

            for sentence in pipeline.sentences:
                words = []
                for word in sentence.words:
                    words.append(word)
                sentences.append(words)
                for entity in sentence.entities:
                    entities.append(entity)

        except KeyError as e:
            raise LanguageNotSupported(f"Language {lang} not supported. Check the list of supported languages.")

        except Exception as e:
            self.logger.exception(e)
            return sentences, entities, repr(e)

        return sentences, entities, e


    def _get_stanza_ner(self, lang: str, raw_text: str):
        pipeline = self.get_stanza_pipeline(lang)(raw_text)
        return [entity for sentence in pipeline.sentences for entity in sentence.entities]


    @staticmethod
    def _get_stanza_processors(lang):
        """
        Returns processor options based on language and NER support in Stanza.
        """
        if lang in STANZA_NER_SUPPORT:
            return "tokenize,pos,lemma,ner"
        else:
            return "tokenize,pos,lemma"


    def process(self, raw_text: str, analyzers: list = ["all"], lang=None):
        """
        Processes raw text.
        :param: raw_text str: Text to be processed.
        :param: analyzers list: List of analyzers to be used.
        :return: Processed text as document ready for Elastic.
        """
        loaded_analyzers = self._load_analyzers(analyzers, SUPPORTED_ANALYZERS)
        document = self.generate_document(raw_text, loaded_analyzers, lang=lang)

        if document:
            for analyzer in loaded_analyzers:
                # For every analyzer, activate the function that processes it from the
                # document class.
                self.__apply_analyzer(document, analyzer)
            return document.to_json()
        else:
            return None


    def lemmatize(self, raw_text: str, lang=None):
        """
        Lemmatizes input text.
        :param: raw_text str: Text to be lemmatized.
        :return: Lemmatized string.
        """
        document = self.process(raw_text, analyzers=["lemmas"], lang=lang)
        return document["text"]["lemmas"]


    def parse_doc_texts(self, doc_path: str, document: dict) -> list:
        """
        Function for parsing text values from a nested dictionary given a field path.
        :param doc_path: Dot separated path of fields to the value we wish to parse.
        :param document: Document to be worked on.
        :return: List of text fields that will be processed by MLP.
        """
        wrapper = PelicanJson(document)
        doc_path_as_list = doc_path.split(".")
        content = wrapper.safe_get_nested_value(doc_path_as_list, default=[])
        if content and isinstance(content, str):
            return [content]
        # Check that content is non-empty list and there are only stings in the list.
        elif content and isinstance(content, list) and all([isinstance(list_content, str) for list_content in content]):
            return content
        # In case the field path is faulty and it gives you a dictionary instead.
        elif isinstance(content, dict):
            return []
        else:
            return []


    def __apply_analyzer(self, doc, analyzer):
        try:
            getattr(doc, analyzer)()
        except Exception as e:
            self.logger.exception(e)


    def process_docs(self, docs: List[dict], doc_paths: List[str], analyzers=["all"]):
        """
        :param docs: Contains tuples with two dicts inside them, the first being the document to be analyzed and the second is the meta information that corresponds to the document for transport purposes later on.
        :param doc_paths: Dot separated paths for how to traverse the dict for the text value you want to analyze.
        :param analyzers: List of strings to determine which procedures you want your text to be analyzed with.
        :return: List of dictionaries where the mlp information is stored inside texta_facts and the last field of the doc_path in the format {doc_path}_mlp.
        """
        # Container for keeping the tuples of the doc and meta pairs.
        container = []
        for document in docs:
            for doc_path in doc_paths:
                # Traverse the (possible) nested dicts and extract their text values from it as a list of strings.
                # Since the nested doc_path could lead to a list there are multiple pieces of text which would be needed to process.
                doc_texts = self.parse_doc_texts(doc_path, document)
                for raw_text in doc_texts:
                    analyzers = self._load_analyzers(analyzers, SUPPORTED_ANALYZERS)
                    doc = self.generate_document(raw_text, analyzers, document, doc_paths=doc_path)
                    if doc:
                        for analyzer in analyzers:
                            # For every analyzer, activate the function that processes it from the
                            # document class.
                            self.__apply_analyzer(doc, analyzer)

                        result = doc.document_to_json(use_default_doc_path=False)
                        new_facts = result.pop("texta_facts", [])
                        existing_facts = document.get("texta_facts", [])
                        unique_facts = Document.remove_duplicate_facts(new_facts + existing_facts)
                        result["texta_facts"] = unique_facts
                        document = result

            if document:
                # Add in texta_facts even if nothing was done due to missing values.
                facts = document.get("texta_facts", [])
                document["texta_facts"] = facts
                container.append(document)
            else:
                # Add in at least something to avoid problems with operations that include indexing.
                container.append({})

        return container


    @staticmethod
    def download_concatenator_resources(resource_dir: str, logger):
        concat_resource_dir = pathlib.Path(resource_dir) / "concatenator"
        concat_resource_dir.mkdir(parents=True, exist_ok=True)
        for url in CONCATENATOR_DATA_FILES:
            file_name = urlparse(url).path.split("/")[-1]
            file_path = concat_resource_dir / file_name
            if not file_path.exists():
                if logger: logger.info(f"Downloading concatenator file {file_name} into the directory: {url}")
                response = urlopen(url)
                content = response.read().decode()
                with open(file_path, "w", encoding="utf8") as fh:
                    fh.write(content)


    def _load_not_entities(self):
        not_entities = list()
        with open(self.not_entities_path, "r", encoding="UTF-8") as file:
            for line in file.readlines():
                not_entities += [line.strip().lower()]
        return not_entities


    def _load_space_between_not_ok(self):
        space_between_not_ok = list()
        with open(self.space_between_not_ok_path, "r", encoding="UTF-8") as file:
            for line in file.readlines():
                space_between_not_ok += [line.strip()]

        return re.compile("|".join(space_between_not_ok))


    def _load_months(self):
        months = list()
        with open(self.months_path, "r", encoding="UTF-8") as file:
            for line in file.readlines():
                months += [line.strip()]
        return months
