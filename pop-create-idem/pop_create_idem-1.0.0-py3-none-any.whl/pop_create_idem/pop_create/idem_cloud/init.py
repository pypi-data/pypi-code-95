import pathlib


def __init__(hub):
    hub.pop.sub.add(dyne_name="cloudspec")


def context(hub, ctx, directory: pathlib.Path):
    # If an acct plugin was passed in then we don't need to create auth plugins
    if ctx.get("simple_service_name"):
        ctx.service_name = ctx.simple_service_name
    elif not ctx.get("service_name"):
        ctx.service_name = (
            ctx.clean_name.replace("idem", "").replace("cloud", "").strip("_")
        )

    ctx.has_acct_plugin = bool(ctx.acct_plugin)
    if not ctx.has_acct_plugin:
        # Create auth plugins
        ctx.acct_plugin = ctx.service_name

    return ctx
