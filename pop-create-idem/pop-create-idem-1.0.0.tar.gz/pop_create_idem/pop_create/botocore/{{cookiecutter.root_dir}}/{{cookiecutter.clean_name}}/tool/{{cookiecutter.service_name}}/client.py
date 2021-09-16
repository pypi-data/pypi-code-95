from typing import Any, Dict

from botocore.paginate import Paginator

__func_alias__ = {"exec_", "exec"}


async def exec_(
    hub, ctx, service_name: str, operation: str, op_kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    with ctx.acct.session.create_client(
        service_name=service_name, **ctx.acct.client_kwargs
    ) as client:
        # Don't pass kwargs that have a "None" value to the function call
        kwargs = {k: v for k, v in op_kwargs.items() if v is not None}

        can_paginate = client.can_paginate(operation)
        if can_paginate:
            paginator: Paginator = client.get_paginator(operation)
            paginator.paginate()

        try:
            ret = (await hub.pop.loop.wrap(getattr(client, operation), **kwargs),)
            if can_paginate:
                ret = [ret]
                for page in paginator.paginate():
                    ret.append(page["Content"])
            return {
                "comment": "",
                "ret": ret,
                "status": True,
            }
        except Exception as e:
            return {
                "comment": f"{e.__class__}: {e}",
                "ret": None,
                "status": False,
            }
