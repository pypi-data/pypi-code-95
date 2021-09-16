def context(hub, ctx, directory: str):
    ctx.version_number = "0.1.0"

    ctx.welcome = f"Welcome to {ctx.project_name}'s Documentation!"
    ctx.welcome = f"{ctx.welcome}\n{'=' * len(ctx.welcome)}\n"

    return ctx
