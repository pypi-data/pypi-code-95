# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datasetinsights',
 'datasetinsights.commands',
 'datasetinsights.datasets',
 'datasetinsights.datasets.unity_perception',
 'datasetinsights.io',
 'datasetinsights.io.downloader',
 'datasetinsights.stats',
 'datasetinsights.stats.visualization']

package_data = \
{'': ['*'], 'datasetinsights.stats.visualization': ['font/*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'codetiming>=1.2.0,<2.0.0',
 'cython>=0.29.14,<0.30.0',
 'dash==1.12.0',
 'dask[complete]>=2.14.0,<3.0.0',
 'google-cloud-storage>=1.24.1,<2.0.0',
 'jupyter>=1.0.0,<2.0.0',
 'matplotlib>=3.3.1,<4.0.0',
 'numpy>=1.17,<2.0',
 'opencv-python>=4.4.0.42,<5.0.0.0',
 'pandas>=1.0.1,<2.0.0',
 'plotly>=4.4.1,<5.0.0',
 'pyquaternion>=0.9.5,<0.10.0',
 'tqdm>=4.45.0,<5.0.0']

entry_points = \
{'console_scripts': ['datasetinsights = datasetinsights.__main__:entrypoint']}

setup_kwargs = {
    'name': 'datasetinsights',
    'version': '1.1.1',
    'description': 'Synthetic dataset insights.',
    'long_description': '# Dataset Insights\n\n[![PyPI python](https://img.shields.io/pypi/pyversions/datasetinsights)](https://pypi.org/project/datasetinsights)\n[![PyPI version](https://badge.fury.io/py/datasetinsights.svg)](https://pypi.org/project/datasetinsights)\n[![Downloads](https://pepy.tech/badge/datasetinsights)](https://pepy.tech/project/datasetinsights)\n[![Tests](https://github.com/Unity-Technologies/datasetinsights/actions/workflows/linting-and-unittests.yaml/badge.svg?branch=master&event=push)](https://github.com/Unity-Technologies/datasetinsights/actions/workflows/linting-and-unittests.yaml?query=branch%3Amaster+event%3Apush)\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)\n\nUnity Dataset Insights is a python package for downloading, parsing and analyzing synthetic datasets generated using the Unity [Perception package](https://github.com/Unity-Technologies/com.unity.perception).\n\n## Installation\n\nDataset Insights maintains a pip package for easy installation. It can work in any standard Python environment using `pip install datasetinsights` command.\n\n## Getting Started\n\n### Dataset Statistics\n\nWe provide a sample [notebook](notebooks/Perception_Statistics.ipynb) to help you load synthetic datasets generated using [Perception package](https://github.com/Unity-Technologies/com.unity.perception) and visualize dataset statistics. We plan to support other sample Unity projects in the future.\n\n### Dataset Download\n\nYou can download the datasets from HTTP(s), GCS, and Unity simulation projects using the \'download\' command from CLI or API.\n\n[CLI](https://datasetinsights.readthedocs.io/en/latest/datasetinsights.commands.html#datasetinsights-commands-download)\n\n```bash\ndatasetinsights download \\\n  --source-uri=<xxx> \\\n  --output=$HOME/data\n```\n[Programmatically](https://datasetinsights.readthedocs.io/en/latest/datasetinsights.io.downloader.html#module-datasetinsights.io.downloader.gcs_downloader)\n\nUnitySimulationDownloader downloads a dataset from Unity Simulation.\n\n```python3\nfrom datasetinsights.io.downloader import UnitySimulationDownloader\n\nsource_uri=usim://<project_id>/<run_execution_id>\ndest = "~/data"\naccess_token = "XXX"\ndownloader = UnitySimulationDownloader(access_token=access_token)\ndownloader.download(source_uri=source_uri, output=dest)\n```\nGCSDatasetDownloader downloads a dataset from GCS location.\n```python3\nfrom datasetinsights.io.downloader import GCSDatasetDownloader\n\nsource_uri=gs://url/to/file.zip or gs://url/to/folder\ndest = "~/data"\ndownloader = GCSDatasetDownloader()\ndownloader.download(source_uri=source_uri, output=dest)\n```\nHTTPDatasetDownloader downloads a dataset from any HTTP(S) location.\n```python3\nfrom datasetinsights.io.downloader import HTTPDatasetDownloader\n\nsource_uri=http://url.to.file.zip\ndest = "~/data"\ndownloader = HTTPDatasetDownloader()\ndownloader.download(source_uri=source_uri, output=dest)\n```\n### Dataset Explore\nYou can explore the dataset [schema](https://datasetinsights.readthedocs.io/en/latest/Synthetic_Dataset_Schema.html#synthetic-dataset-schema) by using following API:\n\n[Unity Perception](https://datasetinsights.readthedocs.io/en/latest/datasetinsights.datasets.unity_perception.html#datasetinsights-datasets-unity-perception)\n\nAnnotationDefinitions and MetricDefinitions loads synthetic dataset definition tables and return a dictionary containing the definitions.\n\n```python3\nfrom datasetinsights.datasets.unity_perception import AnnotationDefinitions,\nMetricDefinitions\nannotation_def = AnnotationDefinitions(data_root=dest, version="my_schema_version")\ndefinition_dict = annotation_def.get_definition(def_id="my_definition_id")\n\nmetric_def = MetricDefinitions(data_root=dest, version="my_schema_version")\ndefinition_dict = metric_def.get_definition(def_id="my_definition_id")\n```\nCaptures loads synthetic dataset captures tables and return a pandas dataframe with captures and annotations columns.\n\n```python3\nfrom datasetinsights.datasets.unity_perception import Captures\ncaptures = Captures(data_root=dest, version="my_schema_version")\ncaptures_df = captures.filter(def_id="my_definition_id")\n```\nMetrics loads synthetic dataset metrics table which holds extra metadata that can be used to describe a particular sequence, capture or annotation and return a pandas dataframe with captures and metrics columns.\n\n```python3\nfrom datasetinsights.datasets.unity_perception import Metrics\nmetrics = Metrics(data_root=dest, version="my_schema_version")\nmetrics_df = metrics.filter_metrics(def_id="my_definition_id")\n```\n\n## Docker\n\nYou can use the pre-build docker image [unitytechnologies/datasetinsights](https://hub.docker.com/r/unitytechnologies/datasetinsights) to run similar commands.\n\n## Documentation\n\nYou can find the API documentation on [readthedocs](https://datasetinsights.readthedocs.io/en/latest/).\n\n## Contributing\n\nPlease let us know if you encounter a bug by filing an issue. To learn more about making a contribution to Dataset Insights, please see our Contribution [page](CONTRIBUTING.md).\n\n## License\n\nDataset Insights is licensed under the Apache License, Version 2.0. See [LICENSE](LICENCE) for the full license text.\n\n## Citation\nIf you find this package useful, consider citing it using:\n```\n@misc{datasetinsights2020,\n    title={Unity {D}ataset {I}nsights Package},\n    author={{Unity Technologies}},\n    howpublished={\\url{https://github.com/Unity-Technologies/datasetinsights}},\n    year={2020}\n}\n```\n',
    'author': 'Unity AI Perception Team',
    'author_email': 'computer-vision@unity3d.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Unity-Technologies/datasetinsights',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
