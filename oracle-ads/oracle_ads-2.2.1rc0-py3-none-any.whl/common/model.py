#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import distutils
import json
import os
import shutil
from collections import Iterable
from distutils.dir_util import copy_tree

import numpy as np
import pandas as pd
from IPython.core.display import display, HTML
from ads.common.utils import is_notebook
from sklearn.pipeline import Pipeline

from ads.common import logger, utils
from ads.common.model_artifact import ModelArtifact
from ads.common.utils import JsonConverter, generate_schema
from ads.dataset.pipeline import TransformerPipeline
from ads.common.model_export_util import prepare_generic_model, serialize_model, Progress_Steps_W_Fn, \
    Progress_Steps_Wo_Fn, ONNXTransformer

from skl2onnx.common.data_types import FloatTensorType, Int64TensorType, StringTensorType

Unsupported_Model_Types = []
NoTransformModels = ['torch', 'tensorflow', 'keras']

class ADSModel(object):

    def __init__(self, est, target=None, transformer_pipeline=None, client=None, booster=None, classes=None, name=None):
        """
        Construct an ADSModel

        Parameters
        ----------
        est: fitted estimator object
          The estimator can be a standard sklearn estimator, a keras, lightgbm, or xgboost estimator, or any other object that implement methods from
          (BaseEstimator, RegressorMixin) for regression or (BaseEstimator, ClassifierMixin) for classification
        target: PandasSeries
          The target column you are using in your dataset, this is assigned as the "y" attribute
        transformer_pipeline: TransformerPipeline
          A custom trasnformer pipeline object
        client: Str
          Currently unused
        booster: Str
          Currently unused
        classes: list, optional
          List of target classes. Required for classification problem if the est does not contain classes_ attribute
        name: str, optional
          Name of the model
        """
        self.est = est
        if utils.is_same_class(transformer_pipeline, Pipeline):
            self.transformer_pipeline = TransformerPipeline(transformer_pipeline.steps)
        elif isinstance(transformer_pipeline, list):
            self.transformer_pipeline = TransformerPipeline(transformer_pipeline)
        else:
            self.transformer_pipeline = transformer_pipeline
        self.target = target
        if classes is not None:
            self.classes_ = classes
        self.name = name if name is not None else str(est)  # Let the estimator define its own representation
        # These parameters make sense for dask_xgboost
        self.client = client
        self.booster = booster
        self._get_underlying_model_type()

    @staticmethod
    def from_estimator(est, transformers=None, classes=None, name=None):
        """
        Build ADSModel from a fitted estimator

        Parameters
        ----------
        est: fitted estimator object
            The estimator can be a standard sklearn estimator or any object that implement methods from
            (BaseEstimator, RegressorMixin) for regression or (BaseEstimator, ClassifierMixin) for classification
        transformers: a scalar or an iterable of objects implementing transform function, optional
            The transform function would be applied on data before calling predict and predict_proba on estimator
        classes: list, optional
            List of target classes. Required for classification problem if the est does not contain classes_ attribute
        name: str, optional
            Name of the model

        Returns
        -------
        model: ads.common.model.ADSModel
        Examples
        --------
        model = MyModelClass.train()

        model_ads = from_estimator(model)
        """
        if hasattr(est, "predict"):
            return ADSModel(est, transformer_pipeline=transformers, classes=classes, name=name)
        elif callable(est):
            return ADSModel(est, transformer_pipeline=transformers, classes=classes, name=name)

    # determine if the model is one of the common types without importing all of the libraries
    def _get_underlying_model_type(self):
        # WARNING!! Do not change the order. Particularly, sklearn must be last, as many classes extend sklearn
        model_bases = utils.get_base_modules(self.est)
        # should we be going past the first pkg name??
        if any([str(x)[:15] == "<class 'automl." for x in model_bases]):
            self._underlying_model = "automl"  # always has "automl.interface.pipeline.Pipeline" ?
        elif any([str(x)[:12] == "<class 'h2o." for x in model_bases]):
            self._underlying_model = "h2o"  # always has "h2o.model.model_base.ModelBase" ?
        elif any([str(x)[:17] == "<class 'lightgbm." for x in model_bases]):
            self._underlying_model = "lightgbm"  # either "lightgbm.sklearn.LGBMModel" or "lightgbm.Booster"
        elif any([str(x)[:16] == "<class 'xgboost." for x in model_bases]):
            self._underlying_model = "xgboost"  # always has "xgboost.sklearn.XGBModel" or "xgboost."
        elif any([str(x)[:14] == "<class 'torch." for x in model_bases]):
            self._underlying_model = "torch"  # "torch.nn.modules.module.Module"
        elif any([str(x)[:14] == "<class 'mxnet." for x in model_bases]):
            self._underlying_model = "mxnet"
        elif any([str(x)[:19] == "<class 'tensorflow." for x in model_bases]):
            self._underlying_model = "tensorflow"  # "tensorflow.python.module.module.Module"   
            if any([str(x)[:32] == "<class 'tensorflow.python.keras." for x in model_bases]):
                self._underlying_model = 'keras'
        elif any([str(x)[:13] == "<class 'pyod." for x in model_bases]):
            self._underlying_model = "pyod"  # always has pyod.models.base.BaseDetector
        elif any([str(x)[:16] == "<class 'sklearn." for x in model_bases]):
            self._underlying_model = "sklearn"  # always has "sklearn.base.BaseEstimator"
        else:
            self._underlying_model = "Unknown"
        return

    def rename(self, name):
        """
        Changes the name of a model

        Parameters
        ----------
        name: str
          A string which is supplied for naming a model
        """
        self.name = name

    def predict(self, X):
        """
        Runs the models predict function on some data

        Parameters
        ----------
        X: MLData
          A MLData object which holds the examples to be predicted on

        Returns
        -------
        Variable, based on estimator but usually a list or PandasSeries of predictions
        """
        X = self.transform(X)
        if self._underlying_model in ['torch']:
            return self.est(X)
        if self.client is not None and self.booster is not None:
            return self.est.predict(self.client, self.booster, X).persist()
        else:
            return self.est.predict(X)

    # For callable estimators, this will be more natural for ADSModel to support
    __call__ = predict

    def predict_proba(self, X):
        """
        Runs the models predict probabilities function on some data

        Parameters
        ----------
        X: MLData
          A MLData object which holds the examples to be predicted on

        Returns
        -------
        Variable, based on estimator but usually a list or PandasSeries of prediction probabilities
        """
        X = self.transform(X)
        if self._underlying_model in ['torch']:
            return self.est(X)
        if self.client is not None and self.booster is not None:
            return self.est.predict_proba(self.client, self.booster, X).persist()
        else:
            return self.est.predict_proba(X)

    def score(self, X, y_true, score_fn=None):
        """
        Scores a model according to a custom score function

        Parameters
        ----------
        X: MLData
          A MLData object which holds the examples to be predicted on
        y_true: MLData
          A MLData object which holds ground truth labels for the examples which are being predicted on
        score_fn: Scorer (callable)
          A callable object that returns a score, usually created with sklearn.metrics.make_scorer()

        Returns
        -------
        Variable, but almost always a scalar score (usually a float).
        """
        X = self.transform(X)
        if score_fn:
            return score_fn(self, X, y_true)
        else:
            assert (hasattr(self.est, "score")), f"Could not find a score function for estimator of type: " \
                                                 f"{self._underlying_model}. Please pass in your desired scoring " \
                                                 f"function to score_fn "
            if self.client is not None and self.booster is not None:
                return self.est.score(self.client, self.booster, X, y_true).persist()
            else:
                return self.est.score(X, y_true)

    def summary(self):
        """
        A summary of the ADSModel
        """
        print(self)

    def __repr__(self):
        if self._underlying_model == "automl":
            framework = self.est.pipeline.trained_model.__class__.__module__
            est = self.est.selected_model_
            params = self.est.selected_model_params_
        else:
            framework = self.est.__class__.__module__
            est = self.est.__class__.__name__
            params = self.est.get_params() if hasattr(self.est, "get_params") else None
        return "Framework: %s\n" % framework + "Estimator class: %s\n" % est + "Model Parameters: %s\n" % params

    def __getattr__(self, item):
        return getattr(self.est, item)

    def transform(self, X):
        """
        Process some MLData through the selected ADSModel transformers

        Parameters
        ----------
        X: MLData
          A MLData object which holds the examples to be transformed
        """

        if hasattr(X, "copy"):
            X = X.copy()
        if self.transformer_pipeline is not None:
            transformer_pipeline = self.transformer_pipeline
            if not isinstance(transformer_pipeline, Iterable):
                transformer_pipeline = [self.transformer_pipeline]
            for transformer in transformer_pipeline:
                try:
                    X = transformer.transform(X)
                except Exception as e:
                    pass
                    # logger.warn("Skipping pre-processing.")
        if self.target is not None and self.target in X.columns:
            X = X.drop(self.target, axis=1)
        return X

    def is_classifier(self):
        """
        Returns True if ADS believes that the model is a classifier

        Returns
        -------
        Boolean: True if the model is a classifier, False otherwise.
        """
        return hasattr(self, "classes_") and self.classes_ is not None

    def feature_names(self, X=None):
        model_type = self._underlying_model
        if model_type == "sklearn":
            return X.columns
        elif model_type == "automl":
            return self.est.selected_features_names_
        elif model_type == "lightgbm":
            try:
                return self.est.feature_name()
            except AttributeError:
                return X.columns
        elif model_type == "torch":
            return []
        elif model_type == "xgboost":
            try:
                return self.est.feature_name()
            except AttributeError:
                return X.columns
        elif model_type == "tensorflow":
            return []
        elif model_type == "keras":
            return []
        elif model_type == "mxnet":
            return []
        else:
            try:
                return self.est.feature_names()
            except:
                utils.print_user_message(f"Warning: could not find model type {model_type}, and therefore no "
                                         f"feature_names for it")
                return []

    def _onnx_data_transformer(self, X, y, **kwargs):
        if self._underlying_model in NoTransformModels:
            return X, y
        try:
            if hasattr(self, "onnx_data_preprocessor") and isinstance(self.onnx_data_preprocessor, ONNXTransformer):
                return self.onnx_data_preprocessor.transform(X=X, y=y)
            # These are the only 2 supported types so far
            task = "classification" if self.is_classifier() else "regression"
            self.onnx_data_preprocessor = ONNXTransformer(task=task)
            return self.onnx_data_preprocessor.fit_transform(X=X, y=y)
        except Exception as e:
            print(f"Warning: Onnx Data Transformation was unsuccessful with error: {e}")
            raise e

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state

    def prepare(self, target_dir=None, data_sample=None, X_sample=None, y_sample=None, include_data_sample=False,
                force_overwrite=False, fn_artifact_files_included=True, fn_name='model_api',
                inference_conda_env=None, data_science_env=False, ignore_deployment_error=False):
        """
        Prepare model artifact directory to be published to model catalog

        Parameters
        ----------
        target_dir: str, default: model.name[:12]
            Target directory under which the model artifact files need to be added
        data_sample: ADSData
            Note: This format is preferable to X_sample and y_sample.
            A sample of the test data that will be provided to predict() API of scoring script
            Used to generate schema.json which defines the input and output formats
            If include_data_sample is set to True, this data also gets added to data_sample.json
        X_sample: Union[pandas.DataFrame, dask.dataframe.core.DataFrame]
            A sample of input data that will be provided to predict() API of scoring script
            Used to generate schema.json which defines the input and output formats
            If include_data_sample is set to True, this data also gets added to data_sample.json
        y_sample: Union[pandas.Series, dask.dataframe.core.Series]
            A sample of output data that is expected to be returned by predict() API of scoring script,
            corresponding to X_sample
            Used to generate schema.json which defines the input and output formats
            Additionally, if include_data_sample is set to True, this data also gets added to data_sample.json
        include_data_sample: bool, default: False
            If True, a data_sample.json showing the sample input and output of scoring script is added to the target
            directory
        force_overwrite: bool, default: False
            If True, overwrites the target directory if exists already
        fn_artifact_files_included: bool, default: True
            If True, generates artifacts to export a model as a function without ads dependency
        fn_name: str, default: 'model_api'
            Required parameter if fn_artifact_files_included parameter is setup.
        inference_conda_env: str, default: None
            Conda environment to use within the model deployment service for inferencing
        data_science_env: bool, default: False
            If set to True, datascience environment represented by the slug in the training conda environment will be used.
        ignore_deployment_error: bool, default: False
            If set to True, the prepare will ignore all the errors that may impact model deployment

        Returns
        -------
        model_artifact: an instance of `ModelArtifact` that can be used to test the generated scoring script
        """
        # Add 2 for model and schema (Artifact Directory gets skipped in prepare_generic when progress is passed in).
        ProgressStepsWFn = Progress_Steps_W_Fn + 2
        ProgressStepsWoFn = Progress_Steps_Wo_Fn + 2
        if target_dir is None:
            utils.print_user_message(
                f"Target Directory was not specified, so we will try to build the Model Artifact in {self.name[:12]}. "
                f"To specify the Target Directory, set target_dir = <your/desired/path>")
        can_generate_fn_files = fn_artifact_files_included and self._underlying_model not in Unsupported_Model_Types
        assert data_sample is not None or X_sample is not None, "In order to prepare a model, you must provide a data " \
                                                                "sample. This can be done as an ADSData object with " \
                                                                "the parameter `data_sample`, or as X and y samples " \
                                                                "to X_sample and y_sample respectively. "
        with utils.get_progress_bar(ProgressStepsWFn if can_generate_fn_files else ProgressStepsWoFn) as progress:
            progress.update("Preparing Model Artifact Directory")
            if os.path.exists(target_dir):
                if not force_overwrite:
                    raise ValueError("Directory already exists, set force to overwrite")
            os.makedirs(target_dir, exist_ok=True)

            # Bring in model-ignore file
            shutil.copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "artifact/.model-ignore"),
                            os.path.join(target_dir, ".model-ignore"))
            distutils.dir_util._path_created = {}

            progress.update("Serializing model")
            # Transform the data to be onnx-ready
            X_sample = data_sample.X if X_sample is None and data_sample is not None else X_sample
            y_sample = data_sample.y if y_sample is None and data_sample is not None else y_sample
            X_trans, y_trans = self._onnx_data_transformer(X=X_sample, y=y_sample)
            model_kwargs = serialize_model(model=self, target_dir=target_dir, X=X_trans, y=y_trans,
                                           model_type=self._underlying_model)
            
            if self._underlying_model not in NoTransformModels:
                try:
                    self.onnx_data_preprocessor.save(os.path.join(target_dir, "onnx_data_transformer.json"))
                except Exception as e:
                    utils.print_user_message(f"Unable to serialize the data transformer due to: {e}", display_type="error")
                    raise e

            progress.update("Generating schema" if X_sample is not None else "")
            model_kwargs['is_classifier'] = self.is_classifier() if hasattr(self, 'is_classifier') and \
                                                                    callable(self.is_classifier) else None
            model_kwargs['classes_'] = getattr(self, 'classes_', None)
            try:
                schema, data_sample = generate_schema(X_sample=X_sample, y_sample=y_sample, **model_kwargs)
                if len(data_sample) > 0:
                    if include_data_sample:
                        with open(os.path.join(target_dir, "data-sample.json"), "wt") as f:
                            json.dump(data_sample, f, cls=JsonConverter, indent=2)
                    with open(os.path.join(target_dir, "schema.json"), "wt") as f:
                        json.dump(schema, f, cls=JsonConverter, indent=2)
            except Exception as e:
                print(f"WARNING: failed to create schema and data sample {e}")
            
            if model_kwargs.get('serializer', "") != "onnx":
                model_kwargs['model_libs'] = utils.extract_lib_dependencies_from_model(self.est)
            model_kwargs['underlying_model'] = self._underlying_model
            model_kwargs['progress'] = progress
            model_kwargs['inference_conda_env'] = inference_conda_env
            model_kwargs['data_science_env'] = data_science_env
            model_kwargs['ignore_deployment_error'] = ignore_deployment_error

            model_artifact = prepare_generic_model(target_dir, fn_artifact_files_included=fn_artifact_files_included,
                                                   fn_name=fn_name, force_overwrite=force_overwrite, **model_kwargs)
            try:
                model_artifact.reload()
            except Exception as e:
                print(str(e))
                msg = "\nWARNING: Validation using scoring script failed. Update the inference script(" \
                      "score.py) as required. "
                print('\033[93m' + msg + '\033[0m')

            # __pycache__ was created during model_artifact.reload() above
            if os.path.exists(os.path.join(target_dir, '__pycache__')):
                shutil.rmtree(os.path.join(target_dir, '__pycache__'), ignore_errors=True)

            utils.print_user_message(
                "Any function defined in <code>score.py</code> can be directly invoked on the returned "
                "<code>ModelArtifact</code> instance")
            utils.print_user_message(model_artifact.__repr__())
            return model_artifact

    def visualize_transforms(self):
        """
        A graph of the ADSModel transformer pipeline.
        It is only supported in JupyterLabs Notebooks.
        """
        self.transformer_pipeline.visualize()

    def show_in_notebook(self):
        """
        Describe the model by showing it's properties
        """
        # ['Is Regression', self.est.is_regression],
        if self._underlying_model == "automl":
            info = [
                ['Model Name', self.name],
                ['Target Variable', self.target],
                ['Selected Algorithm', self.est.selected_model_],
                ['Task', self.est.task],
                ['Training Dataset Size', self.est.train_shape_],
                ['CV', self.est.cv_],
                ['Optimization Metric', self.est.score_metric],
                ['Selected Hyperparameters', self.est.selected_model_params_],
                ['Initial Number of Features', self.est.train_shape_[1]],
                ['Initial Features', self.est.pipeline.orig_feature_names],
                ['Selected Number of Features', len(self.est.selected_features_names_)],
                ['Selected Features', self.est.selected_features_names_],
            ]
        else:
            info = [
                ['Model Name', self.name],
                ['Target Variable', self.target if self.target is not None else "not available from estimator"],
                ['Selected Hyperparameters', self.est.get_params() if hasattr(self.est, "get_params") else None],
                ['Framework', self.est.__class__.__module__],
                ['Estimator Class', self.est.__class__.__name__],
                ['Contained Estimator', self.est.est.__class__.__name__ if hasattr(self.est, "est") else None],
            ]
        info_df = pd.DataFrame(info)

        if is_notebook():
            with pd.option_context('display.max_colwidth', 1000, 'display.width', None, 'display.precision', 4):
                display(HTML(info_df.to_html(index=False, header=False)))
        return info

    @staticmethod
    def get_init_types(df, underlying_model=None):
        if underlying_model == 'sklearn':
            n_cols = len(df.columns)
            return [('input', FloatTensorType([None, n_cols]))], {'type': np.float32}
        return [], {}

    @staticmethod
    def convert_dataframe_schema(df, drop=None):
        inputs = []
        for k, v in zip(df.columns, df.dtypes):
            if drop is not None and k in drop:
                continue
            if v == 'int64':
                t = Int64TensorType([1, 1])
            elif v == 'float64':
                t = FloatTensorType([1, 1])
            else:
                t = StringTensorType([1, 1])
            inputs.append((k, t))
        return inputs
