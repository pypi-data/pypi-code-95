#!/usr/bin/env python
# -*- coding: utf-8 -*--

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from __future__ import print_function, absolute_import, division

import copy

import dask.dataframe as dd
from ads.common.model import ADSModel
from ads.common.model import ADSModel
from ads.dataset import helper
from ads.dataset.dataset_with_target import ADSDatasetWithTarget
from ads.dataset.classification_dataset import BinaryClassificationDataset, MultiClassClassificationDataset, MultiClassTextClassificationDataset, BinaryTextClassificationDataset
from ads.dataset.regression_dataset import RegressionDataset

from ads.dataset.pipeline import TransformerPipeline
from ads.environment import ml_runtime
from ads.type_discovery.type_discovery_driver import TypeDiscoveryDriver
from ads.type_discovery.typed_feature import ContinuousTypedFeature, DiscreteTypedFeature
from ads.common import utils

dataset_task_map = {
        BinaryClassificationDataset: utils.ml_task_types.BINARY_CLASSIFICATION,
        BinaryTextClassificationDataset: utils.ml_task_types.BINARY_TEXT_CLASSIFICATION,
        MultiClassClassificationDataset: utils.ml_task_types.MULTI_CLASS_CLASSIFICATION,
        MultiClassTextClassificationDataset: utils.ml_task_types.MULTI_CLASS_TEXT_CLASSIFICATION,
        RegressionDataset: utils.ml_task_types.REGRESSION
}

def get_ml_task_type(X, y, classes):
    """
    Gets the ML task type and returns it.

    Parameters
    ----------
    X: Dataframe
        The training dataframe
    Y: Dataframe
        The testing dataframe
    Classes: List
        a list of classes

    Returns
    -------
    ml_task_type: A particular task type like `REGRESSION`, `MULTI_CLASS_CLASSIFICATION`...
    """
    target_type = TypeDiscoveryDriver().discover(y.name, y)
    if isinstance(target_type, DiscreteTypedFeature):
        if len(classes) == 2:
            if helper.is_text_data(X):
                ml_task_type = utils.ml_task_types.BINARY_TEXT_CLASSIFICATION
            else:
                ml_task_type = utils.ml_task_types.BINARY_CLASSIFICATION
        else:
            if helper.is_text_data(X):
                ml_task_type = utils.ml_task_types.MULTI_CLASS_TEXT_CLASSIFICATION
            else:
                ml_task_type = utils.ml_task_types.MULTI_CLASS_CLASSIFICATION
    elif isinstance(target_type, ContinuousTypedFeature):
        ml_task_type = utils.ml_task_types.REGRESSION
    else:
        raise TypeError("AutoML for target type ({0}) is not yet available"
                                   .format(target_type.meta_data["type"]))
    return ml_task_type


