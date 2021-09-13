import pathlib

try:
    import google.protobuf.compiler.plugin_pb2 as protobuf

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


def context(hub, ctx, directory: pathlib.Path):
    ctx = hub.pop_create.idem_cloud.init.context(ctx, directory)

    protobuf = hub.OPT.pop_create.specification

    # Convert protobuf to openapi3
    ctx.specification = {"TODO": ""}

    # get ctx from openapi3 with changes that turn swagger into openapi3
    hub.pop_create.init.run(directory=directory, subparsers=["openapi3"], **ctx)

    return ctx
