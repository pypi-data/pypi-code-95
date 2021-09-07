from simpletransformers.classification import MultiLabelClassificationModel
from simpletransformers.classification import ClassificationModel, ClassificationArgs
import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier
import xgboost as xgb
from catboost import CatBoostClassifier
import pandas as pd
import numpy as np
import sklearn
from typing import List
from pprint import pprint


def multilabel_classification(
    model_type, model_name, model_params, train_params, eval_params, train_set, eval_set
):
    """
    Train and evaluate a multilabel classification model.

    :param model_type: One of the model types from the supported models, https://simpletransformers.ai/docs/classification-specifics/#supported-model-types
    :param model_type: str
    :param model_name: Name of the model to use. Find it on the official simpletransformer documentation, https://huggingface.co/transformers/pretrained_models.html
    :type model_name: str
    :param model_params: Model parameters.
    :type model_params: dict
    :param train_params: Training parameters.
    :type train_params: dict
    :param eval_params: Evaluation parameters.
    :type eval_params: dict
    :param train_set: Training set.
    :type train_set: pandas.DataFrame
    :param eval_set: Evaluation set.
    :type eval_set: pandas.DataFrame
    :returns:
        model: fine-tuned simpletransformers model
        results: dict: ex: {"LRAP": 0.98, "eval_loss": 0.15}
    """

    assert type(train_df) == pd.DataFrame, "train_df must be a pandas.DataFrame"
    assert type(eval_df) == pd.DataFrame, "eval_df must be a pandas.DataFrame"

    model = MultiLabelClassificationModel(
        model_type, model_name, use_cuda=False, num_labels=6
    )

    model.train_model(train_df)
    result, model_outputs, wrong_predictions = model.eval_model(eval_df)

    return result, model_outputs, wrong_predictions


def voting_classifier(
    features_train: np.array,
    labels_train,
    features_test: np.array,
    lgbm_params: List = None,
    rf_params: List = None,
    xgb_params: List = None,
    catboost_params: List = None,
) -> sklearn.VotingClassifier:
    """
    Train a voting classifier.

    :param features_train: Training features.
    :type features_train: numpy.ndarray
    :param labels_train: Training labels.
    :type labels_train: List
    :param features_test: Testing features.
    :type features_test: numpy.ndarray
    :param lgbm_params: Parameters for lightgbm.
    :type lgbm_params: dict
    :param rf_params: Parameters for sklearn.ensemble.RandomForestClassifier.
    :type rf_params: dict
    :param xgb_params: Parameters for xgboost.
    :type xgb_params: dict
    :param catboost_params: Parameters for catboost.
    :type catboost_params: dict
    :returns:
        model: fine-tuned voting classifier model
    """

    lgbm_params = lgbm_params if lgbm_params else {}
    rf_params = rf_params if rf_params else {}
    xgb_params = xgb_params if xgb_params else {}
    catboost_params = catboost_params if catboost_params else {}

    lgbm_model = lgb.LGBMClassifier(**lgbm_params)
    rf_model = RandomForestClassifier(**rf_params)
    xgb_model = xgb.XGBClassifier(**xgb_params)
    catboost_model = CatBoostClassifier(**catboost_params)

    voting_model = VotingClassifier(
        estimators=[
            ("lgbm", lgbm_model),
            ("rf", rf_model),
            ("xgb", xgb_model),
            ("catboost", catboost_model),
        ],
        voting="soft",
    )

    vot.fit(features_train, labels_train)
    pprint(vot)

    return voting_model


def multiclass_classification(
    model_type, model_name, epochs, train_set, train_labels, eval_set, eval_labels
):
    """
    Train and evaluate a multilabel classification model.
    :param model_type: One of the model types from the supported models, https://simpletransformers.ai/docs/classification-specifics/#supported-model-types
    :param model_type: str
    :param model_name: Name of the model to use. Find it on the official simpletransformer documentation, https://huggingface.co/transformers/pretrained_models.html
    :type model_name: str
    :param epochs: Number of epochs to train.
    :type epochs: int
    :param train_set: Training set.
    :type train_set: List[str]
    :param train_labels: Training labels.
    :type train_labels: List[int]
    :param eval_set: Evaluation set.
    :type eval_set: List[str]
    :param eval_labels: Evaluation labels.
    :type eval_labels: List[int]
    :returns:
        model: fine-tuned simpletransformers model
        results: dict: ex: {"mcc": 0.98, "eval_loss": 0.15}
        mcc is Matthews correlation coefficient (https://scikit-learn.org/stable/modules/generated/sklearn.metrics.matthews_corrcoef.html)
    """

    assert type(train_set) == list, "train_set must be a list"
    assert type(train_labels) == list, "train_labels must be a list"
    assert type(eval_set) == list, "eval_set must be a list"
    assert type(eval_labels) == list, "eval_labels must be a list"

    epochs = 1 if epochs == 0 else epochs

    train_df = pd.DataFrame({"text": train_set, "label": train_labels})

    eval_df = pd.DataFrame({"text": eval_set, "label": eval_labels})

    model_args = ClassificationArgs(num_train_epochs=1)

    model = ClassificationModel(
        model_type, model_name, num_labels=len(train_df.label.unique()), args=model_args
    )

    model.train_model(train_df)

    result, _, _ = model.eval_model(eval_df)

    return model, result
