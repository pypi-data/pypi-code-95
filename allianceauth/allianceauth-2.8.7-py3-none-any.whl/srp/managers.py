import logging

import requests

from django.contrib.auth.models import User

from allianceauth import NAME
from allianceauth.eveonline.providers import provider

from .models import SrpUserRequest

logger = logging.getLogger(__name__)


class SRPManager:
    
    @staticmethod
    def get_kill_id(killboard_link):
        num_set = '0123456789'
        kill_id = ''.join([c for c in killboard_link if c in num_set])
        return kill_id

    @staticmethod
    def get_kill_data(kill_id):
        url = ("https://zkillboard.com/api/killID/%s/" % kill_id)
        headers = {
            'User-Agent': NAME,
            'Content-Type': 'application/json',
        }
        r = requests.get(url, headers=headers)
        result = r.json()[0]
        if result:
            killmail_id = result['killmail_id']
            killmail_hash = result['zkb']['hash']
            c = provider.client
            km = c.Killmails.get_killmails_killmail_id_killmail_hash(
                killmail_id=killmail_id,
                killmail_hash=killmail_hash
            ).result()
        else:
            raise ValueError("Invalid Kill ID")
        if km:
            ship_type = km['victim']['ship_type_id']
            logger.debug(
                "Ship type for kill ID %s is %s" % (kill_id, ship_type)
            )
            ship_value = result['zkb']['totalValue']
            logger.debug(
                "Total loss value for kill id %s is %s" % (kill_id, ship_value)
            )
            victim_id = km['victim']['character_id']
            return ship_type, ship_value, victim_id
        else:
            raise ValueError("Invalid Kill ID or Hash.")

    @staticmethod
    def pending_requests_count_for_user(user: User):
        """returns the number of open SRP requests for given user 
        or None if user has no permission"""
        if user.has_perm("auth.srp_management"):
            return SrpUserRequest.objects.filter(srp_status="pending").count()
        else:
            return None
