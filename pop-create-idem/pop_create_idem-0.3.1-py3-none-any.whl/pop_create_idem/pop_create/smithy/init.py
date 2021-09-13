import pathlib


def __virtual__(hub):
    return False, "Not implemented"


def context(hub, ctx, directory: pathlib.Path):
    ctx = hub.pop_create.idem_cloud.init.context(ctx, directory)

    # Convert smithy model to openapi3 with gradle
    gradle_build_dir = ctx.specification
    hub.tool.gradle.clean(gradle_build_dir)
    ctx.specification = hub.tool.gradle.build(gradle_build_dir)
    raise NameError("almost there")

    # get ctx from openapi3 with changes that turn smithy into openapi3
    hub.pop_create.init.run(directory=directory, subparsers=["openapi3"], **ctx)

    return ctx
