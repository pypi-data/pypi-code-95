# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Scoring functions that can load a serialized model and predict."""

import logging
import numpy as np
import os
import pandas as pd
import scipy
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    default_data_collator,
)
from typing import Tuple

from azureml.automl.dnn.nlp.classification.common.constants import (
    DatasetLiterals,
    MultiClassInferenceLiterals
)
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language
from azureml.automl.dnn.nlp.common.constants import (
    OutputLiterals,
    Warnings
)
from azureml.core import Dataset as AmlDataset
from azureml.core.run import Run

logger = logging.getLogger(__name__)


class MulticlassInferencer:
    """Class to perform inferencing using training runId and on an unlabeled dataset"""

    def __init__(self,
                 run: Run,
                 device: str):
        """Function to initialize the inferencing object

        :param: Run object
        :param device: device to be used for inferencing
        """
        self.run_object = run
        self.device = device

        if self.device == "cpu":
            logger.warning(Warnings.CPU_DEVICE_WARNING)

        self.workspace = self.run_object.experiment.workspace

    def download_file(
            self,
            run: Run,
            artifact_type: str,
            path: str,
            file_name: str
    ) -> None:
        """Downloads files associated with the run.

        :param run: run context of the run that produced the model
        :param artifact_type: artifact file type
        :param path: artifacts directory path
        :param file_name: file name for artifact
        """
        logger.info("Start downloading {} artifact".format(artifact_type))
        run.download_file(os.path.join(path, file_name), output_file_path=file_name)
        logger.info("Finished downloading {} artifact".format(artifact_type))

    def load_training_artifacts(
            self,
            run: Run,
            artifacts_dir: str,
            dataset_language: str
    ) -> Tuple[AutoModelForSequenceClassification, AutoTokenizer, np.ndarray]:
        """Load the training artifacts.

        :param run: run context of the run that produced the model
        :param artifacts_dir: artifacts directory
        :param dataset_language: language code of dataset
        :return: returns the model, tokenizer and train_label_list from the model's training
        """
        logger.info("Start fetching training artifacts")
        self.download_file(run, OutputLiterals.ARTIFACT_TYPE_TOKENIZER, artifacts_dir,
                           MultiClassInferenceLiterals.TOKENIZER_FILE_NAME)
        self.download_file(run, OutputLiterals.ARTIFACT_TYPE_MODEL, artifacts_dir,
                           MultiClassInferenceLiterals.MODEL_FILE_NAME)
        self.download_file(run, OutputLiterals.ARTIFACT_TYPE_TRAINING_ARGS, artifacts_dir,
                           MultiClassInferenceLiterals.TRAINING_ARGS)
        self.download_file(run, OutputLiterals.ARTIFACT_TYPE_LABELS, artifacts_dir,
                           MultiClassInferenceLiterals.LABEL_LIST)
        model_name_or_path, _ = get_model_from_language(dataset_language)
        # TODO: figure out why the tokenizer.config isn't working out
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        train_label_list = np.load(MultiClassInferenceLiterals.LABEL_LIST, allow_pickle=True)
        config = AutoConfig.from_pretrained(model_name_or_path, num_labels=len(train_label_list))
        model = AutoModelForSequenceClassification.from_pretrained(MultiClassInferenceLiterals.MODEL_FILE_NAME,
                                                                   config=config)
        logger.info("Training artifacts restored successfully")
        return model, tokenizer, train_label_list

    def predict(self,
                trainer: Trainer,
                test_dataset: PyTorchMulticlassDatasetWrapper,
                df: pd.DataFrame,
                train_label_list: np.ndarray,
                label_column_name: str) -> pd.DataFrame:
        """Generate predictions using model

        :param trainer: Trainer object using which the model was trained
        :param test_dataset: Datasets.dataset object containing test data
        :param df: DataFrame to make predictions on
        :param train_label_list: list of labels from training data
        :param label_column_name: Name/title of the label column
        :return: Dataframe with predictions
        """
        predictions = trainer.predict(test_dataset=test_dataset).predictions
        preds = np.argmax(predictions, axis=1)
        probas = scipy.special.softmax(predictions, axis=1)
        pred_probas = np.amax(probas, axis=1)
        predicted_labels = [train_label_list[item] for item in preds]
        if trainer.is_world_process_zero():
            df[label_column_name] = predicted_labels
            df[DatasetLiterals.LABEL_CONFIDENCE] = pred_probas
        return df

    def score(self, input_dataset_id: str,
              label_column_name: str,
              dataset_language: str) -> pd.DataFrame:
        """Generate predictions from input files.

        :param input_dataset_id: The input dataset id
        :param label_column_name: Name/title of the label column
        :param dataset_language: language code of dataset
        :return: Dataframe with predictions
        """
        model, tokenizer, train_label_list = self.load_training_artifacts(self.run_object, OutputLiterals.OUTPUT_DIR,
                                                                          dataset_language)
        # TODO: compute metrics will be added when we support TSI in NLP DNN
        trainer = Trainer(
            model=model,
            tokenizer=tokenizer,
            data_collator=default_data_collator,
        )
        # Fetch AmlDataset object
        ds = AmlDataset.get_by_id(self.workspace, input_dataset_id)
        logger.info("Type of input Dataset is: {}".format(type(ds)))

        # Convert AmlDataset to dataframe and obtain dataloader
        df = ds.to_pandas_dataframe()
        if label_column_name in df.columns:
            df.drop(columns=label_column_name, inplace=True)
        inference_data = PyTorchMulticlassDatasetWrapper(df, train_label_list,
                                                         dataset_language, label_column_name=None)
        return self.predict(trainer, inference_data, df, train_label_list, label_column_name)
