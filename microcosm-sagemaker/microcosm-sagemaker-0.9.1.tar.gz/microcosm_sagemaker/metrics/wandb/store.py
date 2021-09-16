import os

from microcosm.api import binding, defaults
from microcosm_logging.decorators import logger

from microcosm_sagemaker.decorators import metrics_observer


try:
    import wandb
    from wandb.apis import CommError
except ImportError:
    pass


@metrics_observer()
@logger
@binding("weights_and_biases")
@defaults(
    enable=None,
)
class WeightsAndBiases:
    def __init__(self, graph):
        self.graph = graph
        self.enable = (
            # If it is not explicitly enabled or disabled, enable if not testing.
            graph.config.weights_and_biases.enable or not graph.metadata.testing
        )
        self.project_name = graph.metadata.name.replace("_", "-")
        self.bundle_and_dependencies_config_extractor = self.graph.bundle_and_dependencies_config_extractor
        self.active_bundle = getattr(graph, graph.config.active_bundle)
        self.run_path = getattr(graph.config.wandb, "run_path", None)
        self.wandb_run = None

    def init(self):
        # Sometimes, the entity in the wandb run path appears as None.
        # To make sure this does not happen, we explicityly set the wandb entity.
        # https://docs.wandb.com/library/environment-variables
        os.environ["WANDB_ENTITY"] = "globality"

        # Only initialize wandb if it is enabled
        if not self.enable:
            return

        # Only initialize/load wandb if it is not already created/loaded
        if self.wandb_run is not None:
            return

        # Pushing into an existing wandb experiment
        if self.run_path:

            try:
                self.wandb_run = wandb.Api().run(path=self.run_path)
                self.logger.info(f"The existing Weights & Biases run was loaded: {self.run_path}")

            except CommError:
                # If the previous run cannot be found:
                #   - Start a new run instead
                #   - Add a note to the new run that this run is related to a previous run
                self.logger.warning(f"Could not find run: {self.run_path}")
                self.wandb_run = self._create_new_wandb_run(
                    notes=f"Related to previous run: {self.run_path}",
                )

        # Creating a new wandb experiment
        else:
            self.wandb_run = self._create_new_wandb_run()

    def _create_new_wandb_run(self, notes=None):
        wandb_run = wandb.init(
            project=self.project_name,
            config=self.bundle_and_dependencies_config_extractor(self.active_bundle),
            notes=notes,
        )

        # Injecting the wandb run path into the config
        self.graph.config.wandb.run_path = wandb_run.path
        # Setting the run_path for the current instance.
        # This prevents a new wandb instantiation if the `init` method is called again.
        self.run_path = wandb_run.path

        # Adding the link to the Weights & Biases run to the landing page
        landing_convention_links = self.graph.config.landing_convention.get("links", {})
        landing_convention_links.update({"Weights & Biases": wandb_run.get_url()})
        self.graph.config.landing_convention.update({"links": landing_convention_links})

        self.logger.info(f"A new `weights & biases` run was created: {wandb_run.path}")

        return wandb_run

    def log_timeseries(self, **kwargs):
        step = kwargs.pop("step", None)
        self.wandb_run.log(kwargs, step=step)
        return None

    def log_static(self, **kwargs):
        self.wandb_run.summary.update(kwargs)
        return None
