# %%
from eaas import Client
import jsonlines
from pathlib import Path
import os
import unittest

curr_dir = Path(__file__).parent


def read_jsonlines_to_list(file_name):
    lines = []
    with jsonlines.open(file_name, 'r') as reader:
        for obj in reader:
            lines.append(obj)
    return lines


class TestMetrics(unittest.TestCase):
    def test_api(self):
        client = Client()
        client.load_config("config.json")

        input_file = os.path.join(curr_dir, "inputs", "multi_ref.jsonl")
        inputs = read_jsonlines_to_list(input_file)
        res = client.score(inputs)
        print(res)


