"""
Optimization
------------
The ``maica.util.optimization`` module supports the function optimization.
It includes various meta-heuristic algorithms and a wrapper function to execute them.
This module can be used to optimize the input data of user-defined functions or machine learning models.
"""


import numpy
import torch
from mealpy.evolutionary_based.EP import BaseEP
from mealpy.evolutionary_based.ES import BaseES
from mealpy.evolutionary_based.MA import BaseMA
from mealpy.evolutionary_based.GA import BaseGA
from mealpy.evolutionary_based.DE import BaseDE
from mealpy.evolutionary_based.FPA import BaseFPA
from mealpy.evolutionary_based.CRO import BaseCRO
from mealpy.swarm_based.PSO import BasePSO
from mealpy.swarm_based.BFO import BaseBFO
from mealpy.swarm_based.BeesA import BaseBeesA
from mealpy.swarm_based.CSO import BaseCSO
from mealpy.swarm_based.ACOR import BaseACOR
from mealpy.swarm_based.ABC import BaseABC
from mealpy.swarm_based.CSA import BaseCSA
from mealpy.swarm_based.FireflyA import BaseFireflyA
from mealpy.swarm_based.FA import BaseFA
from mealpy.swarm_based.BA import BaseBA
from mealpy.swarm_based.FOA import BaseFOA
from mealpy.swarm_based.SSO import BaseSSO
from mealpy.swarm_based.GWO import BaseGWO
from mealpy.swarm_based.SSA import BaseSSA
from mealpy.swarm_based.ALO import BaseALO
from mealpy.swarm_based.MFO import BaseMFO
from mealpy.swarm_based.EHO import BaseEHO
from mealpy.swarm_based.JA import BaseJA
from mealpy.swarm_based.WOA import BaseWOA
from mealpy.swarm_based.DO import BaseDO
from mealpy.swarm_based.BSA import BaseBSA
from mealpy.swarm_based.SHO import BaseSHO
from mealpy.swarm_based.SalpSO import BaseSalpSO
from mealpy.swarm_based.SRSR import BaseSRSR
from mealpy.swarm_based.GOA import BaseGOA
from mealpy.swarm_based.MSA import BaseMSA
from mealpy.swarm_based.NMRA import ImprovedNMR
from mealpy.swarm_based.BES import BaseBES
from mealpy.swarm_based.PFA import ImprovedPFA
from mealpy.swarm_based.SFO import ImprovedSFO
from mealpy.swarm_based.HHO import BaseHHO
from mealpy.swarm_based.MRFO import BaseMRFO
from mealpy.swarm_based.SpaSA import BaseSpaSA
from mealpy.swarm_based.HGS import OriginalHGS
from mealpy.physics_based.SA import BaseSA
from mealpy.physics_based.WDO import BaseWDO
from mealpy.physics_based.MVO import BaseMVO
from mealpy.physics_based.TWO import ImprovedTWO
from mealpy.physics_based.EFO import BaseEFO
from mealpy.physics_based.NRO import BaseNRO
from mealpy.physics_based.HGSO import BaseHGSO
from mealpy.physics_based.ASO import BaseASO
from mealpy.physics_based.EO import BaseEO
from mealpy.human_based.CA import OriginalCA
from mealpy.human_based.ICA import BaseICA
from mealpy.human_based.TLO import BaseTLO
from mealpy.human_based.BSO import BaseBSO
from mealpy.human_based.QSA import BaseQSA
from mealpy.human_based.SARO import BaseSARO
from mealpy.human_based.LCBO import BaseLCBO
from mealpy.human_based.SSDO import BaseSSDO
from mealpy.human_based.GSKA import BaseGSKA
from mealpy.human_based.CHIO import BaseCHIO
from mealpy.human_based.FBIO import BaseFBIO
from mealpy.human_based.BRO import BaseBRO
from mealpy.bio_based.IWO import BaseIWO
from mealpy.bio_based.BBO import BaseBBO
from mealpy.bio_based.VCS import BaseVCS
from mealpy.bio_based.SBO import BaseSBO
from mealpy.bio_based.EOA import BaseEOA
from mealpy.bio_based.WHO import BaseWHO
from mealpy.bio_based.SMA import BaseSMA
from mealpy.system_based.GCO import BaseGCO
from mealpy.system_based.WCA import BaseWCA
from mealpy.system_based.AEO import BaseAEO
from mealpy.math_based.HC import BaseHC
from mealpy.math_based.SCA import BaseSCA
from mealpy.music_based.HS import BaseHS
from mealpy.probabilistic_based.CEM import BaseCEM
from mealpy.dummy.PIO import BasePIO
from mealpy.dummy.AAA import BaseAAA
from mealpy.dummy.RHO import BaseRHO
from mealpy.dummy.EPO import BaseEPO
from mealpy.dummy.BOA import BaseBOA
from mealpy.dummy.BMO import BaseBMO
from mealpy.dummy.SOA import BaseSOA
from mealpy.dummy.BWO import BaseBWO
from maica.ml.base import Model
from maica.core.env import *


