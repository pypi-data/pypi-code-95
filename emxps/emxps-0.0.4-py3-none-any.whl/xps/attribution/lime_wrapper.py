import logging

import numpy as np
from tqdm import tqdm
from emutils.dsutils import process_data

import lime
import lime.lime_tabular

from .api import BaseExplainer


class LIME(BaseExplainer):
    def __init__(self, model, X, class_names, feature_names, random_state, **kwargs):
        X = self.preprocess(X)

        logging.info(
            f'Default LIME kernel with is {np.sqrt(len(feature_names)) * .75}.' +
            (f'Here we are using {kwargs["kernel_width"]}.') if 'kernel_width' in kwargs else ""
        )

        self.explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=X,
            class_names=class_names,
            feature_names=feature_names,
            # categorical_features=range(len(self.features)),
            # categorical_names={j: self.encdec.get_values(feature)
            #    for j, feature in enumerate(self.features)},
            # verbose=verbose,
            random_state=random_state,
            # kernel_width=...
            **kwargs
            # mode = 'classification'/'regression'
        )
        self.feature_names = feature_names
        self.model = model

    def shap_values(self, X):
        assert X.shape[1] == len(self.feature_names)
        preds = self.model.predict(X)
        res = []
        for x, pred in tqdm(zip(X, preds)):
            explanation = dict(
                self.explainer.explain_instance(
                    data_row=x,
                    predict_fn=self.model.predict_proba,
                    labels=(pred, ),  # We explain only the predicted class
                    num_features=len(self.feature_names),
                ).as_map()[pred]
            )
            res.append(np.array([explanation[i] for i in range(len(self.feature_names))]))
        return np.array(res)