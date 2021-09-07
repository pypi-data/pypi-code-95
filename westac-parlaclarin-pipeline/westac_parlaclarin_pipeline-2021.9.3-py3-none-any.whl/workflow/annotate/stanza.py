"""PoS tagging using Stanford's Stanza library.
NOTE! THIS CODE IS IN PART BASED ON https://github.com/spraakbanken/sparv-pipeline/blob/master/sparv/modules/stanza/stanza.py

Fix Windows CUDA TDR error:

https://www.pugetsystems.com/labs/hpc/Working-around-TDR-in-Windows-for-a-better-GPU-computing-experience-777/

"""

import os
from typing import Callable, List, Union

import stanza

from ..model.convert import pretokenize
from .interface import ITagger, TaggedDocument

jj = os.path.join


"""Follow Språkbanken Sparv's naming of model names and config keys."""
STANZA_CONFIGS: dict = {
    "sv": {
        "resources_file": "resources.json",
        "lem_model": jj("lem", "sv_suc_lemmatizer.pt"),
        "pos_model": jj("pos", "full_sv_talbanken_tagger.pt"),
        "pretrain_pos_model": jj("pos", "full_sv_talbanken.pretrain.pt"),
        "dep_model": jj("dep", "sv_talbanken_parser.pt"),
        "pretrain_dep_model": jj("pos", "full_sv_talbanken.pretrain.pt"),
    }
}


class StanzaTagger(ITagger):
    """Stanza PoS tagger wrapper"""

    def __init__(
        self,
        model_root: str,
        preprocessors: Callable[[str], str],
        lang: str = "sv",
        processors: str = "tokenize,lemma,pos",
        tokenize_pretokenized: bool = True,
        tokenize_no_ssplit: bool = True,
        use_gpu: bool = True,
    ):
        super().__init__(preprocessors=preprocessors or [pretokenize])

        """Initialize stanza pipeline

        Args:
            model_root (str): where Språkbanken's Stanza models are stored
            preprocessors (Callable[[str], str]): Text transforms to do prior to tagging.
            lang (str, optional): Language (only 'sv' supported). Defaults to "sv".
            processors (str, optional): Stanza process steps. Defaults to "tokenize,lemma,pos".
            tokenize_pretokenized (bool, optional): If true, then already tokenized. Defaults to True.
            tokenize_no_ssplit (bool, optional): [description]. Defaults to True.
            use_gpu (bool, optional): If true, use GPU if exists. Defaults to True.
        """
        print(f"stanza: processors={processors} use_gpu={use_gpu}")
        config: dict = STANZA_CONFIGS[lang]
        self.nlp: stanza.Pipeline = stanza.Pipeline(
            lang=lang,
            processors=processors,
            dir=model_root,
            pos_pretrain_path=jj(model_root, config["pretrain_pos_model"]),
            pos_model_path=jj(model_root, config["pos_model"]),
            lemma_model_path=jj(model_root, config["lem_model"]),
            tokenize_pretokenized=tokenize_pretokenized,
            tokenize_no_ssplit=tokenize_no_ssplit,
            use_gpu=use_gpu,
            verbose=False,
        )

    def tag(self, text: Union[str, List[str]]) -> List[TaggedDocument]:
        """Tag text. Return dict if lists."""
        if isinstance(text, str):
            text = [text]

        if isinstance(text, list):

            if len(text) == 0:
                return []

            documents: List[stanza.Document] = [stanza.Document([], text=self.preprocess(d)) for d in text]

            tagged_documents: List[stanza.Document] = self.nlp(documents)

            if isinstance(tagged_documents, stanza.Document):
                tagged_documents = [tagged_documents]

            return [self.to_dict(d) for d in tagged_documents]

        return ValueError("invalid type")

    def to_dict(self, tagged_document: stanza.Document) -> TaggedDocument:
        """Extract tokens from tagged document. Return dict of list."""

        tokens, lemmas, pos, xpos = [], [], [], []
        # FIXME: Iterate tokens instead???
        for w in tagged_document.iter_words():
            tokens.append(w.text)
            lemmas.append(w.lemma or w.text.lower())
            pos.append(w.upos)
            xpos.append(w.xpos)

        return dict(
            token=tokens,
            lemma=lemmas,
            pos=pos,
            xpos=xpos,
            num_tokens=tagged_document.num_tokens,
            num_words=tagged_document.num_words,
        )

    # @staticmethod
    # def to_csv(tagged_document: TaggedDocument, sep='\t') -> str:
    #     """Converts a stanza.Document to a TSV string"""

    #     csv_str = '\n'.join(f"{w.text}{sep}{w.lemma}{sep}{w.upos}{sep}{w.xpos}" for w in tagged_document.iter_words())
    #     csv_str = f"text{sep}lemma{sep}pos{sep}xpos\n{csv_str}"
    #     return csv_str
