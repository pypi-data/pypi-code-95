from typing import Any
from typing import Dict


async def run(
    hub, desc_root: str, acct_file: str, acct_key: str, acct_profile: str = "default"
) -> Dict[str, Dict[str, Any]]:
    """
    :param hub:
    :param desc_root:
    :param acct_file:
    :param acct_key:
    :param acct_profile:
    :return:
    """
    ctx = await hub.idem.ex.ctx(
        path=desc_root,
        acct_file=acct_file,
        acct_key=acct_key,
        acct_profile=acct_profile,
    )
    return await hub.idem.describe.recurse(ctx, hub[desc_root])


async def recurse(hub, ctx, mod, ret: Dict[str, Dict[str, Any]] = None):
    if ret is None:
        ret = {}
    if hasattr(mod, "_subs"):
        for sub in mod._subs:
            ret = await hub.idem.describe.recurse(ctx, mod[sub], ret)
    if hasattr(mod, "_loaded"):
        for sub in mod._loaded:
            ret = await hub.idem.describe.recurse(ctx, mod[sub], ret)
    elif hasattr(mod, "describe"):
        result = mod.describe(ctx)
        result = await hub.pop.loop.unwrap(result)
        ret.update(result)
    return ret
