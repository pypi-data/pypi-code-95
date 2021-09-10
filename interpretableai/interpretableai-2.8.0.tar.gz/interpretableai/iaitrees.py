from .iai import _IAI, _requires_iai_version, GridSearch
from .iaibase import (Learner, SupervisedLearner, ClassificationLearner,
                      RegressionLearner, SurvivalLearner, PrescriptionLearner,
                      PolicyLearner, SurvivalCurve)
import pandas as _pd


class TreeLearner(SupervisedLearner):
    """Abstract type encompassing all tree-based learners."""

    def get_num_nodes(self):
        """Return the number of nodes in the trained learner.

        Julia Equivalent:
        `IAI.get_num_nodes <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_num_nodes>`

        Examples
        --------
        >>> lnr.get_num_nodes(node_index)
        """
        return _IAI.get_num_nodes_convert(self._jl_obj)

    def is_leaf(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a leaf.

        Julia Equivalent:
        `IAI.is_leaf <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.is_leaf>`

        Examples
        --------
        >>> lnr.is_leaf(node_index)
        """
        return _IAI.is_leaf_convert(self._jl_obj, node_index)

    def get_depth(self, node_index):
        """Return the depth of node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_depth <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_depth>`

        Examples
        --------
        >>> lnr.get_depth(node_index)
        """
        return _IAI.get_depth_convert(self._jl_obj, node_index)

    def get_num_samples(self, node_index):
        """Return the number of training points contained in node `node_index`
        in the trained learner.

        Julia Equivalent:
        `IAI.get_num_samples <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_num_samples>`

        Examples
        --------
        >>> lnr.get_num_samples(node_index)
        """
        return _IAI.get_num_samples_convert(self._jl_obj, node_index)

    def get_lower_child(self, node_index):
        """Return the index of the lower child of node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_lower_child <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_lower_child>`

        Examples
        --------
        >>> lnr.get_lower_child(node_index)
        """
        return _IAI.get_lower_child_convert(self._jl_obj, node_index)

    def get_parent(self, node_index):
        """Return the index of the parent node of node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_parent <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_parent>`

        Examples
        --------
        >>> lnr.get_parent(node_index)
        """
        return _IAI.get_parent_convert(self._jl_obj, node_index)

    def get_upper_child(self, node_index):
        """Return the index of the upper child of node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_upper_child <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_upper_child>`

        Examples
        --------
        >>> lnr.get_upper_child(node_index)
        """
        return _IAI.get_upper_child_convert(self._jl_obj, node_index)

    def is_parallel_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a
        parallel split.

        Julia Equivalent:
        `IAI.is_parallel_split <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.is_parallel_split>`

        Examples
        --------
        >>> lnr.is_parallel_split(node_index)
        """
        return _IAI.is_parallel_split_convert(self._jl_obj, node_index)

    def is_hyperplane_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a
        hyperplane split.

        Julia Equivalent:
        `IAI.is_hyperplane_split <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.is_hyperplane_split>`

        Examples
        --------
        >>> lnr.is_hyperplane_split(node_index)
        """
        return _IAI.is_hyperplane_split_convert(self._jl_obj, node_index)

    def is_categoric_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a
        categoric split.

        Julia Equivalent:
        `IAI.is_categoric_split <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.is_categoric_split>`

        Examples
        --------
        >>> lnr.is_categoric_split(node_index)
        """
        return _IAI.is_categoric_split_convert(self._jl_obj, node_index)

    def is_ordinal_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is an
        ordinal split.

        Julia Equivalent:
        `IAI.is_ordinal_split <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.is_ordinal_split>`

        Examples
        --------
        >>> lnr.is_ordinal_split(node_index)
        """
        return _IAI.is_ordinal_split_convert(self._jl_obj, node_index)

    def is_mixed_parallel_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a mixed
        categoric/parallel split.

        Julia Equivalent:
        `IAI.is_mixed_parallel_split <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.is_mixed_parallel_split>`

        Examples
        --------
        >>> lnr.is_mixed_parallel_split(node_index)
        """
        return _IAI.is_mixed_parallel_split_convert(self._jl_obj, node_index)

    def is_mixed_ordinal_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a mixed
        categoric/ordinal split.

        Julia Equivalent:
        `IAI.is_mixed_ordinal_split <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.is_mixed_ordinal_split>`

        Examples
        --------
        >>> lnr.is_mixed_ordinal_split(node_index)
        """
        return _IAI.is_mixed_ordinal_split_convert(self._jl_obj, node_index)

    def missing_goes_lower(self, node_index):
        """Return `True` if missing values take the lower branch at node
        `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.missing_goes_lower <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.missing_goes_lower>`

        Examples
        --------
        >>> lnr.missing_goes_lower(node_index)
        """
        return _IAI.missing_goes_lower_convert(self._jl_obj, node_index)

    def get_split_feature(self, node_index):
        """Return the feature used in the split at node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_split_feature <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_split_feature>`

        Examples
        --------
        >>> lnr.get_split_feature(node_index)
        """
        return _IAI.get_split_feature_convert(self._jl_obj, node_index)

    def get_split_threshold(self, node_index):
        """Return the threshold used in the split at node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_split_threshold <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_split_threshold>`

        Examples
        --------
        >>> lnr.get_split_threshold(node_index)
        """
        return _IAI.get_split_threshold_convert(self._jl_obj, node_index)

    def get_split_categories(self, node_index):
        """Return the categoric/ordinal information used in the split at node
        `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_split_categories <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_split_categories>`

        Examples
        --------
        >>> lnr.get_split_categories(node_index)
        """
        return _IAI.get_split_categories_convert(self._jl_obj, node_index)

    def get_split_weights(self, node_index):
        """Return the weights for numeric and categoric features used in the
        hyperplane split at  node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_split_weights <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_split_weights>`

        Examples
        --------
        >>> lnr.get_split_weights(node_index)
        """
        return _IAI.get_split_weights_convert(self._jl_obj, node_index)

    def apply(self, *args, **kwargs):
        """Return the leaf index in the learner into which each point in the
        features `X` falls.

        Julia Equivalent:
        `IAI.apply <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.apply>`

        Examples
        --------
        >>> lnr.apply(X)
        """
        return _IAI.apply_convert(self._jl_obj, *args, **kwargs)

    def apply_nodes(self, *args, **kwargs):
        """Return the indices of the points in the features `X` that fall into
        each node in the learner.

        Julia Equivalent:
        `IAI.apply_nodes <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.apply_nodes>`

        Examples
        --------
        >>> lnr.apply_nodes(X)
        """
        node_inds = _IAI.apply_nodes_convert(self._jl_obj, *args, **kwargs)
        return [inds - 1 for inds in node_inds]

    def decision_path(self, *args, **kwargs):
        """Return a matrix where entry `(i, j)` is `True` if the `i`th point in
        the features `X` passes through the `j`th node in the learner.

        Julia Equivalent:
        `IAI.decision_path <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.decision_path>`

        Examples
        --------
        >>> lnr.decision_path(X)
        """
        return _IAI.decision_path_convert(self._jl_obj, *args, **kwargs)

    def print_path(self, *args, **kwargs):
        """Print the decision path through the learner for each sample in the
        features `X`.

        Julia Equivalent:
        `IAI.print_path <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.print_path>`

        Examples
        --------
        >>> lnr.print_path(X)
        """
        return _IAI.print_path_convert(self._jl_obj, *args, **kwargs)

    def write_png(self, filename, **kwargs):  # pragma: no cover
        """Write learner to `filename` as a PNG image.

        Requires
        [GraphViz](http://www.graphviz.org/)
        be installed and on the system `PATH`.

        Julia Equivalent:
        `IAI.write_png <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.write_png>`

        Examples
        --------
        >>> lnr.write_png(filename, **kwargs)
        """
        return _IAI.write_png_convert(filename, self._jl_obj, **kwargs)

    def write_pdf(self, filename, **kwargs):  # pragma: no cover
        """Write learner to `filename` as a PDF image.

        Requires
        [GraphViz](http://www.graphviz.org/)
        be installed and on the system `PATH`.

        Julia Equivalent:
        `IAI.write_pdf <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.write_pdf>`

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.

        Examples
        --------
        >>> lnr.write_pdf(filename, **kwargs)
        """
        _requires_iai_version("2.1.0", "write_pdf")
        return _IAI.write_pdf_convert(filename, self._jl_obj, **kwargs)

    def write_svg(self, filename, **kwargs):  # pragma: no cover
        """Write learner to `filename` as an SVG image.

        Requires
        [GraphViz](http://www.graphviz.org/)
        be installed and on the system `PATH`.

        Julia Equivalent:
        `IAI.write_svg <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.write_svg>`

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.

        Examples
        --------
        >>> lnr.write_svg(filename, **kwargs)
        """
        _requires_iai_version("2.1.0", "write_svg")
        return _IAI.write_svg_convert(filename, self._jl_obj, **kwargs)

    def write_dot(self, filename, **kwargs):
        """Write learner to `filename` in
        [.dot format](http://www.graphviz.org/content/dot-language/).

        Julia Equivalent:
        `IAI.write_dot <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.write_dot>`

        Examples
        --------
        >>> lnr.write_dot(filename, **kwargs)
        """
        return _IAI.write_dot_convert(filename, self._jl_obj, **kwargs)

    def write_html(self, filename, **kwargs):
        """Write interactive browser visualization of learner to `filename` as
        HTML.

        Julia Equivalent:
        `IAI.write_html <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.write_html>`

        Examples
        --------
        >>> lnr.write_html(filename, **kwargs)
        """
        return _IAI.write_html_convert(filename, self._jl_obj, **kwargs)

    def show_in_browser(self, **kwargs):  # pragma: no cover
        """Show interactive visualization of learner in default browser.

        Julia Equivalent:
        `IAI.show_in_browser <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.show_in_browser>`

        Examples
        --------
        >>> lnr.show_in_browser(**kwargs)
        """
        return _IAI.show_in_browser_convert(self._jl_obj, **kwargs)

    def write_questionnaire(self, filename, **kwargs):
        """Write interactive questionnaire based on learner to `filename` as
        HTML.

        Julia Equivalent:
        `IAI.write_questionnaire <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.write_questionnaire>`

        Examples
        --------
        >>> lnr.write_questionnaire(filename, **kwargs)
        """
        return _IAI.write_questionnaire_convert(filename, self._jl_obj,
                                                **kwargs)

    def show_questionnaire(self, **kwargs):  # pragma: no cover
        """Show interactive questionnaire based on learner in default browser.

        Julia Equivalent:
        `IAI.show_questionnaire <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.show_questionnaire>`

        Examples
        --------
        >>> lnr.show_questionnaire(**kwargs)
        """
        return _IAI.show_questionnaire_convert(self._jl_obj, **kwargs)

    def variable_importance_similarity(self, new_lnr, *args, **kwargs):
        """Calculate similarity between this learner and another tree learner
        using variable importance scores.

        Julia Equivalent:
        `IAI.variable_importance_similarity <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.variable_importance_similarity>`

        Examples
        --------
        Calculate similarity scores between the final tree in this learner and
        all trees in `new_lnr`

        >>> lnr.variable_importance_similarity(new_lnr)

        Calculate similarity scores between the final tree in this learner and
        all trees in `new_lnr` using the data `X` and `y` with `criterion`

        >>> lnr.variable_importance_similarity(new_lnr, X, y,
                                               criterion='default')

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "variable_importance_similarity")
        if not isinstance(new_lnr, Learner):
            raise TypeError("new_lnr is not a Learner")
        return _IAI.variable_importance_similarity_convert(
            self._jl_obj, new_lnr._jl_obj, *args, **kwargs)

    def get_tree(self, index):
        """Return a copy of the learner that uses the tree at `index` rather
        than the tree with the best training objective.

        Julia Equivalent:
        `IAI.get_tree <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_tree>`

        Examples
        --------
        >>> lnr.get_tree(index)

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "get_tree")
        jl_obj = _IAI.get_tree(self._jl_obj, index)
        new_lnr = type(self)()
        Learner.__init__(new_lnr, jl_obj)
        return new_lnr


class ClassificationTreeLearner(ClassificationLearner):
    """Abstract type encompassing all tree-based learners with classification
    leaves.
    """

    def get_classification_label(self, node_index, **kwargs):
        """Return the predicted label at node `node_index` in the trained
        learner.

        Julia Equivalent:
        `IAI.get_classification_label <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_classification_label>`

        Examples
        --------
        >>> lnr.get_classification_label(node_index)
        """
        return _IAI.get_classification_label_convert(self._jl_obj, node_index,
                                                     **kwargs)

    def get_classification_proba(self, node_index, **kwargs):
        """Return the predicted probabilities of class membership at node
        `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_classification_proba <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_classification_proba>`

        Examples
        --------
        >>> lnr.get_classification_proba(node_index)
        """
        return _IAI.get_classification_proba_convert(self._jl_obj, node_index,
                                                     **kwargs)

    def get_regression_constant(self, node_index, **kwargs):
        """Return the constant term in the logistic regression prediction at
        node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_regression_constant <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_regression_constant-Tuple%7BTreeLearner%7BIAIBase.ClassificationTask%7D%2CInt64%7D>`

        Examples
        --------
        >>> lnr.get_regression_constant(node_index)

        Compatibility
        -------------
        Requires IAI version 3.0 or higher.
        """
        _requires_iai_version("3.0.0", "get_regression_constant")
        return _IAI.get_regression_constant_convert(self._jl_obj, node_index,
                                                    **kwargs)

    def get_regression_weights(self, node_index, **kwargs):
        """Return the weights for each feature in the logistic regression
        prediction at node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_regression_weights <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_regression_weights-Tuple%7BTreeLearner%7BIAIBase.ClassificationTask%7D%2CInt64%7D>`

        Examples
        --------
        >>> lnr.get_regression_weights(node_index)

        Compatibility
        -------------
        Requires IAI version 3.0 or higher.
        """
        _requires_iai_version("3.0.0", "get_regression_constant")
        return _IAI.get_regression_weights_convert(self._jl_obj, node_index,
                                                   **kwargs)

    def set_threshold(self, *args, **kwargs):
        """For a binary classification problem, update the the predicted labels
        in the leaves of the learner to predict `label` only if the predicted
        probability is at least `threshold`. If `simplify` is `True`, the tree
        will be simplified after all changes have been made.

        Julia Equivalent:
        `IAI.set_threshold! <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.set_threshold!>`

        Examples
        --------
        >>> lnr.set_threshold(label, threshold, simplify=False)
        """
        _IAI.set_threshold_convert(self._jl_obj, *args, **kwargs)
        return self

    def set_display_label(self, *args, **kwargs):
        """Show the probability of `display_label` when visualizing learner.

        Julia Equivalent:
        `IAI.set_display_label! <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.set_display_label!>`

        Examples
        --------
        >>> lnr.set_display_label(display_label)
        """
        _IAI.set_display_label_convert(self._jl_obj, *args, **kwargs)
        return self

    def reset_display_label(self):
        """Reset the predicted probability displayed to be that of the
        predicted label when visualizing learner.

        Julia Equivalent:
        `IAI.reset_display_label! <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.reset_display_label!>`

        Examples
        --------
        >>> lnr.reset_display_label(display_label)
        """
        _IAI.reset_display_label_convert(self._jl_obj)
        return self


class RegressionTreeLearner(RegressionLearner):
    """Abstract type encompassing all tree-based learners with regression
    leaves.
    """

    def get_regression_constant(self, node_index, **kwargs):
        """Return the constant term in the regression prediction at node
        `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_regression_constant <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_regression_constant-Tuple%7BTreeLearner%7BIAIBase.RegressionTask%7D%2CInt64%7D>`

        Examples
        --------
        >>> lnr.get_regression_constant(node_index)
        """
        return _IAI.get_regression_constant_convert(self._jl_obj, node_index,
                                                    **kwargs)

    def get_regression_weights(self, node_index, **kwargs):
        """Return the weights for each feature in the regression prediction at
        node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_regression_weights <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_regression_weights-Tuple%7BTreeLearner%7BIAIBase.RegressionTask%7D%2CInt64%7D>`

        Examples
        --------
        >>> lnr.get_regression_weights(node_index)
        """
        return _IAI.get_regression_weights_convert(self._jl_obj, node_index,
                                                   **kwargs)


class SurvivalTreeLearner(SurvivalLearner):
    """Abstract type encompassing all tree-based learners with survival leaves.
    """

    def get_survival_curve(self, node_index, **kwargs):
        """Return the
        `SurvivalCurve <https://docs.interpretable.ai/v2.2.0/IAI-Python/reference/#SurvivalCurve>`
        at node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_survival_curve <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_survival_curve>`

        Examples
        --------
        >>> lnr.get_survival_curve(node_index)
        """
        jl_curve = _IAI.get_survival_curve_convert(self._jl_obj, node_index,
                                                   **kwargs)
        return SurvivalCurve(jl_curve)

    def get_survival_expected_time(self, node_index, **kwargs):
        """Return the predicted expected survival time at node `node_index` in
        the trained learner.

        Julia Equivalent:
        `IAI.get_survival_expected_time <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_survival_expected_time>`

        Examples
        --------
        >>> lnr.get_survival_expected_time(node_index)

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "get_survival_expected_time")
        return _IAI.get_survival_expected_time_convert(self._jl_obj,
                                                       node_index, **kwargs)

    def get_survival_hazard(self, node_index, **kwargs):
        """Return the predicted hazard ratio at node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_survival_hazard <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_survival_hazard>`

        Examples
        --------
        >>> lnr.get_survival_hazard(node_index)

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "get_survival_hazard")
        return _IAI.get_survival_hazard_convert(self._jl_obj, node_index,
                                                **kwargs)


