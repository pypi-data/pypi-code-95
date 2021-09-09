from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns

from harmoniums import SurvivalHarmonium


def _plot_weight_category(model):
    """
    Plot the weights coupling to the categorical variables.
    """
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    ticks_latent = [f"$h_{i}$" for i in range(1, model.n_hidden_units + 1)]
    hcat = sns.heatmap(
        model.W_A,
        yticklabels=model.categorical_columns,
        xticklabels=ticks_latent,
        center=0,
        cmap=cmap,
        cbar=False,
        annot=True,
    )
    hcat.set_title(r"Categorical ($W_A$)")
    hcat.set_yticklabels(
        hcat.get_yticklabels(), rotation=0,
    )
    return hcat


def _plot_bias_category(model):
    """
    Plot the bias parameters of the categorical variables.
    """
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    hcat_bias = sns.heatmap(
        model.a_A,
        yticklabels=model.categorical_columns,
        xticklabels=["bias"],
        center=0,
        cmap=cmap,
        cbar=False,
        annot=True,
    )
    hcat_bias.set_title(r"Categorical ($a_A$)")
    hcat_bias.set_yticklabels(
        hcat_bias.get_yticklabels(), rotation=0,
    )
    return hcat_bias


def _plot_weight_numeric(model):
    """
    Plot the weights coupling to the numeric variables.
    """
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    ticks_latent = [f"$h_{i}$" for i in range(1, model.n_hidden_units + 1)]
    Wmax = 0.0
    if model.W_A.shape[0] > 0:
        Wmax = max(Wmax, abs(model.W_A).max())
    if model.W_C.shape[0] > 0:
        Wmax = max(Wmax, abs(model.W_C).max())

    hnum = sns.heatmap(
        model.W_C,
        yticklabels=model.numeric_columns,
        xticklabels=ticks_latent,
        center=0,
        cmap=cmap,
        vmin=-Wmax,
        vmax=Wmax,
        annot=True,
    )
    hnum.set_title(r"Numeric ($W_C$)")
    hnum.set_yticklabels(
        hnum.get_yticklabels(), rotation=0,
    )
    return hnum


def _plot_bias_numeric(model):
    """
    Plot the bias parameters of the numeric variables.
    """
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    amax = 0.0
    if model.a_A.shape[0] > 0:
        amax = max(amax, abs(model.a_A).max())
    if model.a_C.shape[0] > 0:
        amax = max(amax, abs(model.a_C).max())

    hnum_bias = sns.heatmap(
        model.a_C,
        yticklabels=model.numeric_columns,
        xticklabels=["bias"],
        center=0,
        cmap=cmap,
        vmin=-amax,
        vmax=amax,
        annot=True,
    )
    hnum_bias.set_title(r"Numeric ($a_C$)")
    hnum_bias.set_yticklabels(
        hnum_bias.get_yticklabels(), rotation=0,
    )
    return hnum_bias


def _plot_rate_survival(model):
    """
    Plot weight and bias parameters determining rate of time-to-event variables.
    """
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    ticks_latent = [f"$h_{i}$" for i in range(1, model.n_hidden_units + 1)]
    hsurvW = sns.heatmap(
        np.concatenate([model.W_B, model.a_B], axis=1).T,
        xticklabels=model.survival_columns,
        yticklabels=ticks_latent + ["bias"],
        center=0,
        cmap=cmap,
        annot=True,
    )
    hsurvW.set_title(r"Time-to-event ($W_B$, $a_B$)")
    hsurvW.set_yticklabels(
        hsurvW.get_yticklabels(), rotation=0,
    )
    return hsurvW


def _plot_shape_survival(model):
    """
    Plot weight and bias parameters determining shape of time-to-event variables.
    """
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    ticks_latent = [f"$h_{i}$" for i in range(1, model.n_hidden_units + 1)]
    hsurvV = sns.heatmap(
        np.concatenate([model.V, model.c], axis=1).T,
        xticklabels=model.survival_columns,
        yticklabels=ticks_latent + ["bias"],
        center=0,
        cmap=cmap,
        annot=True,
    )
    hsurvV.set_title(r"Time-to-event ($V$, $c$)")
    hsurvV.set_yticklabels(
        hsurvV.get_yticklabels(), rotation=0,
    )
    return hsurvV


def plot(
    model: SurvivalHarmonium,
    show_bias: bool = False,
    show_event: bool = False,
    new_figure=True,
):
    """
    Plot the weights and biases of the model.
    """
    number_of_rows = 1
    if show_bias:
        number_of_rows += 1
    if show_event:
        number_of_rows += 1

    number_of_columns = 0
    if model.categorical_columns:
        number_of_columns += 1
    if model.numeric_columns:
        number_of_columns += 1
    if show_event:
        number_of_columns = 2

    current_panel = 1

    if new_figure:
        # Make figure of learned parameters.
        plt.rc("font", family="serif")
        plt.figure(figsize=(2 * number_of_columns, 3 * number_of_rows))

    if model.categorical_columns:
        plt.subplot(number_of_rows, number_of_columns, current_panel)
        _plot_weight_category(model)
        current_panel += 1

    if model.numeric_columns:
        plt.subplot(number_of_rows, number_of_columns, current_panel)
        _plot_weight_numeric(model)
        current_panel += 1

    if show_bias:
        if model.categorical_columns:
            plt.subplot(number_of_rows, number_of_columns, current_panel)
            _plot_bias_category(model)
            current_panel += 1

        if model.numeric_columns:
            plt.subplot(number_of_rows, number_of_columns, current_panel)
            _plot_bias_numeric(model)
            current_panel += 1

    if show_event and model.survival_columns:
        plt.subplot(number_of_rows, number_of_columns, current_panel)
        _plot_rate_survival(model)
        current_panel += 1

        plt.subplot(number_of_rows, number_of_columns, current_panel)
        _plot_shape_survival(model)
        current_panel += 1

    plt.tight_layout()
