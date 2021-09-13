import shutil

# aws sts assume-role --role-arn arn:aws:iam::9999999:role --role-session-name "session name"
"""
#!/bin/bash
# Name: ~/.aws/assume.sh
# Usage: . ~/.aws/assume.sh arn:aws:iam::883373499178:role/xacct/developer
echo
echo " HISTCONTROL=ignoreboth"
echo " export AWS_DEFAULT_REGION=us-west-2"
round=1
for i in $(aws sts assume-role --role-session-name "${GOOGLE_USERNAME}" --role-arn "${1}"|jq -r '.Credentials|.AccessKeyId,.SecretAccessKey,.SessionToken,.Expiration')
do
    case $round in
        1)
        echo " export AWS_ACCESS_KEY_ID=$i"
        export AWS_ACCESS_KEY_ID="$i"
        round=$(( $round+1))
        ;;
        2)
        echo " export AWS_SECRET_ACCESS_KEY=$i"
        export AWS_SECRET_ACCESS_KEY="$i"
        round=$(( $round+1))
        ;;
        3)
        echo " export AWS_SESSION_TOKEN=$i"
        export AWS_SESSION_TOKEN="$i"
        round=$(( $round+1))
        ;;
        4)
        echo " export AWS_SESSION_EXPIRATION=$i"
        export AWS_SESSION_EXPIRATION="$i"
        ;;
    esac
done
unset AWS_PROFILE
echo
env|grep ^AWS
echo
aws sts get-caller-identity
OLDPS1="$PS1"
PS1="(`aws iam list-account-aliases|jq -r '.AccountAliases[0]'`) $PS1"
"""


def __virtual__(hub):
    path = shutil.which("aws")
    return bool(path), path


async def gather(hub):
    """
    Get profile information from node `aws sts`

    Example:
    .. code-block:: yaml

        aws.sts:
          default:
            # aws sts [operation]
            operation: assume-role
            # All other kwargs will be have "--" prepended and will be added to the operation call
            # See `aws sts [operation] help` for available kwargs
            role-arn: arn:aws:iam::99999999:role
            role-session-name: session_name
    """
    sub_profiles = {}
    for profile, ctx in hub.acct.PROFILES.get("aws.sts", {}).items():
        cmd = ["aws", "sts", ctx.pop("operation")] + [
            f"--{key} {value}" for key, value in ctx.items()
        ]
        # TODO run command and figure load all the profiles it defined
        hub.log.debug("aws sts authentication is not yet implemented")

    return sub_profiles
