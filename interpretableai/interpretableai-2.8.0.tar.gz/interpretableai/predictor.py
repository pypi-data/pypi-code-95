import json
import pandas as pd
import numpy as np


def iterate_samples(X):
    if isinstance(X, pd.DataFrame):
        # itertuples returns a namedtuple for each row of the dataframe, which
        # we convert lazily to a dict
        return map(lambda x: x._asdict(), X.itertuples())
    else:
        return X


def get_sample_at_i(X, i):
    if isinstance(X, pd.DataFrame):
        return X.iloc[i, :]
    elif isinstance(X, np.ndarray):
        return X[i, :]
    else:
        return X[i]


class Predictor():
    """An object that reads saved Interpretable AI models from JSON files and
    makes predictions.

    Examples
    --------
    >>> iai.Predictor(filename)

    Parameters
    ----------
    filename : str
        path to the JSON file to be read in
    """
    def __init__(self, path):
        with open(path) as f:
            model = json.load(f)

        if model['_julia_type'] == 'GridSearch':
            self.model = model['lnr']
        else:
            self.model = model

        def convert_sparse_vector(v):
            if isinstance(v, dict):
                return v
            else:
                return {
                    'n': len(v),
                    'nzind': [i + 1 for i, x in enumerate(v) if x != 0],
                    'nzval': [x for x in v if x != 0],
                }

        if self.model['_julia_type'] == 'OptimalFeatureSelectionClassifier':
            if 'fit_' in self.model:
                fit = self.model['fit_']
            else:
                fit = self.model['fits_'][0]
            if 'inner' in fit:
                fit = fit['inner']
            else:
                fit = fit['logistic_fit']
            fit['beta'] = convert_sparse_vector(fit['beta'])
        elif self.model['_julia_type'] == 'OptimalFeatureSelectionRegressor':
            if 'fit_' in self.model:
                fit = self.model['fit_']
            else:
                fit = self.model['fits_'][0]
            fit['beta'] = convert_sparse_vector(fit['beta'])
        else:
            # Convert "Infinity" to inf for thresholds
            for node in self.model['tree_']['nodes']:
                if node['split_type'] == 'MIXED':
                    m = node['split_mixed']
                    if m['do_parallel']:
                        p = m['parallel_split']
                        if isinstance(p['threshold'], str):
                            p['threshold'] = float(p['threshold'].replace(
                                                   "Infinity", "inf"))

            for node in self.model['tree_']['nodes']:
                if node['split_type'] == 'HYPERPLANE':
                    h = node['split_hyperplane']
                    h['weights'] = convert_sparse_vector(h['weights'])
                fit = node['fit']
                if 'beta' in fit:
                    fit['beta'] = convert_sparse_vector(fit['beta'])
                if 'treatment_fit' in fit:
                    for t in fit['treatment_fit']:
                        t['beta'] = convert_sparse_vector(t['beta'])

    # Override autocompletion attributes to hide the internal functions
    def __dir__(self):  # pragma: no cover
        learner_type = self.model['_julia_type']
        if learner_type == 'OptimalTreeClassifier':
            return (
                'apply',
                'predict',
                'predict_proba',
            )
        elif learner_type == 'OptimalTreeRegressor':
            return (
                'apply',
                'predict',
            )
        elif learner_type in ['OptimalTreePolicyMinimizer',
                              'OptimalTreePolicyMaximizer']:
            return (
                'apply',
                'predict',
                'predict_outcomes',
                'predict_treatment_outcome',
                'predict_treatment_rank',
            )
        elif learner_type in ['OptimalTreePrescriptionMinimizer',
                              'OptimalTreePrescriptionMaximizer']:
            return (
                'apply',
                'predict',
                'predict_outcomes',
            )
        elif learner_type == 'OptimalTreeSurvivalLearner':
            return (
                'apply',
                'predict_expected_survival_time',
                'predict_hazard',
            )
        elif learner_type == 'OptimalFeatureSelectionClassifier':
            return (
                'predict',
                'predict_proba',
            )
        elif learner_type == 'OptimalFeatureSelectionRegressor':
            return (
                'predict',
            )
        else:
            raise TypeError('{} not supported'.format(learner_type))

    def _get_term(self, numeric_j, x, coef, features):
        j = features['numeric_features'][numeric_j] - 1
        feature_name = features['feature_names'][j]

        # handle categoric and ordinal onehot
        onehot_j = numeric_j - features['n_numeric_orig_features']
        if onehot_j >= 0:
            onehot_start = features['onehot_start_index'][j]
            onehot_end = features['onehot_start_index'][j + 1]
            level_ind = numeric_j - onehot_start
            ordinal_feature_map = {
                int(k): int(v)
                for k, v in features['ordinal_feature_map'].items()
            }
            ordinal_j = ordinal_feature_map.get(j + 1, 0) - 1

            cat_levels = features['categoric_labelmap'][j]['levels']
            leq_range = range(0, 0)

            label_map = []
            if ordinal_j >= 0:
                ord_levels = features['ordinal_labelmap'][ordinal_j]['levels']
                label_map.extend(ord_levels)

                # Check if we need to account for <= onehot
                n_levels = len(cat_levels) - 1 + len(ord_levels)
                if n_levels > 2 and (onehot_end - onehot_start) > n_levels:
                    leq_levels = ord_levels[1:-2]
                    leq_range = range(len(label_map),
                                      len(label_map) + len(leq_levels))
                    label_map.extend(leq_levels)

            label_map.extend(cat_levels)
            # remove missing level
            label_map.remove('missing')
            if level_ind in leq_range:
                levels = level_ind - len(ord_levels) + 2
                return (x[feature_name] in ord_levels[0:levels]) * coef
            else:
                level = label_map[level_ind]
                return (x[feature_name] == level) * coef

        else:
            return x[feature_name] * coef

    def _get_hyperval(self, weights, x, features):
        return sum([self._get_term(weights['nzind'][i] - 1, x,
                                   weights['nzval'][i],
                                   features)
                    for i in range(len(weights['nzind']))])

    def _apply_split_hyperplane(self, node, x):
        tree = self.model
        features = tree['prb_']['data']['features']

        hyperplane_split = node['split_hyperplane']
        weights = hyperplane_split['weights']
        if weights['nzind']:
            thresh = hyperplane_split['threshold']
            hyperval = self._get_hyperval(weights, x, features)
            return (hyperval < thresh)
        raise Exception()  # pragma: no cover

    def _apply_split_mixed(self, node, x):
        tree = self.model
        features = tree['prb_']['data']['features']

        mixed_split = node['split_mixed']
        categoric_split = mixed_split['categoric_split']
        categoric_j = categoric_split['feature'] - 1
        feature_name = features['feature_names'][categoric_j]
        val = x[feature_name]

        # missing
        if pd.isnull(val) and (tree['missingdatamode'] != 'none'):
            return categoric_split['split'][0]

        # Parallel
        if mixed_split['do_parallel']:
            parallel_split = mixed_split['parallel_split']
            thresh = parallel_split['threshold']
            # only check when this element is numeric
            if isinstance(val, float) or isinstance(val, int):
                return (val <= thresh)

        # Ordinal
        if mixed_split['do_ordinal']:
            ordinal_split = mixed_split['ordinal_split']
            ordinal_j = ordinal_split['feature'] - 1
            levels = features['ordinal_labelmap'][ordinal_j]['levels']
            if val in levels:
                ind = levels.index(val)
                return ordinal_split['split'][ind]

        # Categoric
        levels = features['categoric_labelmap'][categoric_j]['levels']
        if val in levels:
            ind = levels.index(val)
            return categoric_split['split'][ind]

        # If it has not returned in previous checks, must be unknown levels
        if tree['treat_unknown_level_missing'] and (
           tree['missingdatamode'] != 'none'):
            return categoric_split['split'][0]

        raise ValueError('Don\'t know how to handle value {0} from {1}'.format(val, feature_name))

    def _apply(self, x):
        tree = self.model
        nodes = tree['tree_']['nodes']

        node = nodes[0]
        while True:
            is_lower = None

            if node['split_type'] == 'LEAF':
                return node['id']

            elif node['split_type'] == 'MIXED':
                is_lower = self._apply_split_mixed(node, x)

            elif node['split_type'] == 'HYPERPLANE':
                is_lower = self._apply_split_hyperplane(node, x)

            assert is_lower is not None
            next_id = node['lower_child'] if is_lower else node['upper_child']
            node = nodes[next_id - 1]

    def _predict_proba(self, x):
        model = self.model
        learner_type = model['_julia_type']
        target = model['prb_']['data']['target']

        if learner_type == 'OptimalTreeClassifier':
            nodes = model['tree_']['nodes']
            leaf_id = self._apply(x)
            node = nodes[leaf_id - 1]
            preds = node['fit']['probs']
            return dict(zip(target['classes']['levels'], preds))
        elif learner_type == 'OptimalFeatureSelectionClassifier':
            # convert to probability matrix
            target = model['prb_']['data']['target']
            target_levels = target['classes']['levels']
            if 'fit_' in model:
                fit = model['fit_']
            else:
                fit = model['fits_'][0]
            if 'inner' in fit:
                fit = fit['inner']
            else:
                fit = fit['logistic_fit']
            pred = self._decision_function(fit, x)
            p = 1 / (1 + np.exp(-pred))
            return {target_levels[0]: 1 - p,  target_levels[1]: p}
        else:
            raise TypeError('`_predict_proba` is not supported for {}'.format(learner_type))

    def _predict_outcomes_policy(self, x, reward):
        tree = self.model
        nodes = tree['tree_']['nodes']
        target = tree['prb_']['data']['target']

        leaf_id = self._apply(x)
        node = nodes[leaf_id - 1]

        best_treatment = node['fit']['treatment_rank'][0] - 1
        if isinstance(reward, np.ndarray):
            return reward[best_treatment]
        else:
            return reward[target['rewards']['feature_names'][best_treatment]]

    def _predict_outcomes_prescription(self, x):
        tree = self.model
        nodes = tree['tree_']['nodes']
        features = tree['prb_']['data']['features']
        target = tree['prb_']['data']['target']

        leaf_id = self._apply(x)
        node = nodes[leaf_id - 1]

        out = dict()
        treatment_fits = node['fit']['treatment_fit']
        for t in range(len(node['fit']['treatment_rank'])):
            beta = treatment_fits[t]['beta']
            pred = float(treatment_fits[t]['offset'])
            if beta['nzind']:
                pred += self._get_hyperval(beta, x, features)
            else:
                pred = treatment_fits[t]['constant_offset']
            treatment_name = target['treatments']['classes']['levels'][t]
            out[str(treatment_name)] = pred
        return out

    def _get_display_name(self, name, ind):
        if name == '':
            return 'x' + str(ind + 1)
        else:
            return name

    def _predict_treatment_rank(self, x):
        tree = self.model
        nodes = tree['tree_']['nodes']
        learner_type = tree['_julia_type']
        target = tree['prb_']['data']['target']

        leaf_id = self._apply(x)
        node = nodes[leaf_id - 1]

        if learner_type in ['OptimalTreePolicyMinimizer',
                            'OptimalTreePolicyMaximizer']:
            return [self._get_display_name(
                target['rewards']['feature_names'][r - 1],
                r - 1) for r in node['fit']['treatment_rank']]
        else:
            raise TypeError('`predict_treatment_rank` is not supported for {}'.format(learner_type))

    def _predict_treatment_outcome(self, x):
        tree = self.model
        nodes = tree['tree_']['nodes']
        learner_type = tree['_julia_type']
        target = tree['prb_']['data']['target']

        leaf_id = self._apply(x)
        node = nodes[leaf_id - 1]

        if learner_type in ['OptimalTreePolicyMinimizer',
                            'OptimalTreePolicyMaximizer']:
            vals = node['fit']['treatment_error']
            names = [
                self._get_display_name(name, i)
                for i, name in enumerate(target['rewards']['feature_names'])
            ]
            return dict(zip(names, vals))
        else:
            raise TypeError('`predict_treatment_outcome` is not supported for {}'.format(learner_type))

    def _predict_hazard(self, x):
        tree = self.model
        nodes = tree['tree_']['nodes']
        learner_type = tree['_julia_type']

        leaf_id = self._apply(x)
        node = nodes[leaf_id - 1]

        if learner_type in ['OptimalTreeSurvivalLearner',
                            'OptimalTreeSurvivor']:
            return node['fit']['theta']
        else:
            raise TypeError('`predict_hazard` is not supported for {}'.format(learner_type))

    def _predict_expected_survival_time(self, x):
        tree = self.model
        nodes = tree['tree_']['nodes']
        learner_type = tree['_julia_type']

        leaf_id = self._apply(x)
        node = nodes[leaf_id - 1]

        if learner_type in ['OptimalTreeSurvivalLearner',
                            'OptimalTreeSurvivor']:
            return node['fit']['curve']['expected_time']
        else:
            raise TypeError('`predict_expected_survival_time` is not supported for {}'.format(learner_type))

    def _predict_tree(self, x):
        tree = self.model
        nodes = tree['tree_']['nodes']
        learner_type = tree['_julia_type']
        features = tree['prb_']['data']['features']
        target = tree['prb_']['data']['target']

        leaf_id = self._apply(x)
        node = nodes[leaf_id - 1]
        if learner_type == 'OptimalTreeClassifier':
            class_ind = node['fit']['class'] - 1
            pred = target['classes']['levels'][class_ind]
            return pred
        elif learner_type == 'OptimalTreeRegressor':
            beta = node['fit']['beta']
            pred = float(node['fit']['offset'])
            if beta['nzind']:
                pred += self._get_hyperval(beta, x, features)
            return pred
        elif learner_type in ['OptimalTreePrescriptionMinimizer',
                              'OptimalTreePrescriptionMaximizer']:
            treatment_fits = node['fit']['treatment_fit']
            best_treatment = node['fit']['treatment_rank'][0] - 1
            pres = target['treatments']['classes']['levels'][best_treatment]
            beta = treatment_fits[best_treatment]['beta']

            pred = float(treatment_fits[best_treatment]['offset'])
            if beta['nzind']:
                pred += self._get_hyperval(beta, x, features)
            else:
                pred = treatment_fits[best_treatment]['constant_offset']
            return {'pres': pres, 'pred': pred}

        elif learner_type in ['OptimalTreePolicyMinimizer',
                              'OptimalTreePolicyMaximizer']:
            best_treatment = node['fit']['treatment_rank'][0] - 1
            pres = target['rewards']['feature_names'][best_treatment]
            pres = self._get_display_name(pres, best_treatment)
            return pres
        else:
            raise TypeError('`predict` is not supported for {}'.format(learner_type))

    def _decision_function(self, fit, x):
        model = self.model
        features = model['prb_']['data']['features']
        beta = fit['beta']
        pred = float(fit['offset'])
        if beta['nzind']:
            pred += self._get_hyperval(beta, x, features)
        return pred

    def _predict_ofs(self, x):
        model = self.model
        learner_type = model['_julia_type']

        if 'fit_' in model:
            fit = model['fit_']
        else:
            fit = model['fits_'][0]
        if learner_type == 'OptimalFeatureSelectionClassifier':
            if 'inner' in fit:
                fit = fit['inner']
            else:
                fit = fit['logistic_fit']

        pred = self._decision_function(fit, x)

        if learner_type == 'OptimalFeatureSelectionClassifier':
            # convert to the class prediction
            target = model['prb_']['data']['target']
            target_levels = target['classes']['levels']
            return target_levels[0] if pred < 0 else target_levels[1]
        else:
            return pred

    def apply(self, X):
        """Return the leaf index in the Optimal Trees model into which each
        point in the features `X` falls.

        Equivalent to :meth:`interpretableai.iai.TreeLearner.apply`.

        Examples
        --------
        >>> predictor.apply(X)
        """
        tree = self.model
        learner_type = tree['_julia_type']

        out = []
        if learner_type in ['OptimalTreeClassifier',
                            'OptimalTreeRegressor',
                            'OptimalTreePrescriptionMinimizer',
                            'OptimalTreePrescriptionMaximizer',
                            'OptimalTreePolicyMinimizer',
                            'OptimalTreePolicyMaximizer',
                            'OptimalTreeSurvivalLearner',
                            'OptimalTreeSurvivor']:
            for row in iterate_samples(X):
                id_out = self._apply(row)
                out.append(id_out)
        else:
            raise TypeError('`apply` is not supported for {}'.format(learner_type))

        return out

    def predict_proba(self, X):
        """Return the probabilities of class membership predicted by the
        model for each point in the features `X`.

        Equivalent to :meth:`interpretableai.iai.ClassificationLearner.predict_proba`.

        Examples
        --------
        >>> predictor.predict_proba(X)
        """
        out = []
        for row in iterate_samples(X):
            row_out = self._predict_proba(row)
            out.append(row_out)
        return pd.DataFrame(out)

    def predict_treatment_rank(self, X):
        """Return the treatments in ranked order of effectiveness for each point
        in the features `X` as predicted by the Optimal Policy Tree model.

        Equivalent to :meth:`interpretableai.iai.PolicyLearner.predict_treatment_rank`.

        Examples
        --------
        >>> predictor.predict_treatment_rank(X)
        """
        out = []
        for row in iterate_samples(X):
            row_out = self._predict_treatment_rank(row)
            out.append(row_out)
        return out

    def predict_treatment_outcome(self, X):
        """Return the estimated quality of each treatment in the trained Optimal
        Policy Tree model for each point in the features `X`.

        Equivalent to :meth:`interpretableai.iai.PolicyLearner.predict_treatment_outcome`.

        Examples
        --------
        >>> predictor.predict_treatment_outcome(X)
        """
        out = []
        for row in iterate_samples(X):
            row_out = self._predict_treatment_outcome(row)
            out.append(row_out)
        return pd.DataFrame(out)

    def predict_outcomes(self, X, *args):
        """The behavior of this function depends on the type of model.

        Examples
        --------
        For Optimal Prescriptive Trees, return the predicted outcome for each
        point in the features `X` for each treatment made by the model.

        Equivalent to :meth:`interpretableai.iai.PrescriptionLearner.predict_outcomes`.

        >>> predictor.predict_outcomes(X)

        For Optimal Policy Trees, return the outcome for each point in the
        features `X` from `rewards` under the prescriptions made by the
        model. The `rewards` can be a numpy matrix, a pandas dataframe, or
        a `list` of `dict`s as it would be represented as JSON.

        Equivalent to :meth:`interpretableai.iai.PolicyLearner.predict_outcomes`.

        >>> predictor.predict_outcomes(X, rewards)
        """
        tree = self.model
        learner_type = tree['_julia_type']

        out = []
        if learner_type in ['OptimalTreePrescriptionMinimizer',
                            'OptimalTreePrescriptionMaximizer']:
            for row in iterate_samples(X):
                row_out = self._predict_outcomes_prescription(row)
                out.append(row_out)
            return pd.DataFrame(out)

        elif learner_type in ['OptimalTreePolicyMinimizer',
                              'OptimalTreePolicyMaximizer']:
            if len(args) != 1:
                raise TypeError('`predict_outcomes` for {} takes two arguments: `X` and `rewards`'.format(learner_type))
            rewards = args[0]
            for i, row in enumerate(iterate_samples(X)):
                reward = get_sample_at_i(rewards, i)
                row_out = self._predict_outcomes_policy(row, reward)
                out.append(row_out)
            return out
        else:
            raise TypeError('`predict_outcomes` is not supported for {}'.format(learner_type))

    def predict_hazard(self, X):
        """Return the fitted hazard coefficient estimate made by the Optimal
        Survival Tree model for each point in the data `X`.

        Equivalent to :meth:`interpretableai.iai.SurvivalLearner.predict_hazard`.

        Examples
        --------
        >>> predictor.predict_hazard(X)
        """
        out = []
        for row in iterate_samples(X):
            row_out = self._predict_hazard(row)
            out.append(row_out)
        return out

    def predict_expected_survival_time(self, X):
        """Return the expected survival time estimate made by the Optimal
        Survival Tree model for each point in the data `X`.

        Equivalent to :meth:`interpretableai.iai.SurvivalLearner.predict_expected_survival_time`.

        Examples
        --------
        >>> predictor.predict_expected_survival_time(X)
        """
        out = []
        for row in iterate_samples(X):
            row_out = self._predict_expected_survival_time(row)
            out.append(row_out)
        return out

    def predict(self, X):
        """Return the predictions made by the model for each point in the
        features `X`.

        Equivalent to :meth:`interpretableai.iai.SupervisedLearner.predict`.

        Examples
        --------
        >>> predictor.predict(X)
        """
        learner_type = self.model['_julia_type']

        out = []

        for row in iterate_samples(X):
            if learner_type in ['OptimalFeatureSelectionClassifier',
                                'OptimalFeatureSelectionRegressor']:
                row_out = self._predict_ofs(row)
            else:
                row_out = self._predict_tree(row)
            out.append(row_out)

        if learner_type in ['OptimalTreePrescriptionMinimizer',
                            'OptimalTreePrescriptionMaximizer']:
            return pd.DataFrame(out).pres, pd.DataFrame(out).pred
        else:
            return out
