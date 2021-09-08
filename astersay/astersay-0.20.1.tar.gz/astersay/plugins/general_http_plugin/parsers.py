#
#  Copyright (c) 2021. Egor Demushin.
#  All rights reserved.
#  This file is distributed under the same license as the current project.
#

import json


class BaseParser:
    parser_params = {}

    def __init__(self, conf=None):
        if conf:
            self.parser_params.update(conf)

    def parse(self, text):
        """
        Переопределите этот метод в вашем классе.
        """
        raise NotImplementedError


class PlainTextParser(BaseParser):
    parser_params = {
        'variable_name': 'http_answer'
    }

    def parse(self, text):
        key = self.parser_params['variable_name']
        return {key: text}


class JsonParser(BaseParser):
    def parse(self, text):
        return json.loads(text, **self.parser_params)
