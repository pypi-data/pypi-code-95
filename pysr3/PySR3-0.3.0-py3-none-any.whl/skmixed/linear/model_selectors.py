"""
Black-box routines for automatic feature selection for mixed-models.
"""
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import yaml

from pysr3.linear.models import LinearL1Model, LinearCADModel, LinearSCADModel
from pysr3.linear.models import LinearL1ModelSR3, LinearCADModelSR3, LinearSCADModelSR3
from pysr3.linear.problems import LinearProblem

MODELS_NAMES = ("L0", "L1", "CAD", "SCAD", "L0_SR3", "L1_SR3", "CAD_SR3", "SCAD_SR3")


class CovariatesSelector:

    def __init__(self, model_name, parameters=None):
        self.model_name = model_name
        self.parameters = parameters
        self.log = None

    def run_selection(self, x, y, display_progress=True):

        log = pd.DataFrame(columns=("i", "var", "model", "time", "mse", "evar", "loss",
                                    "tp", "tn", "fp", "fn", "number_of_iterations", "converged"))

        problem = LinearProblem(a=x, b=y)

        model_constructor, search_grid = get_model(self.model_name, self.parameters, self.problem)

        if display_progress:
            from tqdm import tqdm
            search_grid = tqdm(search_grid)

        for params in search_grid:
            model = model_constructor(params)
            tic = time.perf_counter()
            model.fit_problem(problem)
            toc = time.perf_counter()
            y_pred = model.predict_problem(problem)
            results = {
                "params": params,
                "model": self.model_name,
                "time": toc - tic,
                "mse": np.linalg.norm(y - y_pred)**2,
                "loss": model.logger_.get("loss")[-1],
                "aic": model.aic(),
                "bic": model.bic(),
                "number_of_iterations": len(model.logger_.get("loss")),
            }
            log = log.append(results, ignore_index=True)

        self.log = log

    def get_best_parameters(self, criterion="bic"):
        pgd_argmin = pgd_data[ic].argmin()

def select_covariates(x,
                      y,
                      se = None,
                      output_folder: Union[str, Path] = ".",
                      model: str = "L1_SR3",
                      **kwargs) -> None:
    """Implements a black-box functionality for selecting most important fixed and random features
    in Linear Mixed-Effect Models.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame contains all the necessary columns.
    target : str
        Column name of observation.
    se : str
        Column name of the observation standard error
    group : str
        Column name of the group, usually specified as `study_id`.
    covs : Optional[Dict[str, List[str]]]
        Dictionary contains all the covariate candidates. Keys of the dictionary
        are `fixed_effects` and `random_effects`, and corresponding value is a
        list of covariate names which can be empty. Default to `None`, and when
        `covs` is None, it will be automatically parsed as Dictionary with empty
        list as values.
    pre_sel_covs : Optional[Dict[str, List[str]]]
        Same structure with `covs`. Default to `None`.
    output_folder : Union[str, Path]
        Path for output folder to store the results. Default to `"."`.
    model : str
        which model to use. Can be "L0", "L0_SR3", "L1", "L1_SR3", "CAD", "CAD_SR3", "SCAD", "SCAD_SR3"

    Returns
    -------
    None
        Return nothing. Store a yaml file contains selected fixed and random
        effects and all other diagnostic figures.
    """
    # parse covs and pre_sel_covs
    covs = defaultdict(list) if covs is None else covs
    pre_sel_covs = defaultdict(list) if pre_sel_covs is None else pre_sel_covs
    for key in ["fixed_effects", "random_effects"]:
        covs[key] = list({*covs[key], *pre_sel_covs[key]})

    # check df contain all cols
    cols = {target, se, group, *covs["fixed_effects"], *covs["random_effects"]}
    for col in cols:
        if col not in df.columns:
            raise ValueError(f"df does not contain col={col}.")

    # parse output folder
    output_folder = Path(output_folder)
    if not output_folder.exists():
        output_folder.mkdir()

    problem = LinearLMEProblem.from_dataframe(data=df,
                                              fixed_effects=covs.get("fixed_effects", []),
                                              random_effects=covs.get("random_effects", []),
                                              groups=group,
                                              variance=se,
                                              target=target,
                                              must_include_fe=pre_sel_covs.get("fixed_effects", []),
                                              must_include_re=pre_sel_covs.get("random_effects", []),
                                              )

    model_constructor, selection_spectrum = get_model(model, problem)
    best_model = None
    best_score = +np.infty
    for params in selection_spectrum:
        model = model_constructor(params)
        model.fit_problem(problem)
        score = model.jones2010bic()
        if score < best_score:
            best_model = model
            best_score = score
        print(f"{params}, score={score}")

    sel_covs = {
        "fixed_effects": [label for label, coef in zip(problem.fixed_features_columns, best_model.coef_["beta"]) if coef != 0],
        "random_effects": [label for label, coef in zip(problem.random_features_columns, best_model.coef_["gamma"]) if coef != 0]
    }

    # save results
    with open(output_folder / "sel_covs.yaml", "w") as f:
        yaml.dump(sel_covs, f)

    print(sel_covs)


def get_model(model: str, problem: LinearLMEProblem):
    """
    Takes the name of the model. Returns the constructor for it,
    as well as a suitable parameter grid for various sparsity levels.

    Parameters
    ----------
    model
    problem

    Returns
    -------

    """
    if model == "L0" or model == "SR3_L0":
        selection_spectrum = [{"nnz_tbeta": p, "nnz_tgamma": q} for p in range(1, problem.num_fixed_features) for q in
                              range(1, problem.num_random_features) if p >= q]
        return lambda params: L0LmeModel(**params) if model == "L0" else Sr3L0LmeModel(**params), selection_spectrum

    selection_spectrum = [{"lam": lam} for lam in np.logspace(start=-4, stop=5, num=100)]
    if model == "L1":
        return lambda params: L1LmeModel(**params), selection_spectrum
    elif model == "L1_SR3":
        return lambda params: SR3L1LmeModel(**params), selection_spectrum
    elif model == "CAD":
        return lambda params: CADLmeModel(**params), selection_spectrum
    elif model == "CAD_SR3":
        return lambda params: SR3CADLmeModel(**params), selection_spectrum
    elif model == "SCAD":
        return lambda params: SCADLmeModel(**params), selection_spectrum
    elif model == "SCAD_SR3":
        return lambda params: SR3SCADLmeModel(**params), selection_spectrum
    else:
        raise ValueError(f"Model name is not recognized: {model}. Should be one of: {MODELS_NAMES}")
