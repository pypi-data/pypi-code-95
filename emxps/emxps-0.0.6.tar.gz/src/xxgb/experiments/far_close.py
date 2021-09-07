import scipy
import scipy.spatial
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from emutils.utils import batch_process
from emutils.geometry import get_metric_name_and_params, pairwise_distance

sp = scipy

FAR_CLOSE_NORMALIZATION = ['euclidean', 'cityblock', 'percshift']

# ███████╗██╗  ██╗███████╗ ██████╗██╗   ██╗████████╗██╗ ██████╗ ███╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║   ██║╚══██╔══╝██║██╔═══██╗████╗  ██║
# █████╗   ╚███╔╝ █████╗  ██║     ██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔══╝   ██╔██╗ ██╔══╝  ██║     ██║   ██║   ██║   ██║██║   ██║██║╚██╗██║
# ███████╗██╔╝ ██╗███████╗╚██████╗╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║
# ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#


def generate_points_set(
    X_good,
    X_bad,
    ref_point,
    normalizer,
    normalization='euclidean',
    distance='euclidean',
):

    bad_sample = X_bad.values

    # Normalize the data (good and bad)
    X_good_normalized = normalizer.transform(X_good, method=normalization, tqdm="Good percentile")
    bad_sample_normalized = normalizer.transform(bad_sample, method=normalization, tqdm="Bad percentile")
    # Normalize also the reference point
    ref_point_normalized = normalizer.transform(np.array([ref_point]), method=normalization)[0]

    bad_vs_good_dist = np.array(
        batch_process(
            dataset=bad_sample_normalized,
            f=lambda X: pairwise_distance(
                X=X,
                Y=X_good_normalized,
                aggregate=np.min,
                distance=distance,
            ),
            batch_size=10,
            use_tqdm='Bad vs. Good',
            n_jobs=1,
        )
    ).flatten()

    bad_ref_dist = np.array(
        pairwise_distance(
            Y=bad_sample_normalized,
            X=[ref_point_normalized],
            aggregate=None,
            distance=distance,
        )
    ).flatten()

    return bad_sample, bad_sample_normalized, X_good_normalized, bad_vs_good_dist, bad_ref_dist


# ██████╗ ██╗      ██████╗ ████████╗
# ██╔══██╗██║     ██╔═══██╗╚══██╔══╝
# ██████╔╝██║     ██║   ██║   ██║
# ██╔═══╝ ██║     ██║   ██║   ██║
# ██║     ███████╗╚██████╔╝   ██║
# ╚═╝     ╚══════╝ ╚═════╝    ╚═╝
#


def plot_set_distance_distribution(indexes_and_titles, bad_vs_good_dist, bad_ref_dist):
    columns = ['Decision Boundary Distance', 'Reference Point Distance']
    kwargs = dict(
        x=columns[0],
        y=columns[1],
        # height=300,
        nbinsx=50,
        nbinsy=50,
        marginal_x="histogram",
        marginal_y="histogram",
    )

    for indexes, title in indexes_and_titles:
        a = bad_vs_good_dist if indexes is None else bad_vs_good_dist[indexes]
        b = bad_ref_dist if indexes is None else bad_ref_dist[indexes]

        # Heatmap
        fig = px.density_heatmap(
            pd.DataFrame(
                [a, b],
                index=columns,
            ).T,
            title=f"{title} (n= {len(a)})",
            **kwargs,
        )

        # Mean
        mean_val = a.mean()
        mean_val_rf = b.mean()
        mean_line_dict = dict(
            color='white',
            width=2,
            dash='dash',
        )
        fig.add_shape(
            go.layout.Shape(
                type='line',
                xref='x',
                yref='paper',
                x0=mean_val,
                y0=0,
                x1=mean_val,
                y1=1,
                line=mean_line_dict,
            ),
        )
        fig.add_shape(
            go.layout.Shape(
                type='line',
                xref='paper',
                x0=0,
                y0=mean_val_rf,
                x1=1,
                y1=mean_val_rf,
                line=mean_line_dict,
            ),
        )
        fig.add_annotation(
            x=1.1,  # arrows' head
            y=1.1,  # arrows' head
            text=f'Avg Dist RF = {mean_val_rf:.2f}',
            yref='paper',
            xref='paper',
            axref='x',
            showarrow=False,
        )
        fig.add_annotation(
            x=1.1,  # arrows' head
            y=1.05,  # arrows' head
            text=f'Avg Dist DB = {mean_val:.2f}',
            yref='paper',
            xref='paper',
            axref='x',
            showarrow=False,
        )
        fig.show()


def plot_allsets_distance_distribution(
    bad_vs_good_dist,
    bad_ref_dist,
    points_close_to_ref_index,
    points_far_from_rf_index,
    points_close_to_db_index,
):
    plot_set_distance_distribution(
        [
            (None, 'ALL BAD customers'),
            (
                points_close_to_ref_index,
                'BAD customers CLOSE to the reference point',
            ),
            (
                points_far_from_rf_index,
                'BAD customers FAR from the reference point<br>BUT CLOSE to the DECISION BOUNDARY',
            ),
            (
                points_close_to_db_index,
                'Customers CLOSE to the DECISION BOUNDARY',
            ),
        ],
        bad_vs_good_dist=bad_vs_good_dist,
        bad_ref_dist=bad_ref_dist,
    )
