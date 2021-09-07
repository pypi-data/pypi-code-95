import numpy as np
from tqdm import tqdm
import pandas as pd

import plotly.express as px

# ███████╗██╗  ██╗███████╗ ██████╗██╗   ██╗████████╗██╗ ██████╗ ███╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║   ██║╚══██╔══╝██║██╔═══██╗████╗  ██║
# █████╗   ╚███╔╝ █████╗  ██║     ██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔══╝   ██╔██╗ ██╔══╝  ██║     ██║   ██║   ██║   ██║██║   ██║██║╚██╗██║
# ███████╗██╔╝ ██╗███████╗╚██████╗╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║
# ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#


def _find_corner_cases(model, features_objs, mask, X, X_nr, method, target_class=0):
    # Get useless features
    useless_features = np.argwhere(np.array([feat.is_useless() for feat in features_objs])).flatten()
    # We ignore useless features (faster execution)
    indices = [(i, f) for i, f in tqdm(np.argwhere(mask)) if f not in useless_features]
    ret = []
    tq = tqdm(total=len(indices), desc=method)
    for e, (i, f) in enumerate(indices):
        if e % 5000 == 0:
            tq.update(e)
        x = X[i]
        new_values = features_objs[f].get_values_towards_change(
            x[f],
            target_class=target_class,
        )

        for nv in new_values:
            x_prime = x.copy()
            x_prime[f] = nv
            if model.predict(np.array([x_prime]))[0] == target_class:
                ret.append((x, x_prime, f, X_nr[i], i))
                break
    tq.close()
    return ret


def find_aar_corner_cases(X, ref_point, features_trend, **kwargs):
    # Mask : features below (will never be returned as an explanation by AAR) the reference point threshold
    aar_noxp_mask = (X * features_trend) < (ref_point * features_trend)
    # Find where the corner cases happen
    return _find_corner_cases(X=X, mask=aar_noxp_mask, **kwargs)


def _X_from_results(xps_results, method):
    return np.array([r['x'] for r in xps_results if r[method] is not None])


def _X_nr_from_results(xps_results, method):
    return np.array([r['x_nonrecoded'] for r in xps_results if r[method] is not None])


def compute_noexp_mask_from_results(xps_results, method):
    return _X_from_results(xps_results, method) <= 0


def compute_special_mask_from_results(xps_results, max_values, method):
    X_nr = _X_nr_from_results(xps_results, method)
    return X_nr > max_values


def find_attribution_corner_cases(xps_results, method, **kwargs):
    # Note: we are filtering non-existing explanations (None)
    # Get the X and X_nr from the results
    X = _X_from_results(xps_results, method)
    X_nr = _X_nr_from_results(xps_results, method)

    # Mask of non-positive SHAP/attributions
    noxp_mask = compute_noexp_mask_from_results(xps_results, method)

    # Find where the corner cases happen
    return _find_corner_cases(X=X, X_nr=X_nr, mask=noxp_mask, method=method, **kwargs)


def compute_corner_cases_summary(corner_cases, noexp_mask, special_mask):
    noexp = (noexp_mask).sum(axis=0)
    noexp_spec = (noexp_mask * special_mask).sum(axis=0)
    noexp_nospec = (noexp_mask * ~special_mask).sum(axis=0)
    corner_noexp = corner_cases['f'].value_counts().reindex(pd.RangeIndex(noexp_mask.shape[1]))
    corner_noexp = corner_noexp.fillna(0).values.astype(int)
    corner_noexp_spec = corner_cases[corner_cases.spec]['f'].value_counts().reindex(pd.RangeIndex(noexp_mask.shape[1]))
    corner_noexp_spec = corner_noexp_spec.fillna(0).values.astype(int)
    corner_noexp_nospec = corner_cases[~corner_cases.spec]['f'].value_counts().reindex(
        pd.RangeIndex(noexp_mask.shape[1])
    ).fillna(0).values.astype(int)
    return {
        "nb_samples":
            noexp_mask.shape[0],
        None:
            dict(
                nb_noexp=noexp_mask.sum(),
                noexp=noexp,
                corner_noexp=corner_noexp,
                corner_rate=corner_noexp / noexp,
            ),
        True:
            dict(
                nb_noexp=(noexp_mask * special_mask).sum(),
                noexp=noexp_spec,
                corner_noexp=corner_noexp_spec,
                corner_rate=corner_noexp_spec / noexp_spec,
            ),
        False:
            dict(
                nb_noexp=(noexp_mask * ~special_mask).sum(),
                noexp=noexp_nospec,
                corner_noexp=corner_noexp_nospec,
                corner_rate=corner_noexp_nospec / noexp_nospec,
            )
    }


