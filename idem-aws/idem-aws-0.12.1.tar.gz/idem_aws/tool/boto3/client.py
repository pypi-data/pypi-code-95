import re
from typing import Any
from typing import Dict
from typing import Generator

import boto3.session

ITERATION_FINISHED = object()

__func_alias__ = {"exec_": "exec"}


async def exec_(
    hub,
    ctx,
    service_name: str,
    operation: str,
    jmes_search_path: str = None,
    *op_args,
    **op_kwargs: Dict[str, Any],
) -> Any:
    """
    :param hub:
    :param ctx:
    :param service_name: The name of the service client to create
    :param operation: The operation to run from the service client
    :param jmes_search_path: The JMES path to use as a filter for paginated results
    :param op_args: arguments to pass to the operation call
    :param op_kwargs: keyword arguments to pass to the operation call

    :return: The result of the operation call
    """
    session: boto3.session.Session = hub.tool.boto3.session.get()
    client = session.client(service_name=service_name, **ctx.acct)

    # Don't pass kwargs that have a "None" value to the function call
    kwargs = {k: v for k, v in op_kwargs.items() if v is not None}

    can_paginate = client.can_paginate(operation)

    if can_paginate:
        hub.log.debug(f"Paginating results for {service_name}.{operation}")
        paginator = client.get_paginator(operation)
        pages = paginator.paginate(*op_args, **kwargs)
        if jmes_search_path is None:
            return await hub.pop.loop.wrap(pages.build_full_result)
        else:
            iterator = await hub.pop.loop.wrap(pages.search, jmes_search_path)
            return [_ for _ in iterator]
    else:
        hub.log.debug(f"Getting raw results for {service_name}.{operation}")
        op = getattr(client, operation)
        return await hub.pop.loop.wrap(op, *op_args, **kwargs)


async def wait(
    hub, ctx, service_name: str, waiter_name: str, *wt_args, **wt_kwargs
) -> None:
    """
    Asynchronously wait for the named resource to be avilable

    :param hub:
    :param ctx:
    :param service_name: The name of the service client to retrieve
    :param waiter_name: The name of the waiter to get from the service client
    :param wt_args: Args to pass to the wait function
    :param wt_kwargs: kwargs to pass to the wait function
    """
    session: boto3.session.Session = hub.tool.boto3.session.get()
    client = session.client(service_name=service_name, **ctx.acct)

    if waiter_name not in client.waiter_names:
        raise NameError(
            f"No waiter '{waiter_name}'. "
            f"Available waiters for '{service_name}' are: {' '.join(client.waiter_names)}"
        )

    waiter = client.get_waiter(waiter_name)

    await hub.pop.loop.wrap(waiter.wait, *wt_args, **wt_kwargs)


async def search(
    hub, ctx, service_name: str, collection: str, jmes_path: str = "*[]"
) -> str:
    """
    :param hub:
    :param ctx:
    :param service_name:
    :param collection:
    :param jmes_path:
    :return:
    """
    session: boto3.session.Session = hub.tool.boto3.session.get()
    client = session.client(service_name=service_name, **ctx.acct)

    # Find a paginator that can describe this collection
    for operation in client.meta.method_to_api_mapping:
        if client.can_paginate(operation) and re.match(
            f"[a-z]+_{collection}s?$", operation
        ):
            break
    else:
        raise AttributeError(
            f"Could not find a paginator for {service_name}.{collection}"
        )

    paginator = client.get_paginator(operation)
    pages = paginator.paginate()
    iterator: Generator = await hub.pop.loop.wrap(pages.search, jmes_path)
    ret = next(iterator, None)
    iterator.close()
    return ret
