import json
from typing import List


class Fact:

    def __init__(self, fact_type: str, fact_value: str, doc_path: str = None, fact_lemma: str = None, spans: list = [[0, 0]]):
        self.fact_type = fact_type
        self.fact_value = fact_value
        self.spans = spans
        self.doc_path = doc_path
        self.fact_lemma = fact_lemma


    @staticmethod
    def from_json(list_of_facts: List[dict]):
        container = []
        for fact_json in list_of_facts:
            fact_type = fact_json.get("fact")
            spans = json.loads(fact_json.get("spans"))
            value = fact_json.get("str_val")
            field_path = fact_json.get("doc_path")
            fact = Fact(fact_type=fact_type, fact_value=value, doc_path=field_path, spans=spans)
            container.append(fact)
        return container


    def to_json(self):
        container = {
            "str_val": self.fact_value,
            "spans": json.dumps(self.spans),
            "fact": self.fact_type,
            "doc_path": self.doc_path,
        }
        if self.fact_lemma:
            container["lemma"] = self.fact_lemma
        return container
