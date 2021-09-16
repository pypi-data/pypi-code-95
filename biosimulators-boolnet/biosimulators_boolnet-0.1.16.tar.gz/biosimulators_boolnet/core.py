""" BioSimulators-compliant command-line interface to the `BoolNet <https://sysbio.uni-ulm.de/?Software:BoolNet>`_ simulation program.

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-01-05
:Copyright: 2020-2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from .data_model import KISAO_METHOD_ARGUMENTS_MAP
from .utils import (validate_time_course, validate_data_generator_variables, get_variable_target_x_path_keys,
                    get_boolnet, set_simulation_method_arg, get_variable_results)
from biosimulators_utils.combine.exec import exec_sedml_docs_in_archive
from biosimulators_utils.config import get_config, Config  # noqa: F401
from biosimulators_utils.log.data_model import CombineArchiveLog, TaskLog, StandardOutputErrorCapturerLevel  # noqa: F401
from biosimulators_utils.viz.data_model import VizFormat  # noqa: F401
from biosimulators_utils.report.data_model import ReportFormat, VariableResults, SedDocumentResults  # noqa: F401
from biosimulators_utils.sedml import validation
from biosimulators_utils.sedml.data_model import (Task, ModelLanguage, ModelAttributeChange,  # noqa: F401
                                                  AddElementModelChange, RemoveElementModelChange, ReplaceElementModelChange,
                                                  UniformTimeCourseSimulation, Variable)
from biosimulators_utils.sedml.exec import exec_sed_doc as base_exec_sed_doc
from biosimulators_utils.sedml.utils import apply_changes_to_xml_model
from biosimulators_utils.simulator.utils import get_algorithm_substitution_policy
from biosimulators_utils.utils.core import raise_errors_warnings
from biosimulators_utils.warnings import warn, BioSimulatorsWarning
from kisao.data_model import AlgorithmSubstitutionPolicy, ALGORITHM_SUBSTITUTION_POLICY_LEVELS
from kisao.utils import get_preferred_substitute_algorithm_by_ids
from rpy2.robjects.vectors import StrVector
import copy
import lxml.etree
import numpy
import os
import tempfile

__all__ = ['exec_sedml_docs_in_combine_archive', 'exec_sed_doc', 'exec_sed_task', 'preprocess_sed_task']


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
                                      apply_xml_model_changes=True,
                                      config=config)


def exec_sed_doc(doc, working_dir, base_out_path, rel_out_path=None,
                 apply_xml_model_changes=True,
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
        preprocessed_task (:obj:`object`, optional): preprocessed information about the task, including possible
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

          * Task requires a time course that BoolNet doesn't support
          * Task requires an algorithm that BoolNet doesn't support
    """
    config = config or get_config()

    if config.LOG and not log:
        log = TaskLog()

    if preprocessed_task is None:
        preprocessed_task = preprocess_sed_task(task, variables, config=config)

    model = task.model
    sim = task.simulation

    # read model
    boolnet_model = preprocessed_task['model']['model']

    # modify model
    if model.changes:
        raise_errors_warnings(validation.validate_model_change_types(
            model.changes,
            (ModelAttributeChange, AddElementModelChange, RemoveElementModelChange, ReplaceElementModelChange)),
            error_summary='Changes for model `{}` are not supported.'.format(model.id))

        model_etree = preprocessed_task['model']['model_etree']

        model = copy.deepcopy(model)
        for change in model.changes:
            if isinstance(change, ModelAttributeChange):
                change.new_value = str(change.new_value)

        apply_changes_to_xml_model(model, model_etree, sed_doc=None, working_dir=None)

        model_file, model_filename = tempfile.mkstemp(suffix='.xml')
        os.close(model_file)

        model_etree.write(model_filename,
                          xml_declaration=True,
                          encoding="utf-8",
                          standalone=False,
                          pretty_print=False)

        boolnet_model = preprocessed_task['boolnet'].loadSBML(StrVector([model_filename]))

        os.remove(model_filename)

    # initialize arguments for BoolNet's time course simulation method
    simulation_method_args = preprocessed_task['simulation']['method_args']
    simulation_method_args['numMeasurements'] = int(sim.number_of_points) + 1

    # execute simulation
    species_results_matrix = preprocessed_task['boolnet'].generateTimeSeries(boolnet_model, **simulation_method_args)[0]
    species_results_dict = {}
    for i_species, species_id in enumerate(species_results_matrix.rownames):
        species_results_dict[species_id] = numpy.array(species_results_matrix.rx(i_species + 1, True))

    # get the results in BioSimulator's format
    variable_target_sbml_id_map = preprocessed_task['model']['variable_target_sbml_id_map']
    variable_results = get_variable_results(sim, variables, variable_target_sbml_id_map, species_results_dict)
    for variable in variables:
        variable_results[variable.id] = variable_results[variable.id][-(int(sim.number_of_points) + 1):]

    # log action
    if config.LOG:
        log.algorithm = preprocessed_task['simulation']['algorithm_kisao_id']
        log.simulator_details = {
            'method': 'BoolNet::generateTimeSeries',
            'arguments': copy.copy(simulation_method_args),
        }
        log.simulator_details['arguments']['type'] = preprocessed_task['simulation']['algorithm_type']

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
        raise_errors_warnings(validation.validate_model_language(model.language, ModelLanguage.SBML),
                              error_summary='Language for model `{}` is not supported.'.format(model.id))
        raise_errors_warnings(validation.validate_model_change_types(
            model.changes,
            (ModelAttributeChange, AddElementModelChange, RemoveElementModelChange, ReplaceElementModelChange)),
            error_summary='Changes for model `{}` are not supported.'.format(model.id))
        raise_errors_warnings(*validation.validate_model_changes(model),
                              error_summary='Changes for model `{}` are invalid.'.format(model.id))
        raise_errors_warnings(validation.validate_simulation_type(sim, (UniformTimeCourseSimulation, )),
                              error_summary='{} `{}` is not supported.'.format(sim.__class__.__name__, sim.id))
        raise_errors_warnings(*validation.validate_simulation(sim),
                              error_summary='Simulation `{}` is invalid.'.format(sim.id))
        raise_errors_warnings(validate_time_course(sim),
                              error_summary='Simulation `{}` is invalid.'.format(sim.id))
        raise_errors_warnings(*validation.validate_data_generator_variables(variables),
                              error_summary='Data generator variables for task `{}` are invalid.'.format(task.id))

    model_etree = lxml.etree.parse(model.source)
    variable_target_sbml_id_map = get_variable_target_x_path_keys(variables, model_etree)

    # validate model
    if config.VALIDATE_SEDML_MODELS:
        raise_errors_warnings(*validation.validate_model(model, [], working_dir='.'),
                              error_summary='Model `{}` is invalid.'.format(model.id),
                              warning_summary='Model `{}` may be invalid.'.format(model.id))

    # get BoolNet
    boolnet = get_boolnet()

    # read model
    boolnet_model = boolnet.loadSBML(StrVector([model.source]))

    # Load the algorithm specified by :obj:`task.simulation.algorithm.kisao_id`
    alg_kisao_id = sim.algorithm.kisao_id
    algorithm_substitution_policy = get_algorithm_substitution_policy(config=config)
    exec_kisao_id = get_preferred_substitute_algorithm_by_ids(
        alg_kisao_id, KISAO_METHOD_ARGUMENTS_MAP.keys(),
        substitution_policy=algorithm_substitution_policy)
    alg = KISAO_METHOD_ARGUMENTS_MAP[exec_kisao_id]
    alg_type = alg['type']

    simulation_method_args = {
        'numMeasurements': int(sim.number_of_points) + 1,
        'numSeries': 1,
        'perturbations': 0,
        'type': StrVector([alg_type]),
    }

    # Apply the algorithm parameter changes specified by `simulation.algorithm.parameter_changes`
    if exec_kisao_id == alg_kisao_id:
        for change in sim.algorithm.changes:
            try:
                set_simulation_method_arg(boolnet_model, exec_kisao_id, change, simulation_method_args)
            except NotImplementedError as exception:
                if (
                    ALGORITHM_SUBSTITUTION_POLICY_LEVELS[algorithm_substitution_policy]
                    > ALGORITHM_SUBSTITUTION_POLICY_LEVELS[AlgorithmSubstitutionPolicy.NONE]
                ):
                    warn('Unsuported algorithm parameter `{}` was ignored:\n  {}'.format(
                        change.kisao_id, str(exception).replace('\n', '\n  ')),
                        BioSimulatorsWarning)
                else:
                    raise
            except ValueError as exception:
                if (
                    ALGORITHM_SUBSTITUTION_POLICY_LEVELS[algorithm_substitution_policy]
                    > ALGORITHM_SUBSTITUTION_POLICY_LEVELS[AlgorithmSubstitutionPolicy.NONE]
                ):
                    warn('Unsuported value `{}` for algorithm parameter `{}` was ignored:\n  {}'.format(
                        change.new_value, change.kisao_id, str(exception).replace('\n', '\n  ')),
                        BioSimulatorsWarning)
                else:
                    raise

    # validate that BoolNet can produce the desired variables of the desired data generators
    validate_data_generator_variables(variables, exec_kisao_id)

    # return preprocessed information
    return {
        'boolnet': boolnet,
        'model': {
            'model': boolnet_model,
            'model_etree': model_etree,
            'variable_target_sbml_id_map': variable_target_sbml_id_map,
        },
        'simulation': {
            'method_args': simulation_method_args,
            'algorithm_kisao_id': exec_kisao_id,
            'algorithm_type': alg_type,
        }
    }
