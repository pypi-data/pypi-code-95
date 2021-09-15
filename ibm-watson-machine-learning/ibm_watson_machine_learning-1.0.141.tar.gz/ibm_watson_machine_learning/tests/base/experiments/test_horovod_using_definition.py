import os
import unittest

from ibm_watson_machine_learning.tests.base.abstract.abstract_deep_learning_test import \
    AbstractDeepLearningTest


class TestHorovodTraining(AbstractDeepLearningTest, unittest.TestCase):
    """
    Test case checking the scenario of training an horovod model
    using model_definition only.
    """

    model_definition_name = "horovod_model_definition"
    training_name = "test_horovod_training"
    training_description = "training - Horovod"
    software_specification_name = "tensorflow_2.4-py3.8-horovod"
    execution_command = "python tensorflow_mnist.py"

    data_location = os.path.join(os.getcwd(), "base", "datasets", "tensorflow", "mnist.npz")
    data_cos_path = "mnist.npz"
    model_paths = [
        os.path.join(os.getcwd(), "base", "artifacts", "horovod", "tf_horovod.zip")
    ]
