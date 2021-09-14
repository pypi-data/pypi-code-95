import os
import unittest

from ibm_watson_machine_learning.tests.base.abstract.abstract_deep_learning_test import \
    AbstractDeepLearningTest


class TestPyTorchTraining(AbstractDeepLearningTest, unittest.TestCase):
    """
    Test case checking the scenario of training an PyTorch model
    using model_definition only.
    """

    model_definition_name = "pytorch_model_definition"
    training_name = "test_pytorch_training"
    training_description = "torch-test-experiment"
    software_specification_name = "pytorch-onnx_1.7-py3.8"
    execution_command = "python torch_mnist.py --epochs 1"

    data_location = os.path.join(os.getcwd(), "base", "datasets", "tensorflow", "mnist.npz")
    data_cos_path = "mnist.npz"
    model_paths = [
        os.path.join(os.getcwd(), "base", "artifacts", "pytorch", "pytorch-model.zip")
    ]
