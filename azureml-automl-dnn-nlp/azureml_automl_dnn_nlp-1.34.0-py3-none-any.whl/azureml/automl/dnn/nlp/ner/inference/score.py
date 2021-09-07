# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Scoring functions that can load a serialized model and predict."""

import logging
import os
import json
import time
from typing import Tuple

from transformers import (
    AutoConfig,
    AutoModelForTokenClassification,
    AutoTokenizer,
    Trainer,
)

from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals
from azureml.automl.dnn.nlp.common.data_utils import download_file_dataset
from azureml.automl.dnn.nlp.common.utils import get_run_by_id, _get_language_code
from azureml.automl.dnn.nlp.ner.ner_tasks import write_predictions_to_file
from azureml.automl.dnn.nlp.ner.io.read.dataset_wrapper import DatasetWrapper
from azureml.automl.dnn.nlp.ner.io.read.labeling_data_helper import (
    load_test_dataset_for_labeling_service, generate_results_for_labeling_service
)
from azureml.automl.dnn.nlp.ner.token_classification_metrics import TokenClassificationMetrics
from azureml.automl.dnn.nlp.ner.utils import get_labels, Split
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language
from azureml.core.run import Run

_logger = logging.getLogger(__name__)


def _download_file(
        run: Run,
        artifact_type,
        path,
        file_name
) -> None:
    """Downloads artifact files associated with the run.

    :param run: run context of the run that produced the model
    :param artifact_type: artifact file type
    :param path: artifacts directory path
    :file_name: file name for artifact
    """
    _logger.info("Start downloading {} artifact".format(artifact_type))
    run.download_file(os.path.join(path, file_name), output_file_path=file_name)
    _logger.info("Finished downloading {} artifact".format(artifact_type))


def _load_training_artifacts(
        run: Run,
        artifacts_dir: str,
        dataset_language: str
) -> Tuple[AutoModelForTokenClassification, AutoTokenizer, AutoConfig]:
    """Load the training artifacts.

    :param run: run context of the run that produced the model
    :param artifacts_dir: artifacts directory
    :return: returns the model, tokenizer and config from the model's training
    """
    _logger.info("Start fetching model from artifacts")

    _download_file(run, OutputLiterals.ARTIFACT_TYPE_CONFIG, artifacts_dir, OutputLiterals.CONFIG_FILE_NAME)
    _download_file(run, OutputLiterals.ARTIFACT_TYPE_MODEL, artifacts_dir, OutputLiterals.NER_MODEL_FILE_NAME)
    _download_file(run, OutputLiterals.ARTIFACT_TYPE_TRAINING_ARGS, artifacts_dir, OutputLiterals.TRAINING_ARGS)
    _download_file(run, OutputLiterals.ARTIFACT_TYPE_LABELS, artifacts_dir, OutputLiterals.LABELS_FILE)

    config = AutoConfig.from_pretrained(OutputLiterals.CONFIG_FILE_NAME)
    # TODO: use tokenizer config
    model_name, _ = get_model_from_language(dataset_language)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(OutputLiterals.NER_MODEL_FILE_NAME, config=config)

    _logger.info("Training artifacts restored successfully")
    return model, tokenizer, config


def score(
        run_id: str,
        input_dataset_id: str,
        ner_dir: str,
        output_dir: str,
        batch_size: int = 8
) -> None:
    """
    Generate predictions from input files.

    :param run_id: azureml run id
    :param input_dataset_id: The input dataset id.  If this is specified image_list_file is not required.
    :param ner_dir: path to data file
    :param output_dir: path to output file
    :param batch_size: batch size for prediction
    """
    _logger.info("Starting inference for run {} batch_size: {}".format(run_id, batch_size))

    _logger.info("Get run context")
    run = get_run_by_id(run_id)
    featurization = json.loads(
        run.parent.parent.properties.get("AMLSettingsJsonString"))['featurization']
    dataset_language = _get_language_code(featurization)

    # Check whether the request is from labeling service
    # Labeling service needs extra conversion on the input dataset
    run_source = run.parent.parent.properties.get(Run._RUNSOURCE_PROPERTY, None)
    is_labeling_run = True if run_source == 'Labeling' else False

    # Load training artifacts
    model, tokenizer, _ = _load_training_artifacts(run, output_dir, dataset_language)

    # Get Test Dataset object
    _logger.info("Load test dataset")
    if is_labeling_run:
        test_file, labeling_input_file_paths = load_test_dataset_for_labeling_service(
            run.experiment.workspace,
            input_dataset_id,
            ner_dir,
            DataLiterals.TEST_TEXT_FILENAME,
            DataLiterals.TEST_DATA_LABEL
        )
    else:
        test_file = download_file_dataset(
            input_dataset_id,
            DataLiterals.TEST_DATA_LABEL,
            run.experiment.workspace,
            ner_dir
        )

    # Init for NER task class, labels and metrics
    _logger.info("Initialize Trainer")
    labels = get_labels(OutputLiterals.LABELS_FILE)
    token_classification_metrics = TokenClassificationMetrics(labels)
    # from HF code - modified
    trainer = Trainer(
        model=model,
        # TODO: unable to use training_args on 'cpu' device
        # args=training_args,
        compute_metrics=token_classification_metrics.compute_metrics
    )

    with open(os.path.join(ner_dir, test_file), encoding="utf-8") as f:
        test_data = f.read()
    test_dataset = DatasetWrapper(
        data=test_data,
        tokenizer=tokenizer,
        labels=labels,
        max_seq_length=128,
        mode=Split.test
    )

    _logger.info("Run prediction")
    st = time.time()
    predictions, label_ids, metrics = trainer.predict(test_dataset)
    time_diff = time.time() - st
    if metrics:
        metrics['infer_time'] = time_diff
    preds_list, _, preds_proba_list = token_classification_metrics.align_predictions_with_proba(predictions,
                                                                                                label_ids)

    # Save predictions
    _logger.info("Save predictions")
    if trainer.is_world_process_zero():
        os.makedirs(output_dir, exist_ok=True)
        predictions_file = os.path.join(output_dir, OutputLiterals.PREDICTION_FILE_NAME)
        with open(predictions_file, "w") as writer:
            with open(os.path.join(ner_dir, test_file), "r") as f:
                write_predictions_to_file(writer, f, preds_list, preds_proba_list)
                _logger.info("Test predictions saved at location: {}".format(predictions_file))
        if is_labeling_run:
            # For labeling service, extra conversion is needed to output
            generate_results_for_labeling_service(
                output_dir, OutputLiterals.PREDICTION_FILE_NAME, labeling_input_file_paths
            )
        if metrics:
            output_test_results_file = os.path.join(output_dir, OutputLiterals.METRIC_RESULTS_FILE_NAME)
            with open(output_test_results_file, "w") as writer:
                for key, value in metrics.items():
                    _logger.info("  {} = {}".format(key, value))
                    writer.write("{} = {}\n".format(key, value))
                _logger.info("Test results saved at location: {}".format(output_test_results_file))

    return