class PrescriptionTreeLearner(PrescriptionLearner):
    """Abstract type encompassing all tree-based learners with prescription
    leaves.
    """

    def get_prescription_treatment_rank(self, node_index, **kwargs):
        """Return the treatments ordered from most effective to least effective
        at node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_prescription_treatment_rank <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_prescription_treatment_rank>`

        Examples
        --------
        >>> lnr.get_prescription_treatment_rank(node_index)
        """
        return _IAI.get_prescription_treatment_rank_convert(self._jl_obj,
                                                            node_index,
                                                            **kwargs)

    def get_regression_constant(self, node_index, treatment, **kwargs):
        """Return the constant in the regression prediction for `treatment` at
        node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_regression_constant <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_regression_constant-Tuple%7BTreeLearner%7BIAIBase.PrescriptionTask%7BO%7D%7D%2520where%2520O%2CInt64%2CAny%7D>`

        Examples
        --------
        >>> lnr.get_regression_constant(node_index, treatment)
        """
        return _IAI.get_regression_constant_convert(self._jl_obj, node_index,
                                                    treatment, **kwargs)

    def get_regression_weights(self, node_index, treatment, **kwargs):
        """Return the weights for each feature in the regression prediction for
        `treatment` at node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_regression_weights <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_regression_weights-Tuple%7BTreeLearner%7BIAIBase.PrescriptionTask%7BO%7D%7D%2520where%2520O%2CInt64%2CAny%7D>`

        Examples
        --------
        >>> lnr.get_regression_weights(node_index, treatment)
        """
        return _IAI.get_regression_weights_convert(self._jl_obj, node_index,
                                                   treatment, **kwargs)


