import logging
from django.dispatch import receiver
from allianceauth.authentication.signals import state_changed


logger = logging.getLogger(__name__)


@receiver(state_changed)
def check_groups_on_state_change(sender, user, state, **kwargs):
    logger.debug(
        "Checking group memberships for %s based on new state %s" % (user, state)
    )        
    state_groups = (
        user.groups.select_related("authgroup").exclude(authgroup__states=None)
    )
    for group in state_groups:
        if not group.authgroup.states.filter(id=state.id).exists():
            logger.info(
                "Removing user %s from group %s due to missing state" % (user, group)
            )        
            user.groups.remove(group)
