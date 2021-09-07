# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Code gen related utility methods."""


import logging

from azureml.core import Run
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared import logging_utilities
from azureml.train.automl._constants_azureml import RunState
from azureml.train.automl.runtime._code_generation import code_generator, notebook_generator
from azureml.train.automl.runtime._code_generation.constants import CodeGenConstants


logger = logging.getLogger(__name__)


def generate_model_code_and_notebook(current_run: Run) -> None:
    """
    Given a child run, generate the code and notebook for the outputted model and upload them as artifacts.
    """
    try:
        logger.info('Generating code for the trained model.')
        code = code_generator.generate_full_script(current_run)

        with open('script.py', 'w') as f:
            f.write(code)

        current_run.upload_file(CodeGenConstants.ScriptOutputPath, 'script.py')
        logger.info('Script has been generated, output saved to {}'.format(CodeGenConstants.ScriptOutputPath))

        notebook = notebook_generator.generate_script_run_notebook(
            current_run._experiment, environment=current_run.get_environment()
        )
        with open('script_run_notebook.ipynb', 'w') as f:
            f.write(notebook)
        current_run.upload_file(CodeGenConstants.ScriptRunNotebookOutputPath, 'script_run_notebook.ipynb')
        logger.info('Script has been generated, output saved to {}'.format(
            CodeGenConstants.ScriptRunNotebookOutputPath))

        try:
            # Quickly check for errors in the script
            _codegen_utilities.check_code_syntax(code)
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            logger.warning("Code generation encountered an error when checking output. The generated code may "
                           "require some manual editing to work properly.")

        current_run.set_tags({CodeGenConstants.TagName: RunState.COMPLETE_RUN})
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        logger.warning('Code generation failed; skipping.')
        current_run.set_tags({CodeGenConstants.TagName: RunState.FAIL_RUN})
