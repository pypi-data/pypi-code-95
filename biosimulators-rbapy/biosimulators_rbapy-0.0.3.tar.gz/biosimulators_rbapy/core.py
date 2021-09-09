""" BioSimulators-compliant command-line interface to the `RBApy <https://sysbioinra.github.io/RBApy/>`_ simulation program.

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-08-12
:Copyright: 2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from biosimulators_utils.combine.exec import exec_sedml_docs_in_archive
from biosimulators_utils.config import get_config, Config  # noqa: F401
from biosimulators_utils.log.data_model import CombineArchiveLog, TaskLog, StandardOutputErrorCapturerLevel  # noqa: F401
from biosimulators_utils.model_lang.rba.validation import validate_model
from biosimulators_utils.report.data_model import ReportFormat, VariableResults, SedDocumentResults  # noqa: F401
from biosimulators_utils.sedml import validation
from biosimulators_utils.sedml.data_model import (Task, ModelLanguage, ModelAttributeChange,  # noqa: F401
                                                  SteadyStateSimulation, UniformTimeCourseSimulation,
                                                  Variable, Symbol)
from biosimulators_utils.sedml.exec import exec_sed_doc as base_exec_sed_doc
from biosimulators_utils.simulator.utils import get_algorithm_substitution_policy
from biosimulators_utils.utils.core import raise_errors_warnings
from biosimulators_utils.viz.data_model import VizFormat  # noqa: F401
from biosimulators_utils.warnings import warn, BioSimulatorsWarning
from kisao.data_model import AlgorithmSubstitutionPolicy, ALGORITHM_SUBSTITUTION_POLICY_LEVELS
from kisao.utils import get_preferred_substitute_algorithm_by_ids
import numpy
import rba

__all__ = ['exec_sedml_docs_in_combine_archive', 'exec_sed_doc', 'exec_sed_task', 'preprocess_sed_task', 'modify_model']


def exec_sedml_docs_in_combine_archive(archive_filename, out_dir, config=None):
    """ Execute the SED tasks defined in a COMBINE/OMEX archive and save the outputs

    Args:
        archive_filename (:obj:`str`): path to COMBINE/OMEX archive
        out_dir (:obj:`str`): path to store the outputs of the archive

            * CSV: directory in which to save outputs to files
              ``{ out_dir }/{ relative-path-to-SED-ML-file-within-archive }/{ report.id }.csv``
            * HDF5: directory in which to save a single HDF5 file (``{ out_dir }/reports.h5``),
              with reports at keys ``{ relative-path-to-SED-ML-file-within-archive }/{ report.id }`` within the HDF5 file

        config (:obj:`Config`, optional): BioSimulators common configuration

    Returns:
        :obj:`tuple`:

            * :obj:`SedDocumentResults`: results
            * :obj:`CombineArchiveLog`: log
    """
    return exec_sedml_docs_in_archive(exec_sed_doc, archive_filename, out_dir,
                                      apply_xml_model_changes=False,
                                      config=config)


def exec_sed_doc(doc, working_dir, base_out_path, rel_out_path=None,
                 apply_xml_model_changes=False,
                 log=None, indent=0, pretty_print_modified_xml_models=False,
                 log_level=StandardOutputErrorCapturerLevel.c, config=None):
    """ Execute the tasks specified in a SED document and generate the specified outputs

    Args:
        doc (:obj:`SedDocument` or :obj:`str`): SED document or a path to SED-ML file which defines a SED document
        working_dir (:obj:`str`): working directory of the SED document (path relative to which models are located)

        base_out_path (:obj:`str`): path to store the outputs

            * CSV: directory in which to save outputs to files
              ``{base_out_path}/{rel_out_path}/{report.id}.csv``
            * HDF5: directory in which to save a single HDF5 file (``{base_out_path}/reports.h5``),
              with reports at keys ``{rel_out_path}/{report.id}`` within the HDF5 file

        rel_out_path (:obj:`str`, optional): path relative to :obj:`base_out_path` to store the outputs
        apply_xml_model_changes (:obj:`bool`, optional): if :obj:`True`, apply any model changes specified in the SED-ML file before
            calling :obj:`task_executer`.
        log (:obj:`SedDocumentLog`, optional): log of the document
        indent (:obj:`int`, optional): degree to indent status messages
        pretty_print_modified_xml_models (:obj:`bool`, optional): if :obj:`True`, pretty print modified XML models
        log_level (:obj:`StandardOutputErrorCapturerLevel`, optional): level at which to log output
        config (:obj:`Config`, optional): BioSimulators common configuration
        simulator_config (:obj:`SimulatorConfig`, optional): tellurium configuration

    Returns:
        :obj:`tuple`:

            * :obj:`ReportResults`: results of each report
            * :obj:`SedDocumentLog`: log of the document
    """
    return base_exec_sed_doc(exec_sed_task, doc, working_dir, base_out_path,
                             rel_out_path=rel_out_path,
                             apply_xml_model_changes=apply_xml_model_changes,
                             log=log,
                             indent=indent,
                             pretty_print_modified_xml_models=pretty_print_modified_xml_models,
                             log_level=log_level,
                             config=config)


def exec_sed_task(task, variables, preprocessed_task=None, log=None, config=None):
    """ Execute a task and save its results

    Args:
        task (:obj:`Task`): task
        variables (:obj:`list` of :obj:`Variable`): variables that should be recorded
        preprocessed_task (:obj:`dict`, optional): preprocessed information about the task, including possible
            model changes and variables. This can be used to avoid repeatedly executing the same initialization
            for repeated calls to this method.
        log (:obj:`TaskLog`, optional): log for the task
        config (:obj:`Config`, optional): BioSimulators common configuration

    Returns:
        :obj:`tuple`:

            :obj:`VariableResults`: results of variables
            :obj:`TaskLog`: log

    Raises:
        :obj:`NotImplementedError`:

          * Task requires a time course that RBApy doesn't support
          * Task requires an algorithm that RBApy doesn't support
    """
    config = config or get_config()

    if config.LOG and not log:
        log = TaskLog()

    if preprocessed_task is None:
        preprocessed_task = preprocess_sed_task(task, variables, config=config)

    # validate task
    model = task.model

    # read model
    rba_model = preprocessed_task['model']

    # modify model
    modify_model(rba_model, model.changes, preprocessed_task)

    # instantiate simulation
    rba_results = rba_model.solve()

    # transform simulation results
    variable_results = VariableResults()
    for variable in variables:
        variable_type, _, rba_id = variable.target.partition('.')

        if variable_type == 'objective':
            variable_results[variable.id] = numpy.array(rba_results.mu_opt)

        elif variable_type == 'variables':
            variable_results[variable.id] = numpy.array(rba_results.variables[rba_id])

        else:
            variable_results[variable.id] = numpy.array(rba_results.dual_values[rba_id])

    # log action
    if config.LOG:
        log.algorithm = preprocessed_task['algorithm_kisao_id']

        log.simulator_details = {}
        log.simulator_details['method'] = '{}.{}.{}'.format(rba_model.__module__, rba_model.__class__.__name__, rba_model.solve.__name__)
        log.simulator_details['lpSolver'] = rba_results._solver.lp_solver.name

    ############################
    # return the result of each variable and log
    return variable_results, log


def preprocess_sed_task(task, variables, config=None):
    """ Preprocess a SED task, including its possible model changes and variables. This is useful for avoiding
    repeatedly initializing tasks on repeated calls of :obj:`exec_sed_task`.

    Args:
        task (:obj:`Task`): task
        variables (:obj:`list` of :obj:`Variable`): variables that should be recorded
        config (:obj:`Config`, optional): BioSimulators common configuration

    Returns:
        :obj:`object`: preprocessed information about the task
    """
    config = config or get_config()

    # validate task
    model = task.model
    sim = task.simulation

    if config.VALIDATE_SEDML:
        raise_errors_warnings(validation.validate_task(task),
                              error_summary='Task `{}` is invalid.'.format(task.id))
        raise_errors_warnings(validation.validate_model_language(model.language, ModelLanguage.RBA),
                              error_summary='Language for model `{}` is not supported.'.format(model.id))
        raise_errors_warnings(validation.validate_model_change_types(model.changes, (ModelAttributeChange,)),
                              error_summary='Changes for model `{}` are not supported.'.format(model.id))
        raise_errors_warnings(*validation.validate_model_changes(model),
                              error_summary='Changes for model `{}` are invalid.'.format(model.id))
        raise_errors_warnings(validation.validate_simulation_type(sim, (SteadyStateSimulation, )),
                              error_summary='{} `{}` is not supported.'.format(sim.__class__.__name__, sim.id))
        raise_errors_warnings(*validation.validate_simulation(sim),
                              error_summary='Simulation `{}` is invalid.'.format(sim.id))
        raise_errors_warnings(*validation.validate_data_generator_variables(variables),
                              error_summary='Data generator variables for task `{}` are invalid.'.format(task.id))

    # read model
    errors, warnings, rba_model = validate_model(model.source, name=model.id)

    raise_errors_warnings(errors, warnings,
                          error_summary='Model `{}` is invalid.'.format(model.id),
                          warning_summary='Model `{}` may be invalid.'.format(model.id))

    # validate changes
    model_target_parameter_map = {}
    for function in rba_model.parameters.functions:
        for parameter in function.parameters:
            target = 'parameters.functions.{}.parameters.{}'.format(function.id, parameter.id)
            model_target_parameter_map[target] = parameter

    invalid_changes = []
    for i_change, change in enumerate(model.changes):
        parameter = model_target_parameter_map.get(change.target, None)
        if parameter is None:
            invalid_changes.append('{}: {}'.format(i_change + 1, change.target))

    if invalid_changes:
        raise ValueError('The following changes are not valid:\n  - {}'.format('\n  - '.join(sorted(invalid_changes))))

    # validate variables
    constraint_matrix = rba.ConstraintMatrix(rba_model)

    valid_targets = ['objective']

    for name in constraint_matrix.col_names:
        valid_targets.append('variables.' + name)

    for name in constraint_matrix.row_names:
        valid_targets.append('constraints.' + name)

    invalid_variables = []
    for variable in variables:
        if variable.symbol:
            invalid_variables.append('{}: symbol: {}'.format(variable.id, variable.symbol))

        else:
            if variable.target not in valid_targets:
                invalid_variables.append('{}: target: {}'.format(variable.id, variable.target))

    if invalid_variables:
        msg = (
            'The following variables are not supported:\n  - {}'
            '\n'
            '\n'
            'Only following variable targets are supported:\n  - {}'
        ).format(
            '\n  - '.join(sorted(invalid_variables)),
            '\n  - '.join(sorted(valid_targets)),
        )
        raise ValueError(msg)

    # configure simulation algorithm
    algorithm_substitution_policy = get_algorithm_substitution_policy(config=config)
    exec_kisao_id = get_preferred_substitute_algorithm_by_ids(
        sim.algorithm.kisao_id, ['KISAO_0000669'],
        substitution_policy=algorithm_substitution_policy)

    # configure parameters of the simulation algorithm
    if sim.algorithm.changes:
        if (
            ALGORITHM_SUBSTITUTION_POLICY_LEVELS[algorithm_substitution_policy]
            <= ALGORITHM_SUBSTITUTION_POLICY_LEVELS[AlgorithmSubstitutionPolicy.NONE]
        ):
            msg = 'No algorithm parameters are supported.'
            raise ValueError(msg)
        else:
            msg = "Algorithm changes were ignored because no algorithm parameters are supported."
            warn(msg, BioSimulatorsWarning)

    ############################
    # processed task
    return {
        'model': rba_model,
        'model_target_parameter_map': model_target_parameter_map,
        'algorithm_kisao_id': exec_kisao_id,
    }


def modify_model(model, changes, preprocessed_task):
    """ Modify a model

    Args:
        model (:obj:`rba.model.RbaModel`): RBA model
        changes (:obj:`list` of :obj:`ModelAttributeChange`): changes to apply to the model
        preprocessed_task (:obj:`dict`): preprocessed informationa about the model
    """
    rba_model_target_parameter_map = preprocessed_task['model_target_parameter_map']
    for change in changes:
        parameter = rba_model_target_parameter_map[change.target]
        parameter.value = float(change.new_value)