class AutoML:

    def __init__(self, training_data, validation_data=None, provider=None, baseline="dummy"):
        """
        Creates an Automatic machine learning object.

        Parameters
        ----------
        training_data : `ADSData` instance
        validation_data : `ADSData` instance
        provider : None or object of ads.automl.provider.AutoMLProvider
            If None, the default OracleAutoMLProvider will be used to generate the model
        baseline: None, "dummy", or object of ads.common.model.ADSModel (Default is "dummy")
            If None, than no baseline is created,
            If "dummy", than the DummyClassifier or DummyRegressor are used
            If Object, than whatever estimator is provided will be used.
              This estimator must include a part of its pipeline which does preprocessing
              to handle categorical data


        Examples
        --------
        train, test = ds.train_test_split()

        olabs_automl = OracleAutoMLProvider()

        model, baseline = AutoML(train, provider=olabs_automl).train()
        """
        from ads.automl.provider import OracleAutoMLProvider, BaselineAutoMLProvider
        if hasattr(training_data, "transformer_pipeline"):
            self.transformer_pipeline = training_data.transformer_pipeline
        else:
            self.transformer_pipeline = None

        if isinstance(training_data, ADSDatasetWithTarget):
            training_data, _ = training_data.train_test_split(test_size=0.0)

        if isinstance(validation_data, ADSDatasetWithTarget):
            validation_data, _ = validation_data.train_test_split(test_size=0.0)

        X = training_data.X.compute() if isinstance(training_data.X, dd.DataFrame) else training_data.X
        y = training_data.y.compute() if isinstance(training_data.y, dd.Series) else training_data.y

        self.X_shape = X.shape

        X_valid = None
        y_valid = None
        if validation_data is not None:
            X_valid = validation_data.X.compute() if isinstance(validation_data.X, dd.DataFrame) else validation_data.X
            y_valid = validation_data.y.compute() if isinstance(validation_data.y, dd.Series) else validation_data.y
        self.target_name = y.name
        self.feature_names = X.columns.values
        self.client = ml_runtime.compute_accelerator()
        class_names = y.unique()

        if training_data.dataset_type in dataset_task_map:
            self.ml_task_type = dataset_task_map[training_data.dataset_type]
        else:
            self.ml_task_type = get_ml_task_type(X, y, class_names)

        # We have decided to use OracleAutoMLProvider as the default if provider
        # is not specified.
        if provider is None:
            provider = OracleAutoMLProvider()
        self.no_baseline = False

        self.automl_provider = provider
        if baseline == None:
            self.no_baseline = True
            self.baseline_provider = None
            self.automl_provider.setup(X, y, self.ml_task_type, X_valid=X_valid, y_valid=y_valid, class_names=class_names, client=self.client)
        elif baseline == "dummy":
            self.baseline_provider = BaselineAutoMLProvider(None)
            for provider in [self.baseline_provider, self.automl_provider]:
                provider.setup(X, y, self.ml_task_type, X_valid=X_valid, y_valid=y_valid, class_names=class_names, client=self.client)
        else:
            self.baseline_provider = BaselineAutoMLProvider(baseline)
            for provider in [self.baseline_provider, self.automl_provider]:
                provider.setup(X, y, self.ml_task_type, X_valid=X_valid, y_valid=y_valid, class_names=class_names,
                               client=self.client)

    def __getattr__(self, attr):
        # If the attribute is not in the AutoML object,
        # then it'll search to see if it exists in the provider
        err_msg = ''
        if attr.startswith('__') and attr.endswith('__'):
            raise AttributeError("{} object has no attribute '{}'.".format(
                self.__class__.__name__, attr))

        if 'automl_provider' in self.__dict__.keys() and self.automl_provider is not None \
            and hasattr(self.automl_provider, attr):
            return getattr(self.automl_provider, attr)
        else:
            raise AttributeError("{} object has no attribute '{}'; {}".format(
                self.__class__.__name__, attr, err_msg))

    def train(self, **kwargs):
        """
        Returns a fitted automl model and a fitted baseline model.

        Parameters
        ----------
        kwargs : dict, optional
            kwargs passed to provider's train method

        Returns
        -------
        model: object of ads.common.model.ADSModel
            the trained automl model
        baseline: object of ads.common.model.ADSModel
            the baseline model to compare
        Examples
        --------
        train, test = ds.train_test_split()

        olabs_automl = OracleAutoMLProvider()

        model, baseline = AutoML(train, provider=olabs_automl).train()
        """

        time_budgeted = 'time_budget' in kwargs
        avail_n_cores = max(utils.get_compute_accelerator_ncores(), utils.get_cpu_count())

        warn_params = [
            (10**5, 4, 'VM.Standard.E2.4'),
            (10**6, 16, 'VM.Standard.2.16')
        ]
        for params in warn_params:
            if self.X_shape[0] * self.X_shape[1] > params[0] and utils.get_cpu_count() <= params[1]:
                warning_message = f"Given the size of your dataset ({self.X_shape[0]} rows with {self.X_shape[1]} columns), " \
                                  f"we recommend that you use a larger VM shape, at least a {params[2]} for this task."

                utils.print_user_message(
                    warning_message,
                    display_type="warning",
                    title="AutoML"
                )

        if avail_n_cores < 6 and self.X_shape[0] > 1000:
            training_message = f"""
            <h2>NOTE: With {avail_n_cores} cores available for training on {self.X_shape[0]} rows with {self.X_shape[1]} features please consider</h2>
                - using a larger VM Shape
                - sampling the data to be smaller
                - using the time_budget feature to reduce training size
                - using the model_list to restrict the algorithms

            AutoML Training ({self.automl_provider.__class__.__name__})
            """
        else:
            training_message = "AutoML Training ({})...".format(self.automl_provider.__class__.__name__)

        utils.print_user_message(
            training_message,
            display_type='info',
            title="AutoML"
        )

        # train using automl and baseline
        if self.no_baseline:
            self.automl_provider.train(**kwargs)
            if self.transformer_pipeline is not None:
                transformer_pipeline1 = copy.deepcopy(self.transformer_pipeline)
                for transformer in self.automl_provider.get_transformer_pipeline():
                    transformer_pipeline1.add(transformer)
            else:
                pipeline1 = self.automl_provider.get_transformer_pipeline()
                transformer_pipeline1 = TransformerPipeline(pipeline1) if pipeline1 is not None else None
            model = ADSModel(self.automl_provider.est, self.target_name, transformer_pipeline1)
            return model
        else:
            for provider in [self.automl_provider, self.baseline_provider]:
                provider.train(**kwargs)
            if self.transformer_pipeline is not None:
                transformer_pipeline1 = copy.deepcopy(self.transformer_pipeline)
                transformer_pipeline2 = copy.deepcopy(self.transformer_pipeline)
                for transformer in self.automl_provider.get_transformer_pipeline():
                    transformer_pipeline1.add(transformer)
                for transformer in self.baseline_provider.get_transformer_pipeline():
                    transformer_pipeline2.add(transformer)
            else:
                pipeline1 = self.automl_provider.get_transformer_pipeline()
                pipeline2 = self.baseline_provider.get_transformer_pipeline()
                transformer_pipeline1 = TransformerPipeline(pipeline1) if pipeline1 is not None else None
                transformer_pipeline2 = TransformerPipeline(pipeline2) if pipeline2 is not None else None
            model = ADSModel(self.automl_provider.est, self.target_name, transformer_pipeline1)
            baseline = ADSModel(self.baseline_provider.est, self.target_name, transformer_pipeline2)
            return model, baseline
