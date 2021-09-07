import plotly.express as px
import pandas as pd
import numpy as np

from sklearn.manifold import TSNE
from sklearn.manifold import LocallyLinearEmbedding
from sklearn.decomposition import PCA
from sklearn.random_projection import johnson_lindenstrauss_min_dim, GaussianRandomProjection


def dim_reduce(
    points,
    technique='tsne',
    random_state=2021,
    n_components=2,
):
    if technique == 'tsne':
        tsne = TSNE(
            n_components=n_components,
            perplexity=30.0,
            early_exaggeration=12.0,
            learning_rate=200.0,
            n_iter=1000,
            n_iter_without_progress=300,
            min_grad_norm=1e-07,
            metric='euclidean',
            init='random',
            verbose=100,
            random_state=random_state,
            method='barnes_hut',
            angle=0.5,
            n_jobs=None,
        )
        transformed_points = tsne.fit_transform(points)
    elif technique == 'jlt':
        print(
            'Minimum JL components (eps = .99): ',
            johnson_lindenstrauss_min_dim(len(points), eps=1 - np.finfo(float).eps)
        )
        grp = GaussianRandomProjection(n_components=n_components, eps=.99)
        transformed_points = grp.fit_transform(points)
    elif technique == 'pca':
        pca = PCA(
            n_components=n_components,
            copy=True,
            whiten=False,
            svd_solver='auto',
            tol=0.0,
            iterated_power='auto',
            random_state=random_state,
        )
        transformed_points = pca.fit_transform(points)

    elif technique == 'lle':
        lle = LocallyLinearEmbedding(
            n_components=n_components,
            random_state=random_state,
        )
        return lle.fit_transform(points)

    else:
        raise ValueError('Invalid technique.')

    return transformed_points


def plot_points_in_clusters(
    points,
    clusters=None,
    axis_names='x',
    clusters_name='group',
    title='Points in clusters',
):
    # Get number of components and names
    n_components = len(points[0])
    assert n_components == 2 or n_components == 3

    if isinstance(axis_names, str):
        axis_names = [axis_names + f'_{i}' for i in range(n_components)]

    df = pd.DataFrame(points, columns=axis_names)
    kwargs = dict(
        x=axis_names[0],
        y=axis_names[1],
        title=title,
    )
    if clusters is not None:
        df[clusters_name] = clusters
        kwargs['color'] = clusters_name

    if n_components > 2:
        kwargs['z'] = axis_names[2]

    if n_components == 2:
        px.scatter(df.sample(frac=1), **kwargs).show()
    else:
        px.scatter_3d(df.sample(frac=1), **kwargs).show()
