import shutil

# gsts --aws-role-arn arn:aws:iam::99999999999:role/xacct/developer --aws-profile=default --sp-id 99999999 --idp-id 999999999 --username foo@example.com


def __virtual__(hub):
    # npm install --global gsts
    path = shutil.which("gsts")
    return bool(path), path


async def gather(hub):
    """
    Get profile information from node gsts

    Example:
    .. code-block:: yaml

        aws.gsts:
          default:
            kwarg: thing
    """
    sub_profiles = {}
    for profile, ctx in hub.acct.PROFILES.get("aws.gsts", {}).items():
        hub.log.debug("GSTS authentication is not yet implemented")

    return sub_profiles
