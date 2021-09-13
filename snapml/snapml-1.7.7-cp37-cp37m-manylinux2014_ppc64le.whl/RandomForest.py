# *****************************************************************
#
# Licensed Materials - Property of IBM
#
# (C) Copyright IBM Corp. 2017, 2020, 2021. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
#
# ******************************************************************

import numpy as np
import sys
import math

if sys.version_info[0] < 3:
    import libsnapmllocal2 as libsnapml
else:
    import snapml.libsnapmllocal3 as libsnapml

from abc import ABC, abstractmethod

from snapml.CommonModel import CommonModel


class RandomForest(CommonModel):
    @abstractmethod
    def __init__(self):
        # just for reference
        self.n_estimators = None
        self.criterion = None
        self.max_depth = None
        self.min_samples_leaf = None
        self.max_features = None
        self.bootstrap = None
        self.n_jobs = None
        self.random_state = None
        self.verbose = None
        self.use_histograms = None
        self.hist_nbins = None
        self.use_gpu = None
        self.gpu_ids = None
        self.task_type_ = None
        self.params = None
        self.n_features_in_ = None
        self.compress_trees = None
        self.n_classes_ = None

    def __setstate__(self, d):

        # if the model was trained, let's rebuild the cache
        if d["model_size_"] > 0:
            d["cache_id_"] = libsnapml.rfc_cache(d["model_"], d["model_size_"])
        else:
            d["cache_id_"] = 0

        self.__dict__ = d

    def __del__(self):
        # if the forest was cached, let's ensure that it gets destroyed in C++
        if self.cache_id_ > 0:
            libsnapml.rfc_delete(self.cache_id_)

    def check_gpu(self):
        if (self.use_gpu == True) and (self.max_depth is None or self.max_depth > 16):
            print(
                "GPU acceleration only supported for bounded max_depth <= 16; forest will be built with max_depth=16"
            )
            self.max_depth = 16

        self.gpu_ids = np.array(self.gpu_ids).astype(np.uint32)
        if self.use_gpu and len(self.gpu_ids) == 0:
            raise ValueError("Please provide at least one gpu_id.")

        for gpu_id in self.gpu_ids:
            if gpu_id < 0:
                raise ValueError("Invalid gpu_id")

    def c_fit(
        self,
        max_depth,
        min_samples_leaf,
        max_features,
        random_state,
        num_ex,
        num_ft,
        num_nz,
        indptr,
        indices,
        data,
        labs,
        num_classes,
        sample_weight,
    ):

        model, model_size, feature_importances, self.cache_id_ = libsnapml.rfc_fit(
            self.task_type_,
            self.n_estimators,
            self.criterion,
            max_depth,
            min_samples_leaf,
            max_features,
            self.bootstrap,
            self.n_jobs,
            random_state,
            self.verbose,
            self.use_histograms,
            self.hist_nbins,
            self.use_gpu,
            self.gpu_ids,
            self.compress_trees,
            num_ex,
            num_ft,
            num_nz,
            num_classes,
            indptr,
            indices,
            data,
            labs,
            sample_weight,
        )

        return model, model_size, feature_importances

    def c_predict(
        self, num_ex, num_ft, indptr, indices, data, n_jobs, proba, num_classes
    ):

        # Generate predictions
        pred, self.cache_id_ = libsnapml.rfc_predict(
            num_ex,
            num_ft,
            n_jobs,
            indptr,
            indices,
            data,
            self.model_,
            self.model_size_,
            proba,
            num_classes,
            self.cache_id_,
        )

        return pred

    def _import_model(self, input_file, type):

        """
        Import a pre-trained forest ensemble from the given input file of the given type.

        Supported import format is (sklearn) PMML and ONNX. The corresponding input file type to be
        provided to the import_model function is 'pmml' or 'onnx' respectively.

        If the input file contains features that are not supported by the import function
        then a runtime error is thrown indicating the feature and the line number within
        the input file containing the feature.

        Parameters
        ----------
        input_file : str
            Input filename

        type : {'pmml', 'onnx'}
            Input file type

        Returns
        -------
        self : object
        """

        if (not isinstance(input_file, (str))) or (input_file == ""):
            raise Exception("Input file name not provided.")

        if (not isinstance(type, (str))) or (type == ""):
            raise Exception("Input file type not provided.")

        self.model_, self.model_size_, self.n_classes_ = libsnapml.rfc_import(
            input_file, type, self.task_type_
        )

        return self

    def _compress_trees(self, X=None):

        """
        Compress decision trees for fast inference

        The binary decision tree ensemble created by training or by importing a pre-trained
        model is transformed into a more compact (compressed) format that enables higher inference
        performance and a smaller serialized model size.

        The transformation involves organizing the original binary decision trees into node clusters
        with specific interconnection structures based on expected node access characteristics. By
        exploiting the interconnection and node characteristics, the node clusters can be compressed
        within a minimum number of cache lines while also increasing spatial locality and, thus,
        cache performance.

        An input data set is optional and is used to predict node access characteristics for
        performing the node clustering. A maximum number (Lmax) of examples is used for this task.

        Parameters
        ----------
        X : dense matrix (ndarray)
            Optional input dataset used for compressing trees

        """

        num_ex = 0
        num_ft = 0
        data = np.array([], dtype=np.float32)

        # Validate input data
        if X is not None:

            if type(X).__name__ != "ndarray":
                raise ValueError("X should be in ndarray format.")

            num_ex = X.shape[0]
            num_ft = X.shape[1]
            data = np.ascontiguousarray(X, dtype=np.float32)

        # Compress trees
        self.model_, self.model_size_, self.cache_id_ = libsnapml.rfc_compress(
            num_ex, num_ft, data, self.model_, self.model_size_, self.cache_id_
        )

        return self

    def import_model(self, input_file, type, X=None):

        """
        Import a pre-trained forest ensemble model from the given input file of the given type.
        Returns an optimized Snap ML model format with compressed decision trees for fast inference.

        Supported import format is (sklearn) PMML.
        The corresponding input file type to be provided to the import_model function is 'pmml'.

        If the input file contains features that are not supported by the import function
        then a runtime error is thrown indicating the feature and the line number within
        the input file containing the feature.

        An input data set X is optional and is used to predict node access characteristics for
        performing the node clustering.

        Parameters
        ----------
        input_file : str
            Input filename

        type : {'pmml'}
            Input file type

        X : dense matrix (ndarray)
            Dataset used for compressing trees

        Returns
        -------
        self : object
        """

        # import model
        self._import_model(input_file, type)

        # compress trees
        self._compress_trees(X)

        return self
