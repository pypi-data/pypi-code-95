import os
from collections import namedtuple
import multiprocessing
from multiprocessing import Pool#,# set_start_method
from pathlib import Path

# set_start_method("fork")

import numpy as np
from openeye import oechem, oeomega, oeshape, oequacpac

from reinvent_scoring.scoring.component_parameters import ComponentParameters
from reinvent_scoring.scoring.score_components.standard.base_rocs_component import BaseROCSComponent
from reinvent_scoring.scoring.enums import ROCSSimilarityMeasuresEnum
from reinvent_scoring.scoring.enums import ROCSInputFileTypesEnum
from reinvent_scoring.scoring.enums import ROCSSpecificParametersEnum

NUM_PROCS = multiprocessing.cpu_count()
_SIM_FUNC = namedtuple('_SIM_FUNC', ['shape', 'color', 'predicate'])
# only way for this namedtuple to be pickled is 1. to have it global and 2. use the same name for variable
# and description (i.e. _SIM_FUNC)
prep = oeshape.OEOverlapPrep()


class ParallelRocsSimilarity(BaseROCSComponent):
    def __init__(self, parameters: ComponentParameters):
        super().__init__(parameters)
        self.sim_measure_enum = ROCSSimilarityMeasuresEnum()
        self.input_types_enum = ROCSInputFileTypesEnum()
        self.param_names_enum = ROCSSpecificParametersEnum()
        self.num_cpus = min(NUM_PROCS, self.parameters.specific_parameters.get(self.param_names_enum.MAX_CPUS, 4))
        self.save_overlays = self.parameters.specific_parameters.get(self.param_names_enum.SAVE_ROCS_OVERLAYS, False)
        self.id = 0
        self.enum_stereo = self.parameters.specific_parameters.get(self.param_names_enum.ENUM_STEREO, False)
        self.max_stereo = self.parameters.specific_parameters.get(self.param_names_enum.MAX_STEREO, 0)
        if self.max_stereo == 0:
            self.enum_stereo = False
        if self.save_overlays:
            try:
                self.dir_name = self.parameters.specific_parameters[self.param_names_enum.ROCS_OVERLAYS_DIR]
            except KeyError:
                raise KeyError("No name for ROCS overlay directory given!")
            try:
                self.overlay_prefix = self.parameters.specific_parameters[self.param_names_enum.ROCS_OVERLAYS_PREFIX]

            except KeyError:
                raise KeyError("No name for ROCS overlay files prefix given!")
            Path(self.dir_name).mkdir(parents=True, exist_ok=True)
        self.file_path = self.parameters.specific_parameters[self.param_names_enum.ROCS_INPUT]
        self.file_type = self.parameters.specific_parameters[self.param_names_enum.INPUT_TYPE]
        self.cff_path = self.parameters.specific_parameters.get(self.param_names_enum.CUSTOM_CFF, None)
        self.shape_weight = self.parameters.specific_parameters[self.param_names_enum.SHAPE_WEIGHT]
        self.color_weight = self.parameters.specific_parameters[self.param_names_enum.COLOR_WEIGHT]
        self.sim_func_name_set = self.__get_similarity_name_set()
        self.setup_omega()
        oechem.OEThrow.SetLevel(10000)

    def _calculate_omega_score(self, smiles) -> np.array:
        inputs = []
        if len(smiles) == 0:
            return np.array(())
        self.__prepare_overlay()
        if self.save_overlays:
            self._assign_id()
        ind = str(self.id).zfill(4)

        for smile in smiles:
            input = {"smile": smile, "shape_weight": self.shape_weight, "color_weight": self.color_weight,
                     "sim_func_name_set": self.sim_func_name_set, "batch_id": ind,
                     "enum_stereo": self.enum_stereo, "max_stereo": self.max_stereo, "save_overlays": self.save_overlays
                     }
            inputs.append(input)
        with Pool(processes=min(self.num_cpus, len(inputs))) as pool:
            results = pool.map(self._unfold, inputs)
        scores = []
        if self.save_overlays:
            overlay_filename = self.overlay_prefix + ind + ".sdf"
            overlay_file_path = os.path.join(self.dir_name, overlay_filename)
            outfs = oechem.oemolostream(overlay_file_path)
        for result in results:
            score, outmol = result
            scores.append(score)
            if self.save_overlays:
                oechem.OEWriteMolecule(outfs, outmol)
        return np.array(scores)

    def __get_similarity_name_set(self):
        similarity_collection_name = self.parameters.specific_parameters.get(self.param_names_enum.SIM_MEASURE,
                                                                             self.sim_measure_enum.TANIMOTO)
        return self.__similarity_collection(similarity_collection_name)

    def __similarity_collection(self, sim_measure_type):
        _SIM_DEF_DICT = {
            self.sim_measure_enum.TANIMOTO: _SIM_FUNC('GetTanimoto', 'GetColorTanimoto', 'OEHighestTanimotoCombo'),
            self.sim_measure_enum.REF_TVERSKY: _SIM_FUNC('GetRefTversky', 'GetRefColorTversky',
                                                         'OEHighestRefTverskyCombo'),
            self.sim_measure_enum.FIT_TVERSKY: _SIM_FUNC('GetFitTversky', 'GetFitColorTversky',
                                                         'OEHighestFitTverskyCombo'),
        }
        return _SIM_DEF_DICT.get(sim_measure_type)

    def __prepare_overlay(self):
        overlay_function_types = {
            self.input_types_enum.SHAPE_QUERY: self.setup_reference_molecule_with_shape_query,
            self.input_types_enum.SDF_QUERY: self.setup_reference_molecule
        }
        overlay_function = overlay_function_types.get(self.file_type)
        overlay_function(self.file_path, self.cff_path)

    def _unfold(self, args):
        return self.parallel_scoring(**args)

    @classmethod
    def setup_reference_molecule_with_shape_query(cls, shape_query, cff_path):
        if cff_path is not None:
            cff = oeshape.OEColorForceField()
            if cff.Init(cff_path):
                prep.SetColorForceField(cff)
            else:
                raise ValueError("Custom color force field initialisation failed")
        qry = oeshape.OEShapeQuery()
        cls.rocs_overlay = oeshape.OEOverlay()
        if oeshape.OEReadShapeQuery(shape_query, qry):
            cls.rocs_overlay.SetupRef(qry)
        else:
            raise FileNotFoundError("A ROCS shape query file was not found")

    @classmethod
    def setup_reference_molecule(cls, file_path, cff_path):
        input_stream = oechem.oemolistream()
        input_stream.SetFormat(oechem.OEFormat_SDF)
        input_stream.SetConfTest(oechem.OEAbsoluteConfTest(compTitles=False))
        refmol = oechem.OEMol()
        if cff_path is None:
            cff_path = oeshape.OEColorFFType_ImplicitMillsDean
        if input_stream.open(file_path):
            oechem.OEReadMolecule(input_stream, refmol)
        else:
            raise FileNotFoundError("A ROCS reference sdf file was not found")
        cff = oeshape.OEColorForceField()
        if cff.Init(cff_path):
            prep.SetColorForceField(cff)
        prep.Prep(refmol)
        cls.rocs_overlay = oeshape.OEMultiRefOverlay()
        cls.rocs_overlay.SetupRef(refmol)

    @classmethod
    def setup_omega(cls):
        omegaOpts = oeomega.OEOmegaOptions()
        omegaOpts.SetStrictStereo(False)
        cls.omega = oeomega.OEOmega(omegaOpts)
        return cls.omega

    @classmethod
    def parallel_scoring(cls, smile, shape_weight, color_weight, sim_func_name_set, batch_id, enum_stereo=False,
                         max_stereo=0, save_overlays=False):
        predicate = getattr(oeshape, sim_func_name_set.predicate)()
        imol = oechem.OEMol()
        outmol = oechem.OEMol()
        best_score = 0.0
        stereo = False
        no_stereo = False
        if oechem.OESmilesToMol(imol, smile):
            oequacpac.OEGetReasonableProtomer(imol)
            if enum_stereo:
                enantiomers = oeomega.OEFlipper(imol.GetActive(), max_stereo, False, True)
                imol.DeleteConfs()
                for enantiomer in enantiomers:
                    enantiomer = oechem.OEMol(enantiomer)
                    ret_code = cls.omega.Build(enantiomer)
                    if ret_code == oeomega.OEOmegaReturnCode_Success:
                        stereo = True
                        for x in enantiomer.GetConfs():
                            imol.NewConf(x)
            else:
                no_stereo = cls.omega(imol)

            if no_stereo or stereo:
                prep.Prep(imol)
                score = oeshape.OEBestOverlayScore()
                cls.rocs_overlay.BestOverlay(score, imol, predicate)
                if save_overlays:
                    outmol = oechem.OEGraphMol(imol.GetConf(oechem.OEHasConfIdx(score.GetFitConfIdx())))
                best_score_shape = getattr(score, sim_func_name_set.shape)()
                best_score_shape = correct_color_score(best_score_shape)
                best_score_color = getattr(score, sim_func_name_set.color)()
                best_score_color = correct_color_score(best_score_color)
                best_score = ((shape_weight * best_score_shape) + (
                        color_weight * best_score_color)) / (shape_weight + color_weight)
                if save_overlays:
                    score.Transform(outmol)
                    oechem.OESetSDData(outmol, "Batch ID", batch_id)
                    oechem.OESetSDData(outmol, "Smiles", smile)
                    oechem.OESetSDData(outmol, "Shape", "%-.3f" % best_score_shape)
                    oechem.OESetSDData(outmol, "Color", "%-.3f" % best_score_color)
        return best_score, outmol


def correct_color_score(score):
    if score >= 1.0:
        score = 0.90  # or alternative
    return score


def correct_shape_score(score):
    if score >= 1.0:
        score = 0.95  # or alternative
    return score
