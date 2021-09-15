from typing import List, Union
from ..base import BaseText2Vec
from ....base import catch_vector_errors
from ....doc_utils import ModelDefinition
from ....import_utils import *
from ....models_dict import MODEL_REQUIREMENTS
from datetime import date
if is_all_dependency_installed(MODEL_REQUIREMENTS['encoders-text-torch-transformers-auto']):
    from transformers import MT5EncoderModel, T5Tokenizer
    import torch

LegalBertModelDefinition = ModelDefinition(markdown_filepath='encoders/text/torch_transformers/legal_bert')

__doc__ = LegalBertModelDefinition.create_docs()

class LegalBert2Vec(BaseText2Vec):
    definition = LegalBertModelDefinition
    urls = {
            "nlpaueb/bert-base-uncased-contracts": {"data": "Trained on US contracts"},
            "nlpaueb/bert-base-uncased-eurlex": {"data": "Trained on EU legislation"}, 
            "nlpaueb/bert-base-uncased-echr	": {"data": "Trained on ECHR cases"},
            "nlpaueb/legal-bert-base-uncased": {"data": "Trained on all the above"},
            "nlpaueb/legal-bert-small-uncased": {"data": "Trained on all the above"}
    }
    def __init__(self, model_name: str="nlpaueb/legal-bert-base-uncased"):
        self.model = MT5EncoderModel.from_pretrained("google/mt5-small")
        self.tokenizer = T5Tokenizer.from_pretrained("google/mt5-small")

    @catch_vector_errors
    def encode(self, text: Union[str, List[str]], pooling_method='mean') -> List[float]:
        """
            Encode words using T5. It takes the last hidden state of the model and
            performs mean pooling across the layers to get a fixed-size vector.
            Args:
                text: str
        """
        input_ids = self.tokenizer(text, return_tensors="pt").input_ids
        outputs = self.model(input_ids).last_hidden_state
        if pooling_method == 'mean':
            return torch.mean(outputs, axis=1).tolist()[0]
        else:
            raise ValueError("Pooling method not implemented. Currently only implemented mean.")

    @catch_vector_errors
    def bulk_encode(self, texts: List[str]) -> List[List[float]]:
        """
            Encode multiple sentences using transformers.
            args:
                texts: List[str]
        """
        # We use pad_to_multiple_of as other arguments usually do not work.
        # TODO: FIx the older method
        # return torch.mean(self.model(**self.tokenizer(texts, return_tensors='pt', pad_to_multiple_of=self.tokenizer.model_max_length,
        #     truncation=True, padding=True))[0], axis=1).detach().tolist()
        return [self.encode(x) for x in texts]
