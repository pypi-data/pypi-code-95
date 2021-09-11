import logging
import os
import pickle
import html

logger = logging.getLogger(__name__)


class MailmanUnpickler(pickle.Unpickler):

    class Noop:
        class _BounceInfo:
            pass

    def find_class(self, module, name):
        logger.debug(f'{module} {name}')
        if name == '_Bouncer._BounceInfo':
            return MailmanUnpickler.Noop
        if name == '_BounceInfo':
            return MailmanUnpickler.Noop
        if name == '_Bouncer':
            return MailmanUnpickler.Noop
        return super().find_class(module, name)


class ErrorMailmanNotFound(Exception):
    pass


class Mailman(object):

    MODERATION_HOLD = 0
    MODERATION_REJECT = 1
    MODERATION_DISCARD = 2

    ROSTER_PUBLIC = 0
    ROSTER_MEMBERS = 1
    ROSTER_ADMINS = 2

    SUBSCRIBE_POLICY_OPEN = 0
    SUBSCRIBE_POLICY_CONFIRM = 1
    SUBSCRIBE_POLICY_MODERATE = 2
    SUBSCRIBE_POLICY_CONFIRM_THEN_MODERATE = 3

    def __init__(self, args):
        self.args = args

    @staticmethod
    def moderation_action_mapping(value):
        # Convert the member_moderation_action option to an Action enum.
        # The values were: 0==Hold, 1==Reject, 2==Discard
        return {
            Mailman.MODERATION_HOLD: 'approval',
            Mailman.MODERATION_REJECT: 'ignore',
            Mailman.MODERATION_DISCARD: 'ignore',
            }[value]

    def load_pickle(self):
        p = self.args.mailman_config
        if not os.path.exists(p):
            raise ErrorMailmanNotFound(f'{p} not found, skipping')
        return MailmanUnpickler(open(p, 'rb'), encoding=self.args.mailman_encoding).load()

    def load(self):
        self.name = self.args.list
        c = self.load_pickle()

        logger.debug(f'config.pck is {c}')

        self.info = {
            'private_roster': c['private_roster'],
            'description': c['description'],
            'subscribe_policy': c['subscribe_policy'],
        }
        if c.get('archive'):
            if c.get('archive_private'):
                self.info['archive'] = 'private'
            else:
                self.info['archive'] = 'public'
        else:
            self.info['archive'] = 'private'
        if bool(c.get('default_member_moderation', 0)):
            self.info['moderation'] = self.moderation_action_mapping(
                c['member_moderation_action'])
        else:
            self.info['moderation'] = 'no'
        self.user = {}
        for email in c['members']:
            self.user[email] = {'email': email}
        for k in ('moderator', 'owner'):
            for email in c[k]:
                self.user.setdefault(email, {'email': email})[k] = True
        for email in c['digest_members']:
            if email not in self.user:
                logger.error(f'SKIP digest_members for unknown user {email}')
                continue
            self.user[email]['digest'] = True
        for k in ('language', 'delivery_status', 'user_options'):
            for email, value in c[k].items():
                if email not in self.user:
                    logger.error(f'SKIP {k} for unknown user {email}')
                    continue
                self.user[email][k] = value
        for email, usernames in c['usernames'].items():
            if email not in self.user:
                logger.error(f'SKIP usernames for unknown user {email}')
                continue
            if not isinstance(usernames, str):
                logger.error(f'CONVERT usernames {usernames} for user {email} to an empty string')
                usernames = ''
            self.user[email]['usernames'] = html.unescape(usernames)
        if c.get('ban_list'):
            self.info['ban_list'] = c['ban_list']
            for email in c['ban_list']:
                if email in self.user:
                    del self.user[email]
        return True
