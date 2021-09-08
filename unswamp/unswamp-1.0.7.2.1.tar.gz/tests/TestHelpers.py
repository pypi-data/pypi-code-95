import pandas as pd
import numpy as np
import string
from random import seed, random, randint, choice, SystemRandom


class TestHelpers():
    _dataset = None
    @staticmethod
    def load_test_dataset():
        if TestHelpers._dataset is None:
            data_file = "https://data.cityofnewyork.us/api/views/825b-niea/rows.csv?accessType=DOWNLOAD"
            dataset = pd.read_csv(data_file)
            dataset["LineNumber"] = dataset.index
            dataset["LineNumberInverse"] = dataset.shape[0] - dataset["LineNumber"]
            dataset["RandomNumber"] = np.random.choice([1, 9, 20], dataset.shape[0])
            dataset["ConstantNumber"] = 5
            dataset["DataFile"] = data_file
            dataset["NullColumn"] = np.nan
            TestHelpers._dataset = dataset
        return TestHelpers._dataset

    @staticmethod
    def random_string(length=10):
        rand = "".join(SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(length))
        return rand

    @staticmethod
    def random_bool():
        rand = random()
        value = rand >= 0.5
        return value

    @staticmethod
    def test_run(test, check, expectation):
        dataset = TestHelpers.load_test_dataset()
        result = check.run(dataset)
        test.assertEqual(
            result.passed, expectation, f"The result of check '{type(check)}' was expected to be '{expectation}' but was '{result.passed}'")