def post_process_corner_cases(corner_cases, features_info, perc_shifter):

    corner_cases = pd.DataFrame(corner_cases, columns=['x', 'x_prime', 'f', 'x_nr', 'i'])

    corner_cases['f'] = corner_cases.f.astype(int)
    # Absolute difference vector
    corner_cases['delta'] = corner_cases.x_prime - corner_cases.x
    # Absolute difference value (single feature)
    corner_cases['delta_f'] = np.vstack(corner_cases.delta.values)[np.arange(len(corner_cases)), corner_cases.f.values]
    # Value feature f for x
    corner_cases['x_f'] = np.vstack(corner_cases.x.values)[np.arange(len(corner_cases)), corner_cases.f.values]
    # If the value is special we mark it
    corner_cases['x_f_nr'] = np.vstack(corner_cases.x_nr.values)[np.arange(len(corner_cases)), corner_cases.f.values]
    corner_cases['spec'] = corner_cases.x_f_nr.values > features_info['Max Val'].values[corner_cases.f]

    # Value feature f for x_prime
    corner_cases['x_prime_f'] = np.vstack(corner_cases.x_prime.values)[np.arange(len(corner_cases)),
                                                                       corner_cases.f.values]

    # Get percentiles points of the x's values
    corner_cases['x_f_perc'] = 100 * np.array(
        [
            perc_shifter.get_percentile(
                np.array([x_f]),
                f=int(f),
            )[0] for f, x_f in tqdm(corner_cases[['f', 'x_f']].values)
        ]
    )
    corner_cases['x_prime_f_perc'] = 100 * np.array(
        [
            perc_shifter.get_percentile(
                np.array([x_f]),
                f=int(f),
            )[0] for f, x_f in tqdm(corner_cases[['f', 'x_prime_f']].values)
        ]
    )
    # Percentile Shift
    corner_cases['perc_shift'] = np.abs(corner_cases.x_f_perc - corner_cases.x_prime_f_perc)

    # Join features
    corner_cases = corner_cases.join(features_info, on='f')

    return corner_cases


# ██████╗ ██╗      ██████╗ ████████╗
# ██╔══██╗██║     ██╔═══██╗╚══██╔══╝
# ██████╔╝██║     ██║   ██║   ██║
# ██╔═══╝ ██║     ██║   ██║   ██║
# ██║     ███████╗╚██████╔╝   ██║
# ╚═╝     ╚══════╝ ╚═════╝    ╚═╝
#


def plot_corner_cases(corner_cases, summary, special=None, CORNER_LIMIT=.1):
    prefix = 'ALL'
    if special is True:
        prefix = 'Special Only'
        corner_cases = corner_cases[corner_cases.spec].copy()
    elif special is False:
        prefix = 'NOT Special Only'
        corner_cases = corner_cases[~corner_cases.spec].copy()

    print(f'Plotting results for {len(corner_cases)} corner cases for {summary["nb_samples"]} samples.')
    print(
        f'Corner cases are happening for {len(corner_cases.i.unique()) / summary["nb_samples"] * 100}% of the rejected cutomers'
        f'Corner cases with perc_shift < 10% are happening for {len(corner_cases[corner_cases.perc_shift < CORNER_LIMIT].i.unique()) / summary["nb_samples"] * 100}% of the rejected cutomers'
    )

    fig = px.histogram(
        corner_cases,
        x='Feature',
        title=f'{prefix} - AAR SHAP Corner - Cases Features',
        hover_data=corner_cases.columns,
    )
    fig.update_layout(yaxis=dict(tickformat=',.2%', ), )
    fig.show()
    # fig = go.Figure([go.Bar(
    #     x=features_names,
    #     y=summ['corner_rate'],
    # )])
    # fig.update_layout(
    #     title=f'{prefix} - AAR SHAP Corner - Cases Features Rate (percentage)',
    #     yaxis=dict(tickformat=',.0%', ),
    # )
    # fig.show()

    px.histogram(
        corner_cases,
        x='perc_shift',
        title=f'{prefix} - AAR SHAP Corner Cases - Percentile Shifts',
        hover_data=corner_cases.columns,
    ).show()

    px.density_heatmap(
        corner_cases,
        x='Feature',
        y='perc_shift',
        nbinsy=50,
        title=f'{prefix} - AAR SHAP Corner Cases',
    ).show()

    px.density_heatmap(
        corner_cases[corner_cases.perc_shift < CORNER_LIMIT],
        x='Feature',
        y='perc_shift',
        nbinsy=50,
        title=f'{prefix} - AAR SHAP Corner Cases / ONLY with perc_shift < 10%',
    ).show()
