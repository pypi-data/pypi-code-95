from random import shuffle
from typing import Any

import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import BaseFuzzyAttribute
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.documents.models import Document
from wagtail.images import get_image_model
from wagtail_factories.blocks import StreamFieldFactory

from coop.utils.testdata import get_random_image, rbool

Image = get_image_model()


class FuzzyImage(BaseFuzzyAttribute):
    def fuzz(self) -> Image:
        return get_random_image()


class FuzzyPage(BaseFuzzyAttribute):
    def fuzz(self) -> Page:
        return Page.objects.order_by('?').first()


class FuzzyWords(factory.Faker):
    def __init__(self, nb_words: int = 1, maybe: bool = False):
        self.maybe = maybe
        super().__init__('sentence', nb_words=nb_words)

    def evaluate(self, instance, step, extra) -> str:
        if self.maybe and not rbool():
            return ''
        # create a variable sentece, remove full stop
        value = super().evaluate(instance, step, extra)
        return value[:-1]


class ListLengthBlockFactory(factory.SubFactory):
    """
    Returns an n list of generated blocks
    Usage: ListLengthBlockFactory(SubblockFactory, length=10)
    """

    def __init__(self, factory, length=1, **kwargs):
        self.length = length
        super().__init__(factory, **kwargs)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        # TODO could be used with provided values then + (length - provided) generated appended
        return self.evaluate(None, None, kwds)

    def evaluate(self, instance, step, extra):
        subfactory = self.get_factory()
        ret_val = []
        for _ in range(self.length):
            # Very naive, assumes all default values
            ret_val.append(subfactory())
        return ret_val

    class Meta:
        model = blocks.ListBlock


class OrderableFactory(DjangoModelFactory):
    sort_order = factory.Sequence(lambda n: n)


# https://github.com/wagtail/wagtail-factories/pull/25
class RichTextBlockFactory(factory.Factory):
    """
    Usage: rich_text = RichTextBlockFactory(value=lpar(n(1, 3)))
    """
    @classmethod
    def _build(cls, model_class, value=""):
        block = model_class()
        return block.to_python(value)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)

    class Meta:
        model = blocks.RichTextBlock


class FuzzyStreamFieldFactory(StreamFieldFactory):
    def __init__(self, factories, shuffle_blocks=True, **kwargs):
        self.shuffle_blocks = shuffle_blocks
        super().__init__(factories, **kwargs)

    def generate(self, step, params):
        retval = []
        for block_name, block_factory in self.factories.items():
            retval.append((block_name, block_factory()))
        if self.shuffle_blocks:
            shuffle(retval)
        return retval


class FuzzyDocument(BaseFuzzyAttribute):
    def fuzz(self) -> Document:
        return Document.objects.order_by('?').first()


class FuzzyParagraphs(factory.Faker):
    def __init__(self, num=1, **kwargs):
        super().__init__('paragraphs', nb=num, **kwargs)

    def evaluate(self, instance, step, extra) -> str:
        value = super().evaluate(instance, step, extra)
        return ''.join(f'<p>{p}</p>' for p in value)
