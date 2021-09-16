from typing import Mapping, Type

from pyriksprot import ITagger, SwedishDehyphenatorService, dedent, pretokenize

# from .spacy2 import SpacyTagger
from .stanza import StanzaTagger

# pylint: disable=unused-argument


class TaggerRegistry:

    instances: Mapping[Type[ITagger], ITagger] = {}

    @staticmethod
    def get(tagger_cls, model: str, dehyphen_opts: dict, use_gpu: bool = True, **kwargs) -> ITagger:

        if tagger_cls not in TaggerRegistry.instances:

            preprocessors = [
                dedent,
                SwedishDehyphenatorService.create_dehypen(**dehyphen_opts),
                str.strip,
                pretokenize,
            ]

            if tagger_cls is StanzaTagger:
                TaggerRegistry.instances[tagger_cls] = StanzaTagger(
                    model=model,
                    preprocessors=preprocessors,
                    use_gpu=use_gpu,
                )

            # if tagger_cls is SpacyTagger:
            #     TaggerRegistry.instances[tagger_cls] = SpacyTagger(preprocessors=preprocessors, **kwargs)

        return TaggerRegistry.instances[tagger_cls]
