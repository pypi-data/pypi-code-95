from functools import partial

from microcosm.api import defaults
from microcosm.object_graph import ObjectGraph

from microcosm_sagemaker.artifact import RootInputArtifact, RootOutputArtifact
from microcosm_sagemaker.bundle import Bundle
from microcosm_sagemaker.dependency_traverser import traverse_component_and_dependencies
from microcosm_sagemaker.input_data import InputData


@defaults(
    bundle_orchestrator="single_threaded_bundle_orchestrator",
)
class BundleAndDependenciesLoader:
    def __init__(self, graph: ObjectGraph):
        self.bundle_orchestrator = getattr(
            graph,
            graph.config.bundle_and_dependencies_loader.bundle_orchestrator,
        )
        self.graph = graph

    def __call__(
        self,
        bundle: Bundle,
        root_input_artifact: RootInputArtifact,
        dependencies_only: bool = False,
    ):
        def load(bundle):
            name = _get_component_name(self.graph, bundle)
            bundle.load(root_input_artifact / name)

        self.bundle_orchestrator(
            bundle=bundle,
            bundle_handler=load,
            dependencies_only=dependencies_only,
        )


def fit_and_save_bundle(
    graph: ObjectGraph,
    input_data: InputData,
    root_output_artifact: RootOutputArtifact,
    bundle: Bundle,
) -> None:
    bundle_name = _get_component_name(graph, bundle)

    nested_output_artifact = root_output_artifact / bundle_name
    nested_output_artifact.init()

    # We call the training_initializers.init() before any bundle.fit()
    # That makes each bundle's training reproducible, regardless of its order in the training queue.
    graph.training_initializers.init()

    bundle.fit(input_data)
    bundle.save(nested_output_artifact)


@defaults(
    bundle_orchestrator="single_threaded_bundle_orchestrator",
)
class BundleAndDependenciesTrainer:
    def __init__(self, graph: ObjectGraph):
        self.bundle_orchestrator = getattr(
            graph,
            graph.config.bundle_and_dependencies_trainer.bundle_orchestrator,
        )
        self.graph = graph

    def __call__(
        self,
        bundle: Bundle,
        input_data: InputData,
        root_output_artifact: RootOutputArtifact,
        dependencies_only: bool = False,
    ):
        train = partial(
            fit_and_save_bundle,
            self.graph,
            input_data,
            root_output_artifact,
        )

        self.bundle_orchestrator(
            bundle=bundle,
            bundle_handler=train,
            dependencies_only=dependencies_only,
        )


class BundleAndDependenciesConfigExtractor:
    def __init__(self, graph):
        self.config = graph.config
        self.graph = graph

    def __call__(self, bundle: Bundle):
        """
        Returns the config from the `bundle`, as well as all of its dependents.

        """
        config = {}

        for bundle_to_handle in traverse_component_and_dependencies(bundle):
            bundle_name = _get_component_name(self.graph, bundle_to_handle)
            bundle_config = getattr(self.config, bundle_name, {})
            config.update(
                {bundle_name: bundle_config}
            )

        return config


def _get_component_name(graph, component):
    return next(
        key
        for key, possible_component in graph.items()
        if possible_component == component
    )