def optimize(obj_func: object,
             opt_alg: str,
             opt_type: str,
             return_hist: bool = None,
             **kwargs):
    """
    Optimize the given user-defined function ``obj_func`` using the meta-heuristic algorithm ``opt_alg`` in ARTCAI.
    The objective function can be all input-output mappings regardless of their differentiability.

    :param obj_func: (*object*) The objective function to optimize.
    :param opt_alg: (*str*) A name of the meta-heuristic algorithm to optimize the objective function.
    :param opt_type: (*str*) An argument for determining the objective function to be minimized or maximized.
    :param return_hist: (*bool*) Return the optimized inputs over the iterations (*default* = ``None``).
    :param kwargs: (*optional*) Hyperparameters of the meta-heuristic algorithm.
    :return: Optimal input of the objective function and its score in the meta-heuristic algorithm.
    """

    if opt_type == PROB_MIN:
        # Objective function for minimization problem.
        __obj_func = obj_func
    elif opt_type == PROB_MAX:
        # Negative objective function for maximization problem.
        def __obj_func(x: numpy.ndarray):
            return -obj_func(x)
    else:
        raise AssertionError('Unknown optimization type is given: {}.'.format(opt_type))

    if opt_alg == OPT_EP:
        optimizer = BaseEP(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_ES:
        optimizer = BaseES(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_MA:
        optimizer = BaseMA(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_GA:
        optimizer = BaseGA(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_DE:
        optimizer = BaseDE(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_FPA:
        optimizer = BaseFPA(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_CRO:
        optimizer = BaseCRO(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_PSO:
        optimizer = BasePSO(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_BFO:
        optimizer = BaseBFO(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_BEES:
        optimizer = BaseBeesA(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_CSO:
        optimizer = BaseCSO(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_ACO:
        optimizer = BaseACOR(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_ABC:
        optimizer = BaseABC(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_CSA:
        optimizer = BaseCSA(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_FFA:
        optimizer = BaseFireflyA(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_FA:
        optimizer = BaseFA(obj_func=obj_func, **kwargs)
    elif opt_alg == OPT_BA:
        optimizer = BaseBA(obj_func=obj_func, **kwargs)

    best_sol, best_score, _ = optimizer.train()

    if return_hist:
        return best_sol, best_score, optimizer.hist
    else:
        return best_sol, best_score


def run_ml_model(model: Model,
                 input_data: numpy.ndarray):
    """
    Run the given machine learning model of ``model`` to generate model outputs.
    It is a wrapper function to use the machine learning models as an objective function of meta-heuristics.

    :param model: (*maica.ml.base.Model*) A machine learning model that makes up the objective function.
    :param input_data: (*numpy.ndarray*) Input data of the given machine learning model.
    :return: Output data of the machine learning model.
    """

    if model.alg_type == ALG_SKLEARN:
        return model.predict(input_data.reshape(1, -1))
    elif model.alg_type == ALG_PYTORCH:
        return model(torch.tensor(input_data, dtype=torch.float).view(1, -1))
    else:
        raise AssertionError('Unknown algorithm is given: {}.'.format(model.alg_type))
