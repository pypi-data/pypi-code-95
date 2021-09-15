from typing import Dict, Any, List
from enum import Enum


class ActionServerRequest():
    def __init__(self, request: str, variables: Dict[Any, Any], user_request: Dict[Any, Any] = None) -> None:
        self.request = request
        self.variables = variables
        self.user_request = user_request

    def publish(self) -> Dict[Any, Any]:
        if self.user_request is None:
            return {
                "variables": self.variables,
                "request": self.request
            }
        else:
            return {
                "variables": self.variables,
                "request": self.request,
                "user_request": self.user_request
            }


class ButtonQuestion(ActionServerRequest):
    def __init__(self, question: str, buttons: Dict[str, str]):
        v = {
            "question": {
                "text": question,
                "buttons": [name for name in buttons]
            }
        }
        for name in buttons:
            v[name] = buttons[name]  # type:ignore
        super().__init__(
            "ask_button_question",
            v
        )


class YesNoQuestion(ActionServerRequest):
    def __init__(self, question: str, yes_action: str, no_action: str):
        super().__init__(
            "ask_yes_no_question",
            {
                "question": {
                    "text": question
                },
                "yes_action": yes_action,
                "no_action": no_action
            }
        )


class OpenQuestion(ActionServerRequest):
    def __init__(self, question: str, handler: str):
        super().__init__(
            "ask_open_question",
            {
                "question": {
                    "text": question
                },
                "answer_handler": handler
            }
        )


class Fail(ActionServerRequest):
    def __init__(self, fail_msg: str = None):
        super().__init__(
            "notify_action_fail",
            {"action_text": "not_understood" if fail_msg is None else fail_msg}
        )


class Tell(ActionServerRequest):
    def __init__(self, msg: str):
        super().__init__(
            "tell_user",
            {"msg": msg}
        )


class Do(ActionServerRequest):
    def __init__(self, action: str, user_request: Dict[Any, Any] = None):
        super().__init__(
            "perform_action",
            {"action": action},
            user_request
        )


class MultiSelectQuestion(ActionServerRequest):
    def __init__(self, question: str, options: List[str], handler: str):
        super().__init__(
            "ask_mutli_select_question",
            {
                "answer_handler": handler,
                "question": {
                    "text": question,
                    "buttons": options
                }
            }
        )


class CheckboxQuestion(ActionServerRequest):
    def __init__(self, question: str, options: List[str], handler: str):
        super().__init__(
            "ask_checkbox_question",
            {
                "answer_handler": handler,
                "question": {
                    "text": question,
                    "checkboxes": options
                }
            }
        )


class DateQuestion(ActionServerRequest):
    def __init__(self, question: str, handler: str):
        super().__init__(
            "ask_date_question",
            {
                "answer_handler": handler,
                "question": {
                    "text": question
                }
            }
        )


class FormQuestionTypes(Enum):
    MultiSelect = 1
    Checkbox = 2
    Open = 3
    Date = 4


class Form(ActionServerRequest):
    def __init__(self, title: str, submit_handler: str):
        super().__init__(
            "ask_form",
            {},
            {
                "form_data": {
                    "title": title,
                    "questions": {},
                    "submit_action": submit_handler
                }
            }
        )
        self.keys = []

    def add_question(self, key: str, type: FormQuestionTypes, question: str, options: List[str] = None):
        if key in self.keys:
            raise ValueError("Question Key Exists")
        else:
            if type == FormQuestionTypes.MultiSelect:
                self.user_request["form_data"]["questions"].append({
                    "key": key,
                    "type": "multi_choice",
                    "question": question,
                    "options": options
                })
            elif type == FormQuestionTypes.Checkbox:
                self.user_request["form_data"]["questions"].append({
                    "key": key,
                    "type": "checkbox",
                    "question": question,
                    "options": options
                })
            elif type == FormQuestionTypes.Open:
                self.user_request["form_data"]["questions"].append({
                    "key": key,
                    "type": "text",
                    "question": question
                })
            elif type == FormQuestionTypes.Date:
                self.user_request["form_data"]["questions"].append({
                    "key": key,
                    "type": "date",
                    "question": question
                })
            else:
                raise ValueError("Invalid Form Question Type")
            self.keys.append(key)
