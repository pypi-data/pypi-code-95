#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm-sagemaker"
version = "0.9.1"

setup(
    name=project,
    version=version,
    description="Opinionated machine learning organization and configuration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-sagemaker",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
    keywords="microcosm",
    install_requires=[
        "boto3>=1.9.90",
        "awscli>=1.16.200",
        "click>=7.0",
        "microcosm>=2.12.0",
        "microcosm-flask[metrics]>=2.8.0",
        # See: https://github.com/boto/botocore/pull/1910
        "python-dateutil<3.0.0",
        "joblib>=0.15",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "console_scripts": [
            "train = microcosm_sagemaker.commands.train:main",
            "evaluate = microcosm_sagemaker.commands.evaluate:main",
            "runserver = microcosm_sagemaker.commands.runserver:main",
        ],
        "microcosm.factories": [
            "active_bundle = microcosm_sagemaker.factories:configure_active_bundle",
            "active_evaluation = microcosm_sagemaker.factories:configure_active_evaluation",
            (
                "bundle_and_dependencies_loader = "
                "microcosm_sagemaker.bundle_traversal:BundleAndDependenciesLoader"
            ),
            (
                "bundle_and_dependencies_trainer = "
                "microcosm_sagemaker.bundle_traversal:BundleAndDependenciesTrainer"
            ),
            (
                "bundle_and_dependencies_config_extractor = "
                "microcosm_sagemaker.bundle_traversal:BundleAndDependenciesConfigExtractor"
            ),
            (
                "load_active_bundle_and_dependencies = "
                "microcosm_sagemaker.factories:load_active_bundle_and_dependencies"
            ),
            "random = microcosm_sagemaker.random:Random",
            "sagemaker = microcosm_sagemaker.factories:configure_sagemaker",
            (
                "single_threaded_bundle_orchestrator = "
                "microcosm_sagemaker.bundle_orchestrator:SingleThreadedBundleOrchestrator"
            ),
            "training_initializers = microcosm_sagemaker.training_initializer_registry:TrainingInitializerRegistry",
            "experiment_metrics = microcosm_sagemaker.metrics.experiment_metrics:ExperimentMetrics",
            "wandb = microcosm_sagemaker.metrics.wandb.store:WeightsAndBiases",
        ],
        'pytest11': ['pytest_sagemaker = microcosm_sagemaker.tests.pytest_sagemaker'],
    },
    extras_require={
        "torch": [
            "torch>=1.1.0",
        ],
        "tensorflow": [
            "tensorflow>=1.14.0",
        ],
        "test": [
            "PyHamcrest>=1.9.0",
            "coverage>=4.0.3",
            "parameterized>=0.7.0",
            "torch>=1.1.0",
            "wandb>=0.10",
        ],
        "profiling": "pyinstrument>=3.0",
        "wandb": "wandb>=0.10",
    },
)
