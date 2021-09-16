
from haystack import Pipeline
from rest_api.config import PIPELINE_YAML_PATH, FILE_UPLOAD_PATH, INDEXING_PIPELINE_NAME
from pathlib import Path

from haystack.document_store.base import BaseDocumentStore

INDEXING_PIPELINE = Pipeline.load_from_yaml(Path(PIPELINE_YAML_PATH), pipeline_name=INDEXING_PIPELINE_NAME)
res = INDEXING_PIPELINE.get_nodes_by_class(class_type=BaseDocumentStore)
