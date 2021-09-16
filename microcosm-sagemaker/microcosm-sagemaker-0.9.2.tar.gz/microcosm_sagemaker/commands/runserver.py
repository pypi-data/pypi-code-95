"""
Main web service CLI

"""
from click import command, option
from microcosm.loaders import load_from_dict
from microcosm.object_graph import ObjectGraph

from microcosm_sagemaker.app_hooks import create_serve_app
from microcosm_sagemaker.commands.options import input_artifact_option
from microcosm_sagemaker.profiling import enable_profiling


@command()
@option(
    "--host",
    default="127.0.0.1",
)
@option(
    "--port",
    type=int,
)
@option(
    "--debug/--no-debug",
    default=False,
)
@option(
    "--profile/--no-profile",
    default=False,
)
@input_artifact_option()
def main(host, port, debug, profile, input_artifact):
    graph = create_serve_app(
        debug=debug,
        extra_loader=load_from_dict(
            root_input_artifact_path=input_artifact.path,
        ),
    )

    if profile:
        enable_profiling(graph)

    run_serve(
        graph=graph,
        host=host,
        port=port,
    )


def run_serve(
    graph: ObjectGraph,
    host: str,
    port: int,
) -> None:
    graph.flask.run(
        host=host,
        port=port or graph.config.flask.port,
    )