class PolicyTreeLearner(PolicyLearner):
    """Abstract type encompassing all tree-based learners with policy leaves.
    """

    def get_policy_treatment_rank(self, node_index, **kwargs):
        """Return the treatments ordered from most effective to least effective
        at node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_policy_treatment_rank <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_policy_treatment_rank>`

        Examples
        --------
        >>> lnr.get_policy_treatment_rank(node_index)

        Compatibility
        -------------
        Requires IAI version 2.0 or higher.
        """
        _requires_iai_version("2.0.0", "get_policy_treatment_rank")
        return _IAI.get_policy_treatment_rank_convert(self._jl_obj, node_index,
                                                      **kwargs)

    def get_policy_treatment_outcome(self, node_index, **kwargs):
        """Return the quality of the treatments at node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_policy_treatment_outcome <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_policy_treatment_outcome>`

        Examples
        --------
        >>> lnr.get_policy_treatment_outcome(node_index)

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "get_policy_treatment_outcome")
        return _IAI.get_policy_treatment_outcome_convert(self._jl_obj,
                                                         node_index, **kwargs)


class AbstractVisualization():
    """Abstract type encompassing objects related to visualization. """
    def __init__(self, jl_obj):
        self._jl_obj = jl_obj

    def __repr__(self):
        return _IAI.string(self._jl_obj)

    def _repr_html_(self):
        return _IAI.to_html(self._jl_obj)

    def write_html(self, filename, **kwargs):
        """Write interactive browser visualization to `filename` as HTML.

        Julia Equivalent:
        `IAI.write_html <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.write_html>`

        Examples
        --------
        >>> treeplot.write_html(filename, **kwargs)
        """
        return _IAI.write_html_convert(filename, self._jl_obj, **kwargs)

    def show_in_browser(self, **kwargs):  # pragma: no cover
        """Show interactive visualization in default browser.

        Julia Equivalent:
        `IAI.show_in_browser <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.show_in_browser>`

        Examples
        --------
        >>> treeplot.show_in_browser(**kwargs)
        """
        return _IAI.show_in_browser_convert(self._jl_obj, **kwargs)


class TreePlot(AbstractVisualization):
    """Specify an interactive tree visualization of `lnr`.

    Julia Equivalent:
    `IAI.TreePlot <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.TreePlot>`

    Examples
    --------
    >>> iai.TreePlot(lnr, **kwargs)

    Parameters
    ----------
    Refer to the
    `Julia documentation on advanced tree visualization <https://docs.interpretable.ai/v2.2.0/IAITrees/advanced/#Advanced-Visualization-1>`
    for available parameters.

    Compatibility
    -------------
    Requires IAI version 1.1 or higher.
    """
    def __init__(self, lnr, *args, **kwargs):
        _requires_iai_version("1.1.0", "TreePlot")
        jl_obj = _IAI.TreePlot_convert(lnr._jl_obj, *args, **kwargs)
        super().__init__(jl_obj)


class Questionnaire(AbstractVisualization):
    """Specify an interactive questionnaire of `lnr`.

    Julia Equivalent:
    `IAI.Questionnaire <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.Questionnaire>`

    Examples
    --------
    >>> iai.Questionnaire(lnr, **kwargs)

    Parameters
    ----------

    Refer to the
    `Julia documentation on advanced tree visualization <https://docs.interpretable.ai/v2.2.0/IAITrees/advanced/#Advanced-Visualization-1>`
    for available parameters.

    Compatibility
    -------------
    Requires IAI version 1.1 or higher.
    """
    def __init__(self, lnr, **kwargs):
        _requires_iai_version("1.1.0", "Questionnaire")
        jl_obj = _IAI.Questionnaire_convert(lnr._jl_obj, **kwargs)
        super().__init__(jl_obj)


class MultiQuestionnaire(AbstractVisualization):
    """Specify an interactive questionnaire of multiple tree learners

    Julia Equivalent:
    `IAI.MultiQuestionnaire <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.MultiQuestionnaire>`

    Examples
    --------
    Constructs an interactive questionnaire using multiple tree learners from
    specified questions. Refer to the
    `documentation on advanced tree visualization <https://docs.interpretable.ai/v2.2.0/IAI-Python/julia/#Python-Interactive-Visualizations-1>`
    for more information.

    >>> iai.MultiQuestionnaire(questions)

    Constructs an interactive questionnaire containing the final fitted learner
    from trained grid search as well as the learner found for each parameter
    combination.

    >>> iai.MultiQuestionnaire(grid)

    Compatibility
    -------------
    Requires IAI version 1.1 or higher.
    """
    def __init__(self, *args):
        if len(args) > 0 and isinstance(args[0], GridSearch):
            _requires_iai_version("2.0.0", "MultiQuestionnaire")
            args = list(args)
            grid = args.pop(0)
            jl_obj = _IAI.MultiQuestionnaire_convert(grid._jl_obj, *args)
        else:
            _requires_iai_version("1.1.0", "MultiQuestionnaire")
            jl_obj = _IAI.MultiQuestionnaire_convert(*args)
        super().__init__(jl_obj)


class MultiTreePlot(AbstractVisualization):
    """Specify an interactive tree visualization of multiple tree learners

    Julia Equivalent:
    `IAI.MultiTreePlot <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.MultiTreePlot>`

    Examples
    --------
    Constructs an interactive tree visualization using multiple tree learners
    from specified questions. Refer to the
    `documentation on advanced tree visualization <https://docs.interpretable.ai/v2.2.0/IAI-Python/julia/#Python-Interactive-Visualizations-1>`
    for more information.

    >>> iai.MultiTreePlot(questions)

    Constructs an interactive tree visualization containing the final fitted
    learner from trained grid search as well as the learner found for each
    parameter combination.

    >>> iai.MultiTreePlot(grid)

    Compatibility
    -------------
    Requires IAI version 1.1 or higher.
    """
    def __init__(self, *args):
        if len(args) > 0 and isinstance(args[0], GridSearch):
            _requires_iai_version("2.0.0", "MultiTreePlot")
            args = list(args)
            grid = args.pop(0)
            jl_obj = _IAI.MultiQuestionnaire_convert(grid._jl_obj, *args)
        else:
            _requires_iai_version("1.1.0", "MultiTreePlot")
            jl_obj = _IAI.MultiTreePlot_convert(*args)
        super().__init__(jl_obj)


class SimilarityComparison(AbstractVisualization):
    """Conduct a similarity comparison between the final tree in `orig_lnr` and
    all trees in `new_lnr` to consider the tradeoff between training
    performance and similarity to the original tree as measured by
    `deviations`.

    Refer to the
    `documentation on tree stability <https://docs.interpretable.ai/v2.2.0/IAITrees/stability/#Tree-Stability-1>`
    for more information.

    Julia Equivalent:
    `IAI.SimilarityComparison <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.SimilarityComparison>`

    Examples
    --------
    >>> iai.SimilarityComparison(orig_lnr, new_lnr, deviations)

    Compatibility
    -------------
    Requires IAI version 2.2 or higher.
    """
    def __init__(self, orig_lnr, new_lnr, *args, **kwargs):
        _requires_iai_version("2.2.0", "SimilarityComparison")
        if not isinstance(orig_lnr, TreeLearner):
            raise TypeError("orig_lnr is not a TreeLearner")
        if not isinstance(new_lnr, TreeLearner):
            raise TypeError("new_lnr is not a TreeLearner")
        jl_obj = _IAI.SimilarityComparison_convert(
            orig_lnr._jl_obj, new_lnr._jl_obj, *args, **kwargs)
        super().__init__(jl_obj)

    def get_train_errors(self, *args, **kwargs):
        """Extract the training objective value for each candidate tree in the
        comparison, where a lower value indicates a better solution.

        Julia Equivalent:
        `IAI.get_train_errors <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_train_errors>`

        Examples
        --------
        >>> lnr.get_train_errors()

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "get_train_errors")
        return _IAI.get_train_errors_convert(self._jl_obj, *args, **kwargs)

    def plot(self):
        """Plot the similarity comparison results.

        Returns a
        `matplotlib.figure.Figure <https://matplotlib.org/stable/api/figure_api.html?highlight=figure#matplotlib.figure.Figure>`
        containing the plotted results.

        In a Jupyter Notebook, the plot will be shown automatically. In a
        terminal, you can show the plot with `similarity.plot().show()`.

        Examples
        --------
        >>> similarity.plot()

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "plot")

        from julia import Main
        deviations = Main.eval("s -> s.deviations")(self._jl_obj)
        train_errors = self.get_train_errors()
        best_i = Main.eval("s -> s.best_tree_index")(self._jl_obj) - 1

        plot_data = _pd.DataFrame({'deviations': deviations,
                                   'train_errors': train_errors})
        # Add all trees
        ax = plot_data.plot(x='deviations', y='train_errors',
                            label='All trees', kind='scatter', c='C0')
        # Add best tree
        ax = plot_data.iloc[best_i:best_i + 1, :].plot(
            ax=ax, x='deviations', y='train_errors', label='Selected tree',
            kind='scatter', c='C1')

        ax.set_xlabel('Deviation from original tree (lower is better)')
        ax.set_ylabel('Training objective value (lower is better)')
        return ax.get_figure()


class StabilityAnalysis(AbstractVisualization):
    """Conduct a stability analysis of the trees in a tree learner.

    Refer to the
    `documentation on tree stability <https://docs.interpretable.ai/v2.2.0/IAITrees/stability/#Tree-Stability-1>`
    for more information.

    Julia Equivalent:
    `IAI.StabilityAnalysis <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.StabilityAnalysis>`

    Examples
    --------

    Conduct a stability analysis of the trees in `lnr`, using similarity scores
    calculated during training

    >>> iai.StabilityAnalysis(lnr)

    Conduct a stability analysis of the trees in `lnr`, using similarity scores
    calculated with the data `X`, `y` and `criterion`

    >>> iai.StabilityAnalysis(lnr, X, y, criterion='default')

    Compatibility
    -------------
    Requires IAI version 2.2 or higher.
    """
    def __init__(self, lnr, *args, **kwargs):
        _requires_iai_version("2.2.0", "StabilityAnalysis")
        if not isinstance(lnr, TreeLearner):
            raise TypeError("lnr is not a TreeLearner")
        jl_obj = _IAI.StabilityAnalysis_convert(lnr._jl_obj, *args, **kwargs)
        super().__init__(jl_obj)

    def get_stability_results(self, *args, **kwargs):
        """Return the trained trees in order of increasing objective value,
        along with their variable importance scores for each feature.

        Julia Equivalent:
        `IAI.get_stability_results <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_stability_results>`

        Examples
        --------
        >>> stability.get_stability_results()

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "get_stability_results")
        return _IAI.get_stability_results_convert(self._jl_obj, *args, **kwargs)

    def get_cluster_assignments(self, *args, **kwargs):
        """Return the indices of the trees assigned to each cluster, under the
        clustering of the best `num_trees` trees.

        Julia Equivalent:
        `IAI.get_cluster_assignments <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_cluster_assignments>`

        Examples
        --------
        >>> stability.get_cluster_assignments(num_trees)

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "get_cluster_assignments")
        return _IAI.get_cluster_assignments_convert(self._jl_obj, *args,
                                                    **kwargs)

    def get_cluster_details(self, *args, **kwargs):
        """Return the centroid information for each cluster, under the
        clustering of the best `num_trees` trees.

        Julia Equivalent:
        `IAI.get_cluster_details <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_cluster_details>`

        Examples
        --------
        >>> stability.get_cluster_details(num_trees)

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "get_cluster_details")
        return _IAI.get_cluster_details_convert(self._jl_obj, *args,
                                                **kwargs)

    def get_cluster_distances(self, *args, **kwargs):
        """Return the distances between the centroids of each pair of clusters,
        under the clustering of the best `num_trees` trees.

        Julia Equivalent:
        `IAI.get_cluster_distances <https://docs.interpretable.ai/v2.2.0/IAITrees/reference/#IAI.get_cluster_distances>`

        Examples
        --------
        >>> stability.get_cluster_distances(num_trees)

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "get_cluster_distances")
        return _IAI.get_cluster_distances_convert(self._jl_obj, *args,
                                                  **kwargs)

    def plot(self):
        """Plot the stability analysis results.

        Returns a
        `matplotlib.figure.Figure <https://matplotlib.org/stable/api/figure_api.html?highlight=figure#matplotlib.figure.Figure>`
        containing the plotted results.

        In a Jupyter Notebook, the plot will be shown automatically. In a
        terminal, you can show the plot with `stability.plot().show()`.

        Examples
        --------
        >>> stability.plot()

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "plot")

        from julia import Main
        train_errors = Main.eval("s -> s.train_errors")(self._jl_obj)
        n_clusts = Main.eval("s -> size.(s.cluster_centers, 2)")(self._jl_obj)
        cluster_r2 = Main.eval("s -> s.cluster_r2")(self._jl_obj)

        plot_data = _pd.DataFrame({'train_errors': train_errors,
                                   'n_clusts': n_clusts,
                                   'cluster_r2': cluster_r2})

        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(3, sharex=True, figsize=(6, 6))

        # Plot 1
        ax = plot_data.plot(ax=axs[0], y='train_errors', legend=False)
        ax.set_ylabel('Training objective')

        # Plot 2
        ax = plot_data.plot(ax=axs[1], y='n_clusts', legend=False)
        ax.set_ylabel('Number of clusters')

        # Plot 3
        ax = plot_data.plot(ax=axs[2], y='cluster_r2', legend=False)
        ax.set_xlabel('Trees (ordered by training objective)')
        ax.set_ylabel('Number of clusters')

        return fig
