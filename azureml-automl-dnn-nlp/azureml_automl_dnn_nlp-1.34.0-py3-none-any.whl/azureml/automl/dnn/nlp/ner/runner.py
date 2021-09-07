# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entry script that is invoked by the driver script from automl."""

import logging
import os

from transformers import (
    AutoTokenizer
)

from azureml.core.run import Run
from azureml.train.automl.runtime._entrypoints.utils.common import parse_settings
from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals
from azureml.automl.dnn.nlp.ner.io.read.dataloader import load_dataset
from azureml.automl.dnn.nlp.ner.model_wrapper import ModelWrapper
from azureml.automl.dnn.nlp.ner.trainer import NERPytorchTrainer
from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_model_wrapper
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language
from azureml.automl.dnn.nlp.common.utils import (
    _get_language_code,
    prepare_run_properties,
    prepare_post_run_properties,
    save_script,
    save_conda_yml,
)


_logger = logging.getLogger(__name__)


def run(automl_settings):
    """Invoke training by passing settings and write the output model.

    :param automl_settings: dictionary with automl settings
    """
    # Get Run Info
    run = Run.get_context()

    # Check whether the run is for labeling service. If so, it needs extra input data conversion.
    # current run id: AutoML_<guid>_HD_0
    # parent HD run id: run.parent AutoML_<guid>_HD
    # original parent AutoML run: run.parent.parent AutoML_<guid>
    run_source = run.parent.parent.properties.get(Run._RUNSOURCE_PROPERTY, None)
    is_labeling_run = True if run_source == 'Labeling' else False

    workspace = run.experiment.workspace

    # Get dataset id
    automl_settings_obj = parse_settings(run, automl_settings)
    dataset_id = automl_settings_obj.dataset_id
    if hasattr(automl_settings_obj, "validation_dataset_id"):
        validation_dataset_id = automl_settings_obj.validation_dataset_id
    else:
        validation_dataset_id = None

    dataset_language = _get_language_code(automl_settings_obj.featurization)
    model_name, download_dir = get_model_from_language(dataset_language, need_path=True)
    # Set Defaults
    ner_dir = DataLiterals.NER_DATA_DIR
    output_dir = OutputLiterals.OUTPUT_DIR
    labels_filename = OutputLiterals.LABELS_FILE

    # set run properties
    prepare_run_properties(run, model_name)

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Save and load dataset
    train_dataset, eval_dataset, label_list = load_dataset(
        workspace,
        ner_dir,
        output_dir,
        labels_filename,
        tokenizer,
        dataset_id,
        validation_dataset_id,
        is_labeling_run
    )

    # Train model
    trainer = NERPytorchTrainer(
        label_list,
        model_name,
        download_dir,
        output_dir
    )
    trainer.train(train_dataset)
    if trainer.trainer.is_world_process_zero():
        tokenizer.save_pretrained(output_dir)

    # Validate model if validation dataset is provided
    accuracy = 0.0
    if eval_dataset:
        results = trainer.validate(eval_dataset)
        # Log results
        run.log('f1_score_micro', results['eval_f1'])
        run.log('accuracy', results['eval_accuracy'])
        accuracy = results['eval_accuracy']

    model_wrapper = ModelWrapper(trainer.trainer.model, label_list, tokenizer)
    model_path = save_model_wrapper(model_wrapper)

    # Save scoring script
    ner_write_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "io", "write")
    save_script(OutputLiterals.SCORE_SCRIPT, ner_write_dir)
    deploy_script_path = save_script(OutputLiterals.DEPLOY_SCRIPT, ner_write_dir)
    conda_file_path = save_conda_yml(run.get_environment())

    prepare_post_run_properties(run,
                                model_path,
                                2147483648,
                                conda_file_path,
                                deploy_script_path,
                                "accuracy",
                                accuracy)
