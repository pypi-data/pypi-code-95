from numpy import linalg
from emutils.tf.metrics import cosine_distance, mahalabolis
from sklearn.metrics.pairwise import cosine_similarity
from emutils.imports import display
import time
import logging
from typing import Union, Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from tqdm import tqdm
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier

import emutils.tf as emtf
from emutils.utils import random_stability
from emutils.dsutils import process_data

from ...api import XGBWrapping
from ..api import BaseCounterfactualMethod
from .trees import get_prob_classification_forest
from .trees import get_prob_xgboost_binary
from .trees import get_prob_classification_tree
from .hinge import filter_hinge_loss
from .xgb import booster_to_skl_ensemble


class FOCUS(BaseCounterfactualMethod):
    def __init__(
        self,
        model,
        scaler=None,

        # Optimization
        num_iter: int = 1000,
        temperature: float = 1.,
        lr: float = .001,
        opt='adam',
        random_state: Union[None, int] = None,
        deterministic: bool = True,
        patience: int = None,
        early_stopping: float = 1e-5,
        limits: Tuple[float, float] = None,

        # Base term
        sigma: float = 1.,

        # Distance
        distance_weight: float = .01,
        distance_function: str = 'euclidean',
        distance_params: dict = {},

        # Diversity
        nb_diverse_counterfactuals: int = 1,
        diversity_weight: float = .01,

        # Output
        show_progress: bool = False,
        desc: str = 'FOCUS',
        ret_log: bool = True,
        ret_stats: bool = True,
        ret_trace: bool = True,
    ):
        if scaler is not None:
            raise NotImplementedError('Scaler is not implemented for FOCUS!')

        super().__init__(model, scaler)

        if tf.__version__ < '2':
            # Enable eager execution in TensorFlow 1
            logging.info('Enabling eager execution')
            tf.enable_eager_execution()

        # Check parameters
        sigma = float(sigma)
        temperature = float(temperature)
        distance_weight = float(distance_weight)

        assert sigma != 0
        assert temperature >= 0
        assert distance_weight >= 0
        assert diversity_weight >= 0
        assert lr >= 0

        # Save parameters
        self.num_iter = num_iter
        self.sigma = sigma
        self.temperature = temperature
        self.lr = lr
        self.opt = opt
        self.distance_weight = distance_weight
        self.nb_diverse_counterfactuals = nb_diverse_counterfactuals
        self.diversity_weight = diversity_weight
        self.distance_function = distance_function
        self.random_state = random_state
        self.deterministic = deterministic
        self.patience = patience
        self.early_stopping = early_stopping
        self.distance_params = distance_params
        self.limits = limits
        self.show_progress = show_progress
        self.desc = desc
        self.ret_log = ret_log
        self.ret_stats = ret_stats
        self.ret_trace = ret_trace

        # Attributes
        self._stats = None
        self._log = None

        # Set model
        self.model = model  # This is the model that will be used to predict

        # This is the model that will be used to extract the trees
        if isinstance(self.model, XGBWrapping):
            model = model.get_booster()
            # Let's convert it to SKL-like format
            model = booster_to_skl_ensemble(model)

        self.model_ = model

    def __random_stability(self):
        if self.random_state is not None:
            random_stability(self.random_state, deterministic=self.deterministic, verbose=False)

    def __get_iterator(self):
        if self.show_progress:
            iters = tqdm(range(self.num_iter), desc=self.desc)
        else:
            iters = range(self.num_iter)
        return iters

    def __get_counterfactuals(self, X, nb_diverse_counterfactuals):
        diversity_enabled = nb_diverse_counterfactuals > 1 and self.diversity_weight > 0

        start_time = time.time()

        # Random stability
        self.__random_stability()

        # Basic info
        nb_original_samples = X.shape[0]
        n_examples = X.shape[0] * nb_diverse_counterfactuals
        n_class = len(self.model_.classes_)

        # To Tensorflow
        X = process_data(X, ret_type='tf')

        if diversity_enabled:
            X = tf.repeat(X, repeats=nb_diverse_counterfactuals, axis=0)

        # Transform class names into indexes (not always necessary)
        ground_truth = self.model.predict(X.numpy())
        class_index = np.zeros(n_examples, dtype=np.int64)
        for i, class_name in enumerate(self.model_.classes_):
            mask = np.equal(ground_truth, class_name)
            class_index[mask] = i
        # Get the example class index for later
        class_index = tf.constant(class_index, dtype=tf.int64)
        example_range = tf.constant(np.arange(n_examples, dtype=np.int64))
        example_class_index = tf.stack((example_range, class_index), axis=1)

        # These will be our perturbed features
        X_perturbed = tf.Variable(initial_value=X, name='perturbed_features', trainable=True)

        def prob_from_input(X_perturbed, sigma, temperature):
            if isinstance(self.model_, DecisionTreeClassifier):
                return get_prob_classification_tree(self.model_, X_perturbed, sigma=sigma)
            elif isinstance(self.model_, (AdaBoostClassifier, RandomForestClassifier)):
                return get_prob_classification_forest(self.model_, X_perturbed, sigma=sigma, temperature=temperature)
            else:
                return get_prob_xgboost_binary(self.model_, X_perturbed, sigma=sigma)

        # Create optimizer
        optimizer = tf.keras.optimizers.get(dict(
            class_name=self.opt,
            config=dict(learning_rate=self.lr),
        ))

        # Setup neeede variables
        sigma = np.full(n_examples, self.sigma)
        temperature = np.full(n_examples, self.temperature)
        distance_weight = np.full(n_examples, self.distance_weight)
        indicator = np.ones(n_examples)
        best_X_perturbed = np.full(X_perturbed.shape, np.nan)
        best_distance = np.full(n_examples, np.inf)
        perturb_iteration_found = np.full(n_examples, np.inf)
        minimization_log = []
        minimization_trace = []
        last_nb_counter = 0
        nb_counter = 0
        iter_since_last_flip = 0
        iter_since_last_improve = 0
        loss = None
        loss_improvement = tf.convert_to_tensor(np.inf)

        for i in self.__get_iterator():
            with tf.GradientTape(persistent=True) as t:
                # First part of the loss (change of prediction)
                p_model = filter_hinge_loss(
                    n_class,
                    indicator,
                    X_perturbed,
                    sigma,
                    temperature,
                    model_fn=prob_from_input,
                )
                approx_prob = tf.gather_nd(p_model, example_class_index)
                hinge_approx_prob = indicator * approx_prob

                prev_loss = loss

                # Base loss
                raw_loss = hinge_approx_prob

                # Second part of the loss (distance)
                if self.distance_weight > 0:
                    distance = emtf.metrics.dist(
                        X_perturbed,
                        X,
                        metric=self.distance_function,
                        stable_approx=True,
                        **self.distance_params,
                    )
                    raw_loss += distance_weight * distance

                loss = tf.reduce_mean(raw_loss)

                # Third part of the loss (diversity)
                if diversity_enabled:
                    diversity = tf.reduce_mean(
                        tf.stack(
                            [
                                # DPP
                                tf.linalg.det(
                                    1 / (
                                        1 + emtf.metrics.cdist(
                                            X=X_perturbed[i * nb_diverse_counterfactuals:
                                                          (i + 1) * nb_diverse_counterfactuals],
                                            metric=self.distance_function,
                                            stable_approx=True,
                                            stable_diag=True,
                                            **self.distance_params,
                                        )
                                    ) + tf.cast(
                                        tf.linalg.diag(tf.fill((nb_diverse_counterfactuals, ), 1e-4)),
                                        dtype=X_perturbed.dtype
                                    )
                                ) for i in range(nb_original_samples)
                            ],
                            axis=0
                        )
                    )
                    loss += diversity * self.diversity_weight

                logging.info(
                    f'Loss {loss.numpy()} = H {tf.reduce_mean(hinge_approx_prob).numpy()} + Dist {tf.reduce_mean(distance * distance_weight).numpy()} + Div {diversity.numpy()}'
                )

                if prev_loss is not None:
                    loss_improvement = tf.math.abs(loss - prev_loss)
                    if loss_improvement < self.early_stopping:
                        iter_since_last_improve += 1
                    else:
                        iter_since_last_improve = 0

                # Compute the gradient
                grad = t.gradient(loss, [X_perturbed])
                # logging.info(f"Gradient : {grad}")

                # Check for gradient instabilities
                if tf.math.reduce_any(tf.math.is_nan(grad) | tf.math.is_inf(grad)):
                    logging.error('Gradient is NaN or INF!!')

                # Optimize
                optimizer.apply_gradients(
                    zip(grad, [X_perturbed]),
                    # global_step=tf.train.get_or_create_global_step(), # I don't think we need this
                )
                # logging.info(f"Counterfactuals : {X_perturbed}")

                # And make sure perturbed values are between the limits (if any)
                if self.limits is not None:
                    X_perturbed.assign(tf.math.minimum(self.limits[1], tf.math.maximum(self.limits[0], X_perturbed)))

                # Compute the actual distance (non-approximated)
                true_distance = emtf.metrics.dist(
                    X_perturbed,
                    X,
                    metric=self.distance_function,
                    stable_approx=False,
                    **self.distance_params,
                ).numpy()

                # Check what flipped and what not
                cur_predict = self.model.predict(X_perturbed.numpy())
                mask_flipped = np.not_equal(ground_truth, cur_predict)  # did prediction flip?
                idx_flipped = np.argwhere(mask_flipped).flatten()

                # Update indicator
                indicator = np.equal(ground_truth, cur_predict).astype(np.float64)

                # Find which samples improved
                mask_smaller_dist = true_distance < best_distance  # is dist < previous best dist?

                # Update distance
                dist_temp = best_distance.copy()
                dist_temp[mask_flipped] = true_distance[mask_flipped]
                if diversity_enabled:
                    best_distance = dist_temp
                else:
                    best_distance[mask_smaller_dist] = dist_temp[mask_smaller_dist]

                # Update counterfactual
                X_perturb_temp = best_X_perturbed.copy()
                X_perturb_temp[mask_flipped] = X_perturbed[mask_flipped]
                if diversity_enabled:
                    best_X_perturbed = X_perturb_temp
                else:
                    best_X_perturbed[mask_smaller_dist] = X_perturb_temp[mask_smaller_dist]

                # Update trace
                if self.ret_trace:
                    minimization_trace.append(X_perturbed.numpy())

                # Update stats
                if self.ret_stats:
                    perturb_iteration_found[idx_flipped] = np.minimum(i + 1, perturb_iteration_found[idx_flipped])

                # Update log
                if self.ret_log:
                    last_nb_counter = nb_counter
                    nb_counter = mask_flipped.sum()
                    nb_unchanged_ever = np.isinf(best_distance).sum()
                    avg_distance = tf.reduce_mean(distance).numpy()
                    avg_counter_dist = np.mean(best_distance[~np.isinf(best_distance)]) if nb_counter > 0 else np.inf

                    minimization_log.append(
                        dict(
                            iteration=i,
                            loss=loss.numpy(),
                            loss_improvement=loss_improvement.numpy(),
                            counter=nb_counter,
                            not_counter=X.shape[0] - nb_counter,
                            never_changed=nb_unchanged_ever,
                            prob=tf.reduce_mean(approx_prob).numpy(),
                            avg_cur_dist=avg_distance,
                            avg_counter_dist=avg_counter_dist,
                            sigma=np.amax(sigma),
                            temp=np.amax(temperature),
                            time_passed=time.time() - start_time,
                            iter_since_last_flip=iter_since_last_flip,
                        )
                    )

                    # Update last flip
                    if nb_counter > last_nb_counter:
                        iter_since_last_flip = 0
                    else:
                        iter_since_last_flip += 1

                # Early stopping
                if self.patience is not None:
                    if iter_since_last_improve > self.patience:
                        break

        # Return
        if self.ret_log:
            self._log = pd.DataFrame(minimization_log)
        if self.ret_stats:
            self._stats = pd.DataFrame({'iter_found': perturb_iteration_found, 'best_distance': best_distance})
        if self.ret_trace:
            self._trace = np.array(minimization_trace)

        return best_X_perturbed

    def get_counterfactuals(self, X):
        return self.__get_counterfactuals(X, nb_diverse_counterfactuals=1)

    def get_diverse_counterfactuals(self, X):
        return self.__get_counterfactuals(X, nb_diverse_counterfactuals=self.nb_diverse_counterfactuals).reshape(
            X.shape[0], self.nb_diverse_counterfactuals, -1
        )

    def get_log(self):
        return self._log

    def get_stats(self):
        return self._stats


# %%

# %%
