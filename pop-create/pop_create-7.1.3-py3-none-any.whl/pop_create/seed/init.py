def context(hub, ctx, directory: str):
    if ctx.vertical:
        entrypoint = ""
    else:
        entrypoint = f"{ctx.project_name} = {ctx.clean_name}.scripts:start"

    return dict(
        dyne_dict={f"{d}": [f"{d}"] for d in ctx.dyne_list},
        entrypoint=entrypoint,
        **ctx,
    )
