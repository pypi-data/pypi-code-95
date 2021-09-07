# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entry script that is invoked by the driver script from automl."""
import os

from azureml._common._error_definition import AzureMLError
from azureml.core.run import Run
from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_model_wrapper
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExecutionFailure
from azureml.automl.core.shared.constants import Metric
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.classification.io.read import dataloader
from azureml.automl.dnn.nlp.classification.multiclass.model_wrapper import ModelWrapper
from azureml.automl.dnn.nlp.classification.multiclass.trainer import TextClassificationTrainer
from azureml.automl.dnn.nlp.classification.multiclass.utils import compute_metrics
from azureml.automl.dnn.nlp.common.constants import TaskNames, OutputLiterals
from azureml.automl.dnn.nlp.common.utils import (
    _get_language_code,
    prepare_run_properties,
    prepare_post_run_properties,
    save_script,
    save_conda_yml
)
from azureml.train.automl.runtime._entrypoints.utils.common import parse_settings


def run(automl_settings):
    """Invoke training by passing settings and write the output model.
    :param automl_settings: dictionary with automl settings
    """
    run = Run.get_context()
    workspace = run.experiment.workspace

    automl_settings_obj = parse_settings(run, automl_settings)  # Parse settings internally initializes logger

    dataset_id = automl_settings_obj.dataset_id
    if hasattr(automl_settings_obj, "validation_dataset_id"):
        validation_dataset_id = automl_settings_obj.validation_dataset_id
    else:
        validation_dataset_id = None

    dataset_language = _get_language_code(automl_settings_obj.featurization)
    label_column_name = automl_settings_obj.label_column_name
    if label_column_name is None:
        raise ValidationException._with_error(
            AzureMLError.create(
                ExecutionFailure,
                error_details="Need to pass in label_column_name argument for training"
            )
        )

    training_set, validation_set, label_list, train_label_list, y_val = dataloader.multiclass_dataset_loader(
        dataset_id, validation_dataset_id, label_column_name, workspace, dataset_language)

    trainer_class = TextClassificationTrainer(train_label_list, dataset_language)
    prepare_run_properties(run, trainer_class.model_name_or_path)
    trainer_class.train(training_set)
    accuracy = 0.0
    if validation_set is not None:
        val_predictions = trainer_class.validate(validation_set)
        results = compute_metrics(y_val, val_predictions, label_list, train_label_list)
        accuracy = results[Metric.Accuracy]
        for key in results:
            if key in Metric.SCALAR_CLASSIFICATION_SET:
                run.log(key, results[key])

    model_wrapper = ModelWrapper(trainer_class.trainer.model, train_label_list, dataset_language)
    model_path = save_model_wrapper(model_wrapper)

    multiclass_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "io", "write", TaskNames.MULTICLASS)
    save_script(OutputLiterals.SCORE_SCRIPT, multiclass_directory)
    deploy_script_path = save_script(OutputLiterals.DEPLOY_SCRIPT, multiclass_directory)
    conda_file_path = save_conda_yml(run.get_environment())

    # 2147483648 is 2 GB of memory
    prepare_post_run_properties(run,
                                model_path,
                                2147483648,
                                conda_file_path,
                                deploy_script_path,
                                Metric.Accuracy,
                                accuracy)
