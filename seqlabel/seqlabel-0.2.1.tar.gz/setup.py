# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['seqlabel']

package_data = \
{'': ['*']}

install_requires = \
['pyahocorasick>=1.4.2,<2.0.0', 'pytokenizations>=0.8.4,<0.9.0']

setup_kwargs = {
    'name': 'seqlabel',
    'version': '0.2.1',
    'description': 'Rule-based Text Labeling Framework Aiming at Flexibility',
    'long_description': '# seqlabel: Flexible Rule-based Text Labeling\n\n![CI badge](https://github.com/tech-sketch/seqlabel/actions/workflows/ci.yml/badge.svg)\n\n*seqlabel* is a rule-based text labeling framework aiming at flexibility. \n\n## Installation\n\nTo install seqlabel:\n\n```sh\npip install seqlabel\n```\n\n## Requirements\n\n- Python 3.8+\n\n\n## Usage\n\n### For a normal text\n\nFirst, import some classes.\n\n```py\nfrom seqlabel import Text\nfrom seqlabel.matchers import DictionaryMatcher\nfrom seqlabel.entity_filters import LongestMatchFilter, MaximizedMatchFilter\nfrom seqlabel.serializers import IOB2Serializer\n```\n\nInitialize `Text` by giving it a text you want to label over.\n\n```py\ntext = Text("Tokyo is the capital of Japan.")\n```\n\nPrepare `matcher` matching supplied patterns. You can supply patterns via Hash Map mapping string sequences to the corresponding labels. You can define your own matcher by inheriting `seqlabel.matchers.Matcher`.  \n\nThen, apply `matcher.match` to `text`.  \n\n```py\n# Preparing Matcher\nmatcher = DictionaryMatcher()\n# Adding patterns\nmatcher.add({"Tokyo": "LOC", "Japan": "LOC"})\n# Matching\nentities = matcher.match(text)\n```\n\nFilter unwanted entities. `LongestMatchFilter` removes overlapping entities and leaves longer entity. `MaximizedMatchFilter` removes overlapping entities and leaves as many entities as possible. You can define your own filter by inheriting `seqlabel.entity_filters.EntityFilter`.\n\n```py\nfilter_a = LongestMatchFilter()\nfiltered_entities_a = filter_a(entities)\n\nfilter_b = MaximizedMatchFilter()\nfiltered_entities_b = filter_b(entities)\n```\n\nConvert entities to IOB2 format after matching and filtering. Check `seqlabel.serializers` out if you want to use other formats.\n\n```py\nserializer = IOB2Serializer()\nserializer.save(text, filtered_entities_a)\n```\n\n### For a tokenized text\n\nIf you want to process a tokenized text, you need to use `TokenizedText` instead of `Text`. You could import it as follows:\n\n```py\nfrom seqlabel import TokenizedText\n```\n\nInitialize `TokenizedText` by giving it `tokens` and `space_after` you want to label over. `tokens` is a list of strings and `space_after` is a list of boolean indicating whether each token has a subsequent space.\n\n```py\ntokenized_text = TokenizedText(\n  ["Tokyo", "is", "the", "captial", "of", "Japan", "."],\n  [True, True, True, True, True, True, False]\n)\n```\n\nYou can use `matcher`, `filter`, and `serializer` just like a normal text, as shown above.\n\n```py\n# Mathcing\nentities = matcher.match(tokenized_text)\n# Filtering\nfiltered_entities = filter_a(entities)\n# Serializing\nserializer.save(tokenized_text, filtered_entities)\n```\n',
    'author': 'Yasufumi Taniguchi',
    'author_email': 'yasufumi.taniguchi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tech-sketch/seqlabel',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
