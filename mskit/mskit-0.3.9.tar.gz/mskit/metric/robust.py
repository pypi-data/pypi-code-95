import numpy as np
import scipy.stats
import sklearn


def iqr(value: np.ndarray):
    return np.percentile(value, 75) - np.percentile(value, 25)


def cv(value_array: np.ndarray, min_quant_value_num=3, std_ddof=1, make_percentage=True, keep_na=False, decimal_place=None, return_iqr=False):
    """
    :param value_array: A two-dimensional array with rows as sample and cols as replicates. CV will be performed to each row (dim 0)
    :param min_quant_value_num: Minimum number of non-NA values
    :param std_ddof: ddof for std
    :param make_percentage: If true, CVs will be multi with 100, else nothing will do. Default True
    :param keep_na: Whether to return NAs for those CV-unavailable samples. If True, the returned CVs will have the same size as input samples. Default False
    :param decimal_place:
    :param return_iqr: Whether to return IQR of calulated CVs. If True, a tuple like (cvs, iqr) will be returned, otherwise cvs only. Default False
    """
    if len(value_array.shape) != 2:
        raise ValueError(f'Calc CV would expects a two-dim array with sample as rows and replicates as cols. Current input array has {len(value_array.shape)} dim')
    sample_num, rep_num = value_array.shape
    if min_quant_value_num > rep_num:
        min_quant_value_num = rep_num
    cv_avail_value_idx = np.where((rep_num - np.isnan(value_array).sum(axis=1)) >= min_quant_value_num)[0]
    cv_avail_values = value_array[cv_avail_value_idx]
    cvs = np.nanstd(cv_avail_values, axis=1, ddof=std_ddof) / np.nanmean(cv_avail_values, axis=1)
    if make_percentage:
        cvs = cvs * 100
    if keep_na:
        temp = np.zeros(sample_num)
        temp.fill(np.nan)
        temp[cv_avail_value_idx] = cvs
        cvs = temp.copy()
    return cvs


def count_missing_values(value_array: np.ndarray, keep_all_na_row=True):
    mvs = np.sum(np.isnan(value_array), axis=1)
    return mvs


def fwhm(values: np.ndarray, est_x_num=1e3):
    """
    :return: A tuple as (FWHM value, APEX point, Max estimated Y, KDE func)
    """
    sorted_values = np.sort(values)
    kde = scipy.stats.kde.gaussian_kde(sorted_values)
    kde_x = np.linspace(sorted_values[0], sorted_values[-1], int(est_x_num))
    kde_y = kde(kde_x)
    max_est_y = np.max(kde_y)
    apex_x_idx = np.argmax(kde_y)
    fwhm_min_idx = np.where(kde_y[:apex_x_idx] < kde_y[apex_x_idx] / 2)[0][-1]
    fwhm_max_idx = np.where(kde_y[apex_x_idx:] < kde_y[apex_x_idx] / 2)[0][0] + apex_x_idx
    apex_point = kde_x[apex_x_idx]
    fwhm_value = kde_x[fwhm_max_idx] - kde_x[fwhm_min_idx]
    return fwhm_value, apex_point, max_est_y, kde


# def pca():
#     cond_quant_df = quant_df[conditions].dropna(how='any').copy()
#     pca_input_values = cond_quant_df.values.T
#     pca = sklearn.decomposition.PCA(n_components=2).fit(pca_input_values)
#     component_var = pca.explained_variance_ratio_
#     transformed_values = pca.transform(pca_input_values)
