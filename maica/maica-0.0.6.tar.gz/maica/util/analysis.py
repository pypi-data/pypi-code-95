"""
Analysis
--------
The ``maica.util.analysis`` module contains useful functions to analyze prediction results
of the machine learning algorithms.
"""


import numpy


def get_target_dist(targets: numpy.ndarray,
                    n_bins: int = 10):
    """
    Get a histogram of the target values in ``targets``. It returns bins and labels of the histogram.
    This function is useful to analyze the prediction results based on the target distribution for each range.

    :param targets: (*numpy.ndarray*) Target values of the dataset.
    :param n_bins: (*int*) The number of bins in the histogram (*default* = 10).
    :return: Lists of the bins and the labels of the histogram.
    """

    __targets = targets.flatten()
    bins = numpy.zeros(n_bins)

    # Get labels of the bins.
    targets_min = numpy.min(__targets)
    targets_max = numpy.max(__targets)
    label_bins = numpy.linspace(targets_min, targets_max, n_bins + 1)

    # Compute the number of data for each bin.
    for i in range(0, __targets.shape[0]):
        included = False

        for j in range(0, label_bins.shape[0] - 1):
            if label_bins[j] <= __targets[i] < label_bins[j + 1]:
                bins[j] += 1
                included = True
                break

        # If the target data belongs to the last bin.
        if not included:
            bins[n_bins - 1] += 1

    return bins.tolist(), label_bins.tolist()


def get_error_dist(targets: numpy.ndarray,
                   preds: numpy.ndarray,
                   n_ranges: int = 10):
    """
    Compute mean of prediction errors for each range of the target values in ``targets``.
    The prediction error is calculated by mean absolute error (MAE) between ``targets`` and ``preds``.
    This function is useful to analyze the prediction accuracy for each range of the target values.
    The prediction error of the :math:`k^{th}` range is calculated by:

    .. math::
        error_k = \\frac{1}{|S_k|} \sum_{i \in S_K} |y_i - y_i^{'}|,

    where :math:`S_k` is a set of indices of the data in the :math:`k^{th}` range,
    and :math:`y_i^{'}` is the predicted value of the input data :math:`\mathbf{x}_i`.

    :param targets: (*numpy.ndarray*) Target values of the prediction.
    :param preds: (*numpy.ndarray*) Predicted values.
    :param n_ranges: (*int*) The number of sections to split the range of the target values (*default* = 10).
    :return: Mean of errors and labels for each target range.
    """

    __targets = targets.flatten()
    __preds = preds.flatten()
    errors = numpy.zeros(n_ranges)
    bins = numpy.zeros(n_ranges)

    # Calculate ranges of bins.
    targets_min = numpy.min(__targets)
    targets_max = numpy.max(__targets)
    labels = numpy.linspace(targets_min, targets_max, n_ranges + 1)

    # Compute the error and the number of data for each bin.
    for i in range(0, __targets.shape[0]):
        included = False

        for j in range(0, labels.shape[0] - 1):
            if labels[j] <= __targets[i] < labels[j + 1]:
                errors[j] += numpy.abs(__targets[i] - __preds[i])
                bins[j] += 1
                included = True
                break

        # If the target data belongs to the last bin.
        if not included:
            errors[n_ranges - 1] += numpy.abs(__targets[i] - __preds[i])
            bins[n_ranges - 1] += 1

    # Calculate the mean of the errors for each bin.
    for i in range(0, n_ranges):
        if bins[i] == 0:
            errors[i] = 0
        else:
            errors[i] /= bins[i]

    return errors.tolist(), labels.tolist()
