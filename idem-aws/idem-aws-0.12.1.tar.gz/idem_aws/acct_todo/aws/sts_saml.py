from typing import Any
from typing import Dict

import dict_tools.data

__virtualname__ = "saml"


async def gather(hub) -> Dict[str, Any]:
    """
    Get profile names from encrypted AWS credential files.
    Standardize the profile keys to what a boto3 Client requires.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sts.html#STS.Client.assume_role_with_saml

    Example:
    .. code-block:: yaml

        aws.saml:
          profile_name:
            region: us-east-1
            role_arn: string
            principal_arn: string
            policy_arns:
              - arn: string1
              - arn: string2
            policy: string
            duration: 180
    """
    sub_profiles = {}
    for profile, ctx in hub.acct.PROFILES.get("aws.saml", {}).items():
        hub.tool.boto3.session.get()
        temp_ctx = dict_tools.data.NamespaceDict(
            acct={"region_name": ctx.get("region")}
        )
        saml_xml = "TODO"
        ret = await hub.tool.boto3.client.exec(
            temp_ctx,
            "sts",
            "assume_role_with_saml",
            RoleArn="arn:aws:sts::883373499178:assumed-role/developer/tyjohnson@vmware.com",
            PrincipalArn="arn:aws:sts::883373499178:assumed-role/developer/tyjohnson@vmware.com",
            SAMLAssertion=saml_xml,
        )
        sub_profiles[profile] = {
            "aws_access_key_id": ret["Credentials"]["AccessKeyId"],
            "aws_secret_access_key": ret["Credentials"]["SecretAccessKey"],
            "aws_session_token": ret["Credentials"]["SessionToken"],
            **ctx,
        }
    print(sub_profiles)
    return sub_profiles
