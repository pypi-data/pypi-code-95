import egune
from egune.requests import FormQuestionTypes
import yaml
import random
import re


class ResponseManager:
    def __init__(self, config_path, test):
        self.config = yaml.safe_load(open(config_path, "r"))
        self.response = self.config['responses']
        self.test = test

    def ResponseWeighter(self):
        self.response_weighter = "uniform"
        self.post_processors = "grammar_checker"

    def ResponseSelect(self, template):
        if self.test:
            return template[0]
        else:
            return random.choice(template)

    def ResponseFormatter(self, result, data):
        self.result = result
        result = re.sub(r"\$\{([^\$]*)\}", "%(\\1)s", self.result)
        self.result = result % data
        return self.result

    def responder(self, key, data):
        if key in self.response:
            currentKey = self.response[key]
            currentTypes = currentKey['type']
            currentData = currentKey['required_data']
            checkKeysExist = all(item in data.keys() for item in currentData)
            if checkKeysExist is True:
                if currentTypes == "Tell":
                    currentTemp = currentKey['templates']
                    return egune.Tell(self.ResponseFormatter(self.ResponseSelect(currentTemp), data))
                elif currentTypes == "Fail":
                    currentTemp = currentKey['templates']
                    return egune.Fail(self.ResponseFormatter(self.ResponseSelect(currentTemp), data))
                elif currentTypes == "YesNoQuestion":
                    currentTemp = currentKey['templates']
                    yes_action = currentKey['constants']['yes_action']
                    no_action = currentKey['constants']['no_action']
                    return egune.YesNoQuestion(self.ResponseFormatter(self.ResponseSelect(currentTemp), data),
                                               yes_action, no_action)
                elif currentTypes == "MultiSelectQuestion":
                    currentTemp = currentKey['templates']
                    handler = currentKey['constants']['handler']
                    options = data['options']
                    return egune.MultiSelectQuestion(self.ResponseFormatter(self.ResponseSelect(currentTemp), data),
                                                     options, handler)
                elif currentTypes == "Do":
                    currentTemp = currentKey['templates']
                    return egune.Do(self.ResponseFormatter(self.ResponseSelect(currentTemp), data))
                elif currentTypes == "OpenQuestion":
                    question = data['question']
                    handler = currentKey['constants']['handler']
                    return egune.OpenQuestion(question, handler)
                elif currentTypes == "ButtonQuestion":
                    options = data['options']
                    question = data['question']
                    return egune.ButtonQuestion(question, options)
                elif currentTypes == "Success":
                    currentTemp = currentKey['templates']
                    return egune.Success(self.ResponseFormatter(self.ResponseSelect(currentTemp), data))
                elif currentTypes == "TellPreparedMessage":
                    currentTemp = currentKey['templates']
                    return egune.TellPreparedMessage(self.ResponseFormatter(self.ResponseSelect(currentTemp), data))
                elif currentTypes == "TellCustom":
                    handler = currentKey['constants']['handler'] if "handler" in currentKey['constants'] else None
                    options = data['options']
                    text = currentKey['constants']['text'] if "text" in currentKey['constants'] else None
                    if type(currentKey['constants']['text']) == list:
                        text = self.ResponseSelect(text)
                    return egune.TellCustom(self.ResponseFormatter(text, data), options, handler)
                elif currentTypes == "CheckboxQuestion":
                    handler = currentKey['constants']['handler']
                    options = data['options']
                    question = data['question']
                    return egune.CheckboxQuestion(question, options, handler)
                elif currentTypes == "Form":
                    f = egune.Form('some_form_example_title', "some_form_example_handler")
                    questions = data['questions']
                    currentQuestion = currentKey['questions']
                    for key, value in questions.items():
                        finalTemplate = questionsParser(currentQuestion, key, value)['templates']
                        options, convertedType = typeParser(value)  # type:ignore
                        f.add_question(key, FormQuestionTypes(convertedType), finalTemplate, options)
                    return f
        else:
            return egune.Tell("Key олдсонгүй")

class NoPossibleTemplate(Exception):
    pass


def questionsParser(a, key, b):
    def isQuestion(obj):
        if obj is dict:
            if obj['type'] is not None:
                return True
        return False

    if isQuestion(a) and isQuestion(b):
        if key not in a:
            a[key] = b
        else:
            if not b['templates']:
                if not a[key]:
                    raise NoPossibleTemplate("Need more templates")
                return a[key]
            else:
                a[key]['templates'] = list(set(a[key]['templates'] + b['templates']))
    return b


def typeParser(val):
    qtype = val['type']
    if qtype == 'Open':
        return None, 3
    elif qtype == 'MultiSelect':
        return val['options'], 1
    elif qtype == 'Date':
        return None, 4
    elif qtype == 'Checkbox':
        return val['options'], 2
