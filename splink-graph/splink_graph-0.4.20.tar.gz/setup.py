# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splink_graph', 'splink_graph.embedding']

package_data = \
{'': ['*']}

install_requires = \
['gensim<4.1.0',
 'graphframes==0.6.0',
 'networkx>=2.5.1,<2.6.0',
 'node2vec==0.4.3',
 'numpy==1.19.5']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['scipy==1.5.4'],
 ':python_version >= "3.7" and python_version < "4.0"': ['scipy==1.6.0']}

setup_kwargs = {
    'name': 'splink-graph',
    'version': '0.4.20',
    'description': 'a small set of graph functions to be used from pySpark on top of networkx and graphframes',
    'long_description': '\n![](https://img.shields.io/badge/spark-%3E%3D2.4.x-orange) ![](https://img.shields.io/github/languages/top/moj-analytical-services/splink_graph) ![](https://img.shields.io/pypi/v/splink_graph) ![PyVersions](https://img.shields.io/pypi/pyversions/splink_graph) ![Downloads](https://pepy.tech/badge/splink-graph) \n\n# splink_graph: Graph metrics for data linkage at scale\n\n\n\n![](https://github.com/moj-analytical-services/splink_graph/raw/master/notebooks/splink_graph300x297.png)\n\n---\n\n\n`splink_graph` is a graph utility library for use in Apache Spark.\n\nIt computes graph metrics on the outputs of data linking which are useful for:\n- Quality assurance of linkage results and identifying false positive links\n- Computing quality metrics associated with groups (clusters) of linked records\n- Automatically identifying possible false positive links in clusters\n\n\nIt works with graph data structures such as the ones created from the outputs of data linking -  for instance the candidate pair results produced by ![splink](https://github.com/moj-analytical-services/splink)\n\nCalculations are performed per cluster/connected component/subgraph in a parallel manner thanks to the underlying help from `pyArrow`.\n\n---\n## TL&DR :\n\nGraph Database OLAP solutions are a few and far between.\nIf you have spark data in a format that can be represented as a network/graph then with this package:\n\n- Graph-theoretic metrics can be obtained efficiently using an already existing spark infrastucture without the need for a graph OLAP solution\n- The results can be used as is for finding the needle (of interesting subgraphs) in the haystack (whole set of subgraphs)\n- Or one can augment the available graph-compatible data as part of preprocessing step before the data-ingestion phase in an OLTP graph database (such as AWS Neptune etc)\n- Another use is to provide support for feature engineering from the subgraphs/clusters for supervised and unsupervised ML downstream uses.\n\n## How to Install :\nFor dependencies and other important technical info so you can run these functions without an issue please consult\n`INSTALL.md` on this repo\n\n## Functionality offered :\n\nFor a primer on the terminology used please look at `TERMINOLOGY.md` file in this repo\n\n\n####  Cluster metrics\n\nCluster metrics usually have as an input a spark edgelist dataframe that also includes the component_id (cluster_id) where the edge is in.\nThe output is a row of one or more metrics per cluster\n\n\nCluster metrics currently offered:\n\n- diameter (largest shortest distance between nodes in a cluster)\n- transitivity (or Global Clustering Coefficient in the related literature)\n- cluster triangle clustering coeff (or Local Clustering Coefficient in the related literature)\n- cluster square clustering coeff (useful for bipartite networks)\n- cluster node connectivity\n- cluster edge connectivity\n- cluster efficiency\n- cluster modularity\n- cluster assortativity\n- cluster avg edge betweenness\n- cluster weisfeiler lehman graphhash (in order to quickly test for graph isomorphisms)\n\nCluster metrics are really helpful at finding the needles (of for example clusters with possible linking errors) in the\nhaystack (whole set of clusters after the data linking process).\n\n---\n\n####  Node metrics\n\nNode metrics  have as an input a spark edgelist dataframe that also includes the component_id (cluster_id) where the edge belongs.\nThe output is a row of one or more metrics per node\n\nNode metrics curretnly offered:\n\n- Eigenvector Centrality\n- Harmonic centrality\n\n---\n\n####  Edge metrics\n\nEdge metrics  have as an input a spark edgelist dataframe that also includes the component_id (cluster_id) where the edge belongs.\nThe output is a row of one or more metrics per edge\n\nEdge metrics curretnly offered:\n\n- Edge Betweeness\n- Bridge Edges\n\n\n---\n## Functionality coming soon\n\n- [x] release for MVP to be used on AWS glue and demos\n- [x] cluster modularity based on partitions created by edge-betweenness\n- [x] cluster number of bridges metric added\n- [x] cluster assortativity added\n- [x] cluster modularity based on partitions created by label propagation\n- [ ] shallow embeddings of subgraphs/clusters (WIP)\n- [x] Add a connected components function (from the graphframes library)\n- [x] Add a connected components function for smaller graphs (from the networkx library) so its easier to get started.\n\n\nFor upcoming functionality further down the line please consult the `TODO.md` file\n\n\n## Contributing\n\nFeel free to contribute by\n\n * Starting an issue.\n\n * Forking the repository to suggest a change, and/or\n\n * Want a new metric implemented? Open an issue and ask. Probably it can be.\n',
    'author': 'Theodore Manassis',
    'author_email': 'theodore.manassis@digital.justice.gov.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/moj-analytical-services/splink_graph',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
