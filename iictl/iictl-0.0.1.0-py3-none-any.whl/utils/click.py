def global_option(ctx, param, value):
    if value is None:
        return ctx.obj[param.name] if param.name in ctx.obj else 'default'
    else:
        ctx.obj[param.name] = value
        return value
