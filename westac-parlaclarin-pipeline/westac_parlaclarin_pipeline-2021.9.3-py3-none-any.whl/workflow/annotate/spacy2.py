import os
from typing import Callable, List, Union

import spacy
from spacy.language import Language
from spacy.tokens import Doc

from .interface import ITagger, TaggedDocument

nj = os.path.normpath
jj = os.path.join

MODEL_ROOT = jj("/", "data", "spacy")

SWEDISH_UPOS_MODEL = jj(MODEL_ROOT, "sv_model_upos", "sv_model0", "sv_model_upos0-0.0.0")


class SpacyTagger(ITagger):
    def __init__(
        self,
        model: str = SWEDISH_UPOS_MODEL,
        preprocessors: Callable[[str], str] = None,
        disable: str = "parser,ner",
        n_process: int = 1,
        **_,
    ):

        super().__init__(preprocessors=preprocessors or [])

        self.model: str = model
        self.n_process: int = n_process
        self.disable = disable.split(",")
        self._nlp: Language = spacy.load(model, disable=disable.split(","))

    @property
    def nlp(self) -> Language:
        if self._nlp is None:
            self._nlp: Language = spacy.load(self.model, disable=self.disable)
        return self._nlp

    def tag(self, text: Union[str, List[str]]) -> List[TaggedDocument]:
        """Tag text. Return dict if lists."""

        if isinstance(text, str):
            text = [text]

        if len(text) == 0:
            return []

        tagged_documents: List[Doc] = list(self.nlp.pipe(texts=text, n_process=self.n_process))

        return [self.to_dict(d) for d in tagged_documents]

    def to_dict(self, tagged_document: Doc) -> TaggedDocument:
        """Extract tokens from tagged document. Return dict of list."""

        tokens, lemmas, pos, xpos = [], [], [], []

        for w in tagged_document:
            tokens.append(w.text)
            lemmas.append(w.lemma_ or w.text.lower())
            pos.append(w.tag_)
            xpos.append(w.tag_)

        return dict(
            token=tokens,
            lemma=lemmas,
            pos=pos,
            xpos=xpos,
            num_tokenslen=len(tagged_document),
            num_words=len(tagged_document),
        )
